from abc import ABC
import logging
import os

import docker
from tqdm import tqdm

from blazetest.core.utils.command_executor import CommandExecutor
from blazetest.core.utils.exceptions import DepotTokenNotProvided, ImagePushError

logger = logging.getLogger(__name__)


class BuildTool(ABC):
    EXECUTABLE = None

    def __init__(
        self,
        project_context: str,
        docker_file_path: str,
        image_uri: str,
        build_platform: str,
        *args,
        **kwargs,
    ):
        self.project_context = project_context
        self.docker_file_path = docker_file_path
        self.image_uri = image_uri
        self.build_platform = build_platform

    def login(self, username: str, password: str, registry: str):
        raise NotImplementedError

    def build(self):
        raise NotImplementedError

    def push(self):
        raise NotImplementedError

    def build_and_push(self):
        raise NotImplementedError

    def execute(self, command: str, arguments: dict, allowed_return_codes=None) -> int:
        if allowed_return_codes is None:
            allowed_return_codes = [0]

        command_executor = CommandExecutor(
            executable=self.EXECUTABLE,
            command=command,
            arguments=arguments,
        )
        command_result = command_executor.execute_command(allowed_return_codes=allowed_return_codes)
        return command_result


class DepotBuildTool(BuildTool):
    """
    Uses depot.dev to build and push images to a remote repository.
    """

    EXECUTABLE = "depot"  # TODO: would executable work correctly?
    BUILD_COMMAND = "build"

    def __init__(
        self,
        project_context: str,
        docker_file_path: str,
        image_uri: str,
        build_platform: str,
        depot_token: str = None,
        depot_project_id: str = None,
    ):
        super().__init__(
            project_context=project_context,
            docker_file_path=docker_file_path,
            image_uri=image_uri,
            build_platform=build_platform,
        )
        self.depot_token = depot_token
        if self.depot_token is None:
            self.depot_token = os.getenv("DEPOT_TOKEN")
            if self.depot_token is None:
                raise DepotTokenNotProvided(
                    "Depot token not provided. "
                    "Please provide it using --depot-token CLI argument or DEPOT_TOKEN environment variable."
                )
        self.depot_project_id = depot_project_id

    def build_and_push(self):
        args = {
            "--tag": self.image_uri,
            "--file": self.docker_file_path,
            "--platform": self.build_platform,
            "--token": self.depot_token,
            "--push": None,
            "--provenance": "false",
            self.project_context: None,
        }

        if self.depot_project_id:
            args["--project"] = self.depot_project_id

        return self.execute(
            command=self.BUILD_COMMAND,
            arguments=args,
        )

    def login(self, username: str, password: str, registry: str = None):
        client = docker.from_env()
        client.login(username=username, password=password, registry=registry)


class DockerBuildTool(BuildTool):
    """
    This class will be used to build and push images from local Docker.
    """

    EXECUTABLE = "docker"
    BUILD_COMMAND = "build"
    PUSH_COMMAND = "push"
    LOGIN_COMMAND = "login"

    def __init__(
        self,
        project_context: str,
        docker_file_path: str,
        image_uri: str,
        build_platform: str,
    ):
        super().__init__(
            project_context=project_context,
            docker_file_path=docker_file_path,
            image_uri=image_uri,
            build_platform=build_platform,
        )
        self.client = docker.from_env()
        self._auth_info = None  # Store authentication info for reuse

    def login(self, username: str, password: str, registry: str):
        """
        Login to Docker registry using command line approach
        """
        # Store auth info for potential re-authentication
        self._auth_info = {"username": username, "password": password, "registry": registry}

        self._perform_login()

    def _perform_login(self):
        """
        Internal method to perform the actual login
        """
        if not self._auth_info:
            raise Exception("No authentication information available. Call login() first.")

        args = {"--username": self._auth_info["username"], "--password-stdin": None, self._auth_info["registry"]: None}

        command_executor = CommandExecutor(executable=self.EXECUTABLE, command=self.LOGIN_COMMAND, arguments=args)

        try:
            return_code = command_executor.execute_command(
                input_data=self._auth_info["password"], allowed_return_codes=[0]
            )

            if return_code != 0:
                raise Exception(f"Docker login failed with return code {return_code}")

            logger.info(f"Successfully logged in to registry: {self._auth_info['registry']}")

        except Exception as e:
            logger.error(f"Failed to login to Docker registry: {str(e)}")
            raise

    def build(self):
        args = {
            "--tag": self.image_uri,
            "--file": self.docker_file_path,
            "--platform": self.build_platform,
            self.project_context: None,
        }

        return self.execute(
            command=self.BUILD_COMMAND,
            arguments=args,
        )

    def push(self):
        """
        Push the image to the registry with automatic token refresh on expiration
        """
        max_retries = 2
        retry_count = 0

        while retry_count < max_retries:
            progress_bars = {}
            try:
                logger.info("Pushing image to registry...")
                for line in self.client.images.push(self.image_uri, decode=True, stream=True):
                    if "error" in line:
                        error_msg = line["error"].lower()
                        if "authorization token has expired" in error_msg or "reauthenticate" in error_msg:
                            if retry_count < max_retries - 1:
                                logger.info("Token expired, refreshing authentication...")
                                self._perform_login()
                                retry_count += 1
                                break  # Break the inner loop to retry the push
                            else:
                                raise ImagePushError(f"Error pushing image after token refresh: {line['error']}")
                        else:
                            raise ImagePushError(f"Error pushing image: {line['error']}")

                    if (
                        "progressDetail" in line
                        and "current" in line["progressDetail"]
                        and "total" in line["progressDetail"]
                    ):
                        layer_id = line["id"]
                        current = line["progressDetail"]["current"]
                        total = line["progressDetail"]["total"]

                        if layer_id not in progress_bars:
                            progress_bars[layer_id] = tqdm(
                                total=total, desc=f"Layer {layer_id[:8]}", unit="B", unit_scale=True, leave=True
                            )

                        progress_bars[layer_id].update(current - progress_bars[layer_id].n)

                    elif "status" in line:
                        if line["status"] == "Pushed":
                            layer_id = line["id"]
                            if layer_id in progress_bars:
                                progress_bars[layer_id].close()
                                del progress_bars[layer_id]

                # If we get here without breaking, push was successful
                logger.info("Image push completed successfully")
                break

            except ImagePushError as e:
                if "token expired" not in str(e).lower() or retry_count >= max_retries - 1:
                    logger.error(f"Push failed: {str(e)}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error during push: {str(e)}")
                raise
            finally:
                # Close any remaining progress bars
                for bar in progress_bars.values():
                    bar.close()

            retry_count += 1


class DockerCloudBuildTool(BuildTool):
    """
    This class will be used to build and push images from Docker Cloud.
    """

    EXECUTABLE = "docker buildx"
    CREATE_COMMAND = "create"
    BUILD_COMMAND = "build"
    PUSH_COMMAND = "push"

    def __init__(
        self,
        project_context: str,
        docker_file_path: str,
        image_uri: str,
        build_platform: str,
    ):
        super().__init__(
            project_context=project_context,
            docker_file_path=docker_file_path,
            image_uri=image_uri,
            build_platform=build_platform,
        )

    def login(self, username: str, password: str, registry: str):
        client = docker.from_env()
        client.login(username=username, password=password, registry=registry)

    def build_and_push(self):  # aws_username: str, aws_password: str, aws_registry: str
        self.build()
        # Login to ECR
        # self.login()
        self.push()

    def create_cloud_builder(self):
        args = {
            "--driver": "cloud",
            "--name": "builder",
        }

        return self.execute(
            command=self.CREATE_COMMAND,
            arguments=args,
        )

    def build(self):
        args = {
            "--tag": self.image_uri,
            "--file": self.docker_file_path,
            "--platform": self.build_platform,
            self.project_context: None,
        }

        return self.execute(
            command=self.BUILD_COMMAND,
            arguments=args,
        )

    def push(self):
        args = {
            self.image_uri: None,
        }

        return self.execute(
            command=self.PUSH_COMMAND,
            arguments=args,
        )


class RemoteBuildTool(BuildTool):
    """
    This class will be used to build and push images from AWS CodeBuild, Google Cloud Build, etc.
    """

    def __init__(self):
        raise NotImplementedError("RemoteBuildTool is not implemented yet.")

    def build(self):
        raise NotImplementedError

    def push(self):
        raise NotImplementedError
