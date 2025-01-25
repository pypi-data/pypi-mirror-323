"""
 Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Licensed under the Apache License, Version 2.0 (the "License").
  You may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""

from sparkmagic.auth.customauth import Authenticator
from sparkmagic.utils.sparklogger import SparkLog

from boto3 import session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import json
import os
import re

from sagemaker_studio_analytics_extension.utils.boto_client_utils import (
    get_boto3_session,
)

SERVICE_NAME = "emr-serverless"
AWS_REGION = "AWS_REGION"
AWS_DEFAULT_REGION = "AWS_DEFAULT_REGION"
DEFAULT_EXECUTION_ROLE_ENV = "EMR_SERVERLESS_SESSION_RUNTIME_ROLE_ARN"


class RuntimeRoleNotFoundException(Exception):
    pass


class EMRServerlessCustomSigV4Signer(Authenticator):
    """Custom authenticator for SparkMagic
    1. read the creds using botocore
    2. calculate the SigV4 signature
    3. and add required headers to the request.
    """

    def __init__(self, parsed_attributes=None):
        """Initializes the Authenticator with the attributes in the attributes
        parsed from a %spark magic command if applicable, or with default values
        otherwise.

        Args:
            self,
            parsed_attributes (IPython.core.magics.namespace): The namespace object that
            is created from parsing %spark magic command.
        """
        Authenticator.__init__(self, parsed_attributes)
        self.logger = SparkLog("EMRServerlessSigV4Auth")
        if parsed_attributes is not None:
            url = parsed_attributes.__dict__["url"]
        else:
            url = ""
        self.region = self.get_aws_region(url)
        self.default_role_arn = self.get_default_role_arn()
        self.assumable_role_arn = None

    def add_sigv4_auth(self, request):
        """
        Adds the Sigv4 signature to the request payload using the credentials available.
        """

        boto_session = get_boto3_session(self.assumable_role_arn)
        credentials = boto_session.get_credentials().get_frozen_credentials()

        try:
            aws_signer = SigV4Auth(credentials, SERVICE_NAME, self.region)
            payload = request.body
            http_method = request.method
            orig_headers = request.headers
            aws_headers = {
                "Content-Type": orig_headers.get("Content-Type", "application/json")
            }
            aws_request = AWSRequest(
                method=http_method, url=request.url, data=payload, headers=aws_headers
            )
            aws_signer.add_auth(aws_request)

            for key in aws_request.headers.keys():
                value = aws_request.headers.get(key)

                request.headers[key] = value
        except Exception as err:
            self.logger.error(f"Unexpected {err=}, {type(err)=}")

    def add_defaults_to_body(self, request):
        """
        Adds the default execution role to create session request body.
        """
        try:
            body = json.loads(request.body)
            if "conf" not in body:
                body["conf"] = {}
            session_execution_role = body["conf"].get(
                "emr-serverless.session.executionRoleArn", self.default_role_arn
            )
            if session_execution_role is None:
                raise RuntimeRoleNotFoundException(
                    "Execution role arn is missing. Set the environment variable "
                    + f"{DEFAULT_EXECUTION_ROLE_ENV} or specify emr-serverless.session.executionRoleArn via the %%configure magic"
                )
            body["conf"][
                "emr-serverless.session.executionRoleArn"
            ] = session_execution_role
            del body["conf"]["sagemaker.session.assumableRoleArn"]
            request.body = json.dumps(body)
        except RuntimeRoleNotFoundException as ex:
            raise
        except Exception as err:
            self.logger.error(
                f"Unable to set defaults, unexpected error. {err=}, {type(err)=}"
            )

    def __call__(self, request):
        if request.method == "POST" and request.url.endswith("/sessions"):
            self.get_assumable_role_arn(request.body)
            self.add_defaults_to_body(request)
        self.add_sigv4_auth(request)

        return request

    def __hash__(self):
        return hash((self.url, self.__class__.__name__))

    def get_aws_region(self, url) -> str:
        url_pattern = r".*\.livy.emr-serverless-services.([a-z0-9-]+).*"
        matcher = re.match(url_pattern, url)
        default_region = "us-west-2"
        if matcher:
            region = matcher.group(1)
        else:
            region = os.getenv(
                AWS_REGION, os.getenv(AWS_DEFAULT_REGION, default_region)
            )
        self.logger.info("AWS region resolved to " + region)
        return region

    def get_default_role_arn(self) -> str:
        if DEFAULT_EXECUTION_ROLE_ENV in os.environ:
            return os.getenv(DEFAULT_EXECUTION_ROLE_ENV)
        else:
            self.logger.debug("Default execution role not provided")
            return None

    def get_assumable_role_arn(self, request_body):
        body = json.loads(request_body)
        if "conf" in body:
            self.assumable_role_arn = body["conf"].get(
                "sagemaker.session.assumableRoleArn", None
            )
