from blazetest.core.container_image.tools import (
    DockerBuildTool,
    DepotBuildTool,
    RemoteBuildTool,
    BuildTool,
    DockerCloudBuildTool,
)

backends: dict[str, type[BuildTool]] = {
    "docker": DockerBuildTool,
    "docker-cloud": DockerCloudBuildTool,
    "depot": DepotBuildTool,
    "remote": RemoteBuildTool,
}


class ImageBuildPush:
    def __init__(
        self,
        project_context: str,
        docker_file_path: str,
        image_uri: str,
        build_platform: str,
        backend="depot",
        *args,
        **kwargs,
    ):
        """
        ImageBuildPusher is a class that builds and pushes images to a remote repository using supported backends.
        For now, the supported backends are only "depot" (depot.dev).

        Example usage:
            ```
            image_build_pusher = ImageBuildPush(
                project_context=".",
                docker_file_path="Dockerfile",
                image_uri="123456789.dkr.ecr.us-west-2.amazonaws.com/blazetest",
                build_platform="linux/amd64",
                backend="depot",
                depot_token="depot_token",
                depot_project_id="depot_project_id",
            )
            image_build_push.login()
            image_build_push.build_and_push()
            ```

        Args:
            project_context: The path to the project context.
            docker_file_path: The path to the Dockerfile.
            image_uri: The URI of the remote repository.
            build_platform: The platform to build the image for.
            backend: The backend to use for building and pushing the image.
        """
        self.backend = backends[backend](
            project_context=project_context,
            docker_file_path=docker_file_path,
            image_uri=image_uri,
            build_platform=build_platform,
            *args,
            **kwargs,
        )

    def login(self, username: str, password: str, registry: str):
        self.backend.login(username, password, registry)

    def build(self):
        self.backend.build()

    def push(self):
        self.backend.push()
