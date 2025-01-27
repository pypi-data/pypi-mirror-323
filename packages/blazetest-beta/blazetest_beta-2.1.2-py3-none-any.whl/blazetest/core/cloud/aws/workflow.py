import json
import logging
import time

import boto3
from typing import Dict

from botocore.exceptions import WaiterError

from blazetest.core.utils.exceptions import AWSLambdaFunctionNotCreated

logger = logging.getLogger(__name__)


class AWSWorkflow:
    """
    The AWSWorkflow class is used to deploy an AWS Lambda function using boto3.

    Attributes:
        s3_bucket_name (str): The name of the S3 bucket to use.
        resource_prefix (str): The prefix for resource names.
        tags (dict): Tags to pass to the lambda
        env_vars (Dict[str, str]): Environment variables for the Lambda function.

    Methods:
        deploy(): Deploys the Lambda function.
        create_lambda_function(): Creates the Lambda function.
        create_iam_role(): Creates the IAM role for the Lambda function.
        create_iam_policy(): Creates the IAM policy for the Lambda function.
        attach_policy_to_role(): Attaches the IAM policy to the IAM role.
    """

    def __init__(
        self,
        aws_region: str,
        resource_prefix: str,
        s3_bucket_name: str,
        tags: dict,
        env_vars: Dict[str, str],
    ):
        self.aws_region = aws_region
        self.resource_prefix = resource_prefix
        self.s3_bucket_name = s3_bucket_name
        self.tags = tags or {}
        self.env_vars = env_vars

        self.iam_client = boto3.client("iam", region_name=aws_region)
        self.lambda_client = boto3.client("lambda", region_name=aws_region)

    def deploy(
        self,
        loki_user: str,
        loki_host: str,
        loki_api_key: str,
        image_uri: str,
        memory_size: int,
        function_timeout: int,
        ephemeral_storage_size: int,
    ):
        role_arn, role_created = self.get_or_create_iam_role()
        policy_arn, policy_created = self.get_or_create_iam_policy()

        if role_created or policy_created:
            self.attach_policy_to_role(role_arn, policy_arn)
            logger.info("Waiting for IAM role/policy propagation...")
            time.sleep(10)

        self.create_lambda_function(
            role_arn,
            loki_user,
            loki_host,
            loki_api_key,
            image_uri,
            memory_size,
            function_timeout,
            ephemeral_storage_size,
        )

    def get_or_create_iam_role(self) -> tuple[str, bool]:
        role_name = f"{self.resource_prefix[:15]}-role"
        try:
            response = self.iam_client.get_role(RoleName=role_name)
            logger.info(f"IAM role {role_name} already exists.")
            return response["Role"]["Arn"], False
        except self.iam_client.exceptions.NoSuchEntityException:
            logger.info(f"Creating IAM role {role_name}...")
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }
            response = self.iam_client.create_role(
                RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_role_policy)
            )
            return response["Role"]["Arn"], True

    def get_or_create_iam_policy(self) -> tuple[str, bool]:
        policy_name = f"{self.resource_prefix[:15]}-policy"
        try:
            response = self.iam_client.get_policy(
                PolicyArn=f"arn:aws:iam::{boto3.client('sts').get_caller_identity()['Account']}:policy/{policy_name}"
            )
            logger.info(f"IAM policy {policy_name} already exists.")
            return response["Policy"]["Arn"], False
        except self.iam_client.exceptions.NoSuchEntityException:
            logger.info(f"Creating IAM policy {policy_name}...")
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["s3:PutObject"],
                        "Resource": f"arn:aws:s3:::{self.s3_bucket_name}/*",
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                            "logs:PutRetentionPolicy",
                            "logs:DescribeLogStreams",
                        ],
                        "Resource": ["arn:aws:logs:*:*:*"],
                    },
                ],
            }
            response = self.iam_client.create_policy(PolicyName=policy_name, PolicyDocument=json.dumps(policy_document))
            return response["Policy"]["Arn"], True

    def attach_policy_to_role(self, role_arn: str, policy_arn: str):
        logger.info(f"Attaching IAM policy to IAM role {self.resource_prefix}...")
        role_name = role_arn.split("/")[-1]
        try:
            self.iam_client.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            logger.info(f"Policy {policy_arn} is already attached to role {role_name}")

    def create_lambda_function(
        self,
        role_arn: str,
        loki_user: str,
        loki_host: str,
        loki_api_key: str,
        image_uri: str,
        memory_size: int,
        function_timeout: int,
        ephemeral_storage_size: int = 2048,
    ):
        logger.info(f"Creating Lambda function {self.resource_prefix}...")
        environment_variables = {
            "S3_BUCKET": self.s3_bucket_name,
            "LOKI_USER": loki_user,
            "LOKI_HOST": loki_host,
            "LOKI_API_KEY": loki_api_key,
            **self.env_vars,
        }

        environment_variables = {k: v for k, v in environment_variables.items() if v is not None}

        response = self.lambda_client.create_function(
            FunctionName=f"{self.resource_prefix}-{self.tags['blazetest:uuid']}",
            Role=role_arn,
            PackageType="Image",
            Code={"ImageUri": image_uri},
            Description="Lambda function for execution of PyTest tests in parallel",
            MemorySize=memory_size,
            Timeout=function_timeout,
            Environment={"Variables": environment_variables},
            Tags=self.tags,
            EphemeralStorage={"Size": ephemeral_storage_size},
        )

        function_name = response["FunctionName"]

        logger.info(f"Waiting for function {function_name} to be ready...")
        waiter = self.lambda_client.get_waiter("function_active")

        try:
            waiter.wait(FunctionName=function_name, WaiterConfig={"Delay": 5, "MaxAttempts": 60})
            logger.info(f"Function {function_name} is now ready.")
        except WaiterError as e:
            raise AWSLambdaFunctionNotCreated(f"Function {function_name} failed to become ready: {str(e)}")
