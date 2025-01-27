import datetime
import json
import logging
from typing import List

import boto3
import botocore
from botocore.config import Config

from blazetest.core.config import MAX_LAMBDA_WORKERS
from blazetest.core.utils.exceptions import LambdaNotCreated

logger = logging.getLogger(__name__)


class AWSLambda:
    """
    Invocation class, which is used to invoke AWS Lambda

    Attributes:
        region: AWS region.
        resource_prefix: Used CloudFormation stack name

    Methods:
        invoke(): invokes Lambda function with payload
        get_created_lambda_function_details(): returns the exact function name and
            S3 Bucket that it has access to
    """

    LAMBDA_INVOCATION_TYPE = "RequestResponse"
    LAMBDA_LOG_TYPE = "Tail"
    LAMBDA_TIMEOUT = 60 * 15

    def __init__(
        self,
        region: str = None,
        resource_prefix: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
    ):
        self.region = region
        self.resource_prefix = resource_prefix
        self.client = boto3.client(
            "lambda",
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=Config(
                read_timeout=self.LAMBDA_TIMEOUT,  # for 15 minutes - Lambda's invocation duration timeout
                max_pool_connections=MAX_LAMBDA_WORKERS,
            ),
        )

    def invoke(
        self,
        function_name: str,
        session_uuid: str,
        runtime: str,
        execution_args: List[str],
        node_ids: List[str],
        report_path: str,
        timestamp: str,
        retry: bool = False,
    ) -> dict:
        """
        Invoke Lambda function with support for multiple test frameworks

        Args:
            function_name: Name of the Lambda function
            session_uuid: Session identifier
            runtime: Test runtime ("python" or "java")
            execution_args: Framework-specific execution arguments
            node_ids: Test identifiers
            report_path: Path for test report
            timestamp: Execution timestamp
            retry: Whether this is a retry attempt
        """
        payload = {
            "runtime": runtime,
            "execution_args": execution_args,
            "node_ids": node_ids,
            "session_uuid": session_uuid,
            "report_path": report_path,
            "region": self.region,
            "start_timestamp": timestamp,
            "retry": retry,
        }

        try:
            return self.process_response(
                response=self.client.invoke(
                    FunctionName=function_name,
                    InvocationType=self.LAMBDA_INVOCATION_TYPE,
                    LogType=self.LAMBDA_LOG_TYPE,
                    Payload=json.dumps(payload),
                )
            )
        except botocore.exceptions.ReadTimeoutError as err:
            logger.warning(f"Invocation timeout for: {node_ids}, error: {err}")
            return {}

    def list_functions_to_purge(
        self,
        run_id: str,
        time_limit: int,
        exclude_tags: List[str],
    ) -> List[str]:
        """
        Purges all the Lambda functions that are:
        1) If run_id specified, purges only the Lambda function with the specified run_id
        2) Not older than the specified time limit, and
        3) If tags specified, does not have the specified excluded tags

        Args:
            run_id: UUID of the test session, checked against tag with key : "blazetest:uuuid"
            time_limit: Time limit in hours.
            exclude_tags: List of tags in Lambda function that should be excluded from purging

        Returns:
            list of functions to delete
        """
        current_time = datetime.datetime.now(datetime.timezone.utc)
        time_threshold = current_time - datetime.timedelta(hours=time_limit)

        functions_to_delete = []

        paginator = self.client.get_paginator("list_functions")
        for page in paginator.paginate():
            for function in page["Functions"]:
                function_name = function["FunctionName"]

                # Get the function tags
                try:
                    tags_response = self.client.list_tags(Resource=function["FunctionArn"])
                    tags = tags_response["Tags"]
                except Exception as e:
                    logger.error(f"Error getting tags for function {function_name}: {str(e)}")
                    continue

                if tags.get("blazetest:uuid") is None:
                    logger.debug(f"Function {function_name} is not blazetest function")
                    continue

                # Check if the function has the specified run_id
                if run_id and tags.get("blazetest:uuid") == run_id:
                    functions_to_delete.append(function_name)
                    continue

                # Check if the function is within the time limit
                last_modified = datetime.datetime.strptime(function["LastModified"], "%Y-%m-%dT%H:%M:%S.%f%z")
                if last_modified < time_threshold:
                    logger.debug(f"Function {function_name} is older than the time limit: {function['LastModified']}")
                    continue

                # Check if the function has any of the excluded tags
                if exclude_tags and any(tag in tags for tag in exclude_tags):
                    logger.debug(f"Function {function_name} has excluded tags: {tags}")
                    continue

                functions_to_delete.append(function_name)

        return functions_to_delete

    def batch_delete(self, function_names: List[str]):
        for function_name in function_names:
            try:
                self.client.delete_function(FunctionName=function_name)
                logger.info(f"Deleted Lambda function: {function_name}")
            except Exception as e:
                logger.error(f"Error deleting function {function_name}: {str(e)}")

    @staticmethod
    def process_response(response) -> dict:
        """
        Converts response JSON to Python-dict and returns a bool if test passed.
        Raises an error if there is any error message.

        :param response:
        :return:
        """
        result_payload = json.loads(response["Payload"].read())
        try:
            result_body = json.loads(result_payload["body"])
            logger.debug(result_body)
        except KeyError:
            error_message = result_payload["errorMessage"]
            logger.error(
                f"There was an error during test execution: {error_message}",
            )
            return {"test_result": False, "report_path": ""}
        return result_body

    # TODO: is it possible to use other method for retrieving details of created lambda function?
    def get_created_lambda_function_details(self) -> str:
        """
        Retrieves the details of a specific Lambda function that was created.

        The function queries the list of functions from the AWS Lambda service using the `client` object.
        It looks for a function whose name starts with a resource_prefix.
        The function then saves the name of the function in a dictionary.

        Raises:
        If it does not find a function with the specific name, it raises LambdaNotCreated.

        It returns the dictionary with the function details if it is able to find the function
            with the specific namee.

        Returns:
            str : A dictionary containing the function name value.
        """
        functions = []
        response = self.client.list_functions()
        while response:
            functions.extend(response["Functions"])
            response = self.client.list_functions(Marker=response["NextMarker"]) if "NextMarker" in response else None

        function = None
        for f in functions:
            if f["FunctionName"].startswith(f"{self.resource_prefix}"):
                function = f
                break

        if function is None:
            raise LambdaNotCreated("Lambda function seems to be not created")

        function_name = function["FunctionName"]
        return function_name
