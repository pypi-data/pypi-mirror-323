import contextlib
import io
import json

import sparkmagic.utils.configuration as conf
from sparkmagic.livyclientlib.exceptions import BadUserDataException
from IPython import get_ipython
from sagemaker_studio_analytics_extension.resource.emr_serverless.emr_s_client import (
    EMRServerlessApplication,
)
from sagemaker_studio_analytics_extension.utils.boto_client_utils import (
    get_boto3_session,
)
from sagemaker_studio_analytics_extension.utils.emr_constants import (
    MAGIC_KERNELS,
    SPARK_SESSION_NAME_PREFIX,
)
from sagemaker_studio_analytics_extension.utils.exceptions import (
    SparkSessionStartFailedFault,
    EMRServerlessError,
)

from sagemaker_studio_analytics_extension.utils.service_metrics import (
    records_service_metrics,
)

EMR_SERVERLESS_APPLICATION_STARTED_STATE = "STARTED"
EMR_SERVERLESS_APPLICATION_STARTING_STATE = "STARTING"

EMR_SERVERLESS_AUTH_TYPE = "Sagemaker_EMR_Serverless_Auth"


class EMRServerlessMagicUtils:
    def __init__(self, args, kernel_name, session_name):
        self.kernel_name = kernel_name
        self.application_id = args.application_id
        self.language = args.language
        self.emr_execution_role_arn = args.emr_execution_role_arn
        self.assumable_role_arn = args.assumable_role_arn
        self.session_name = session_name

    @records_service_metrics
    def connect_to_emr_serverless_application(
        self,
        args,
        session_name,
        kernel_name,
        service,
        operation,
        service_logger,
        context,
    ):
        """
        Connect to EMR Serverless application after starting the application
        """
        try:
            self._setup_spark_configuration()
            boto_session = get_boto3_session(self.assumable_role_arn)
            application = EMRServerlessApplication(
                application_id=self.application_id, session=boto_session
            )
            application.start_application()
            has_application_started = application.poll_until_required_application_state(
                required_state=EMR_SERVERLESS_APPLICATION_STARTED_STATE,
                retryable_states=[EMR_SERVERLESS_APPLICATION_STARTING_STATE],
            )
            livy_endpoint = application.get_livy_endpoint()

            if has_application_started:
                print("Initiating EMR Serverless connection..")
                ipy = get_ipython()
                if self.kernel_name in MAGIC_KERNELS:
                    self._initiate_spark_session_in_magic_kernel(
                        livy_endpoint=livy_endpoint, ipy=ipy
                    )
                else:
                    self._initiate_spark_session_in_ipython_kernel(
                        livy_endpoint=livy_endpoint, ipy=ipy
                    )
        except Exception as e:
            print(json.dumps(self._build_response(error_message=str(e))))
            raise e

    def _setup_spark_configuration(self):
        """
        Setting up spark configuration to allow connecting to EMR Serverless application
        """
        session_configs = conf.session_configs()
        if "conf" not in session_configs:
            session_configs["conf"] = {}
        session_configs["conf"][
            "emr-serverless.session.executionRoleArn"
        ] = self.emr_execution_role_arn
        session_configs["conf"][
            "sagemaker.session.assumableRoleArn"
        ] = self.assumable_role_arn
        conf.override(conf.session_configs.__name__, session_configs)

        authenticators = conf.authenticators()
        authenticators[EMR_SERVERLESS_AUTH_TYPE] = (
            "sagemaker_studio_analytics_extension.external_dependencies.emr_serverless_auth"
            ".EMRServerlessCustomSigV4Signer"
        )
        conf.override(conf.authenticators.__name__, authenticators)

    def _initiate_spark_session_in_ipython_kernel(self, livy_endpoint, ipy):
        # Depth should be 2 if run_line_magic is being called from within a magic
        ipy.run_line_magic("load_ext", "sparkmagic.magics", 2)

        endpoint_magic_line = "add -s {0} -l {1} -t {2} -u {3}".format(
            self.session_name, self.language, EMR_SERVERLESS_AUTH_TYPE, livy_endpoint
        )

        ipy.run_line_magic("spark", endpoint_magic_line)

        # Check if session is created. Return true if sagemaker session name prefix is in '%spark info' response.
        # Sagemaker session name prefix is under control and can be used as stable contract.
        spark_info_output = io.StringIO()
        with contextlib.redirect_stdout(spark_info_output):
            ipy.run_line_magic("spark", "info")

        session_started = SPARK_SESSION_NAME_PREFIX in spark_info_output.getvalue()

        if not session_started:
            raise SparkSessionStartFailedFault("Failed to start spark session.")

    def _initiate_spark_session_in_magic_kernel(self, livy_endpoint, ipy):
        endpoint_magic_line = "-s {0} -t {1}".format(
            livy_endpoint, EMR_SERVERLESS_AUTH_TYPE
        )
        try:
            change_endpoint_magic = ipy.find_line_magic("_do_not_call_change_endpoint")
            change_endpoint_magic(endpoint_magic_line)
        except BadUserDataException as e:
            raise EMRServerlessError(
                "Session already exists, please restart kernel and rerun magic"
            )
        except Exception as e:
            raise SparkSessionStartFailedFault("Failed to start spark session.") from e

        # Start spark session
        start_session_magic = ipy.find_cell_magic("_do_not_call_start_session")
        session_started = start_session_magic("")
        if not session_started:
            raise SparkSessionStartFailedFault("Failed to start spark session.")

    def _build_response(self, error_message):
        return {
            "application_id": self.application_id,
            "error_message": error_message,
            "success": False,
            "service": "emr-serverless",
            "operation": "connect",
        }
