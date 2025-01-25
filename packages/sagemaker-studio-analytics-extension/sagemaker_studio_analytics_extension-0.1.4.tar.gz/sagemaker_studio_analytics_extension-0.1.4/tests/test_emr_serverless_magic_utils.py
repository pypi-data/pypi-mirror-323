import unittest
from unittest.mock import patch, MagicMock, call
import pytest
import sparkmagic.utils.configuration as conf

from sagemaker_studio_analytics_extension.utils.emr_serverless_magic_utils import (
    EMRServerlessMagicUtils,
)

from sagemaker_studio_analytics_extension.utils.exceptions import (
    SparkSessionStartFailedFault,
)


@pytest.fixture(scope="session", autouse=True)
def set_config():
    conf.override(conf.authenticators.__name__, {})
    conf.override(conf.session_configs.__name__, {})


class TestEMRServerlessMagicUtils(unittest.TestCase):
    @patch(
        "sagemaker_studio_analytics_extension.utils.boto_client_utils.get_boto3_session"
    )
    def test_setup_spark_configuration(self, boto_session):
        mock_args = MagicMock()
        mock_args.application_id = "test_application_id"
        mock_args.language = None
        mock_args.emr_execution_role_arn = "test_emr_execution_role_arn"
        mock_args.assumable_role_arn = None
        emr_serverless_magic_utils = EMRServerlessMagicUtils(
            args=mock_args,
            session_name="test_session_name",
            kernel_name="test_kernel_name",
        )
        emr_serverless_magic_utils._setup_spark_configuration()
        self.assertEqual(
            conf.session_configs()["conf"],
            {
                "emr-serverless.session.executionRoleArn": "test_emr_execution_role_arn",
                "sagemaker.session.assumableRoleArn": None,
            },
        )
        self.assertEqual(
            conf.authenticators(),
            {
                "Sagemaker_EMR_Serverless_Auth": "sagemaker_studio_analytics_extension.external_dependencies"
                ".emr_serverless_auth.EMRServerlessCustomSigV4Signer"
            },
        )

    @patch("io.StringIO")
    def test_initiate_spark_session_in_ipython_kernel(self, mock_output):
        mock_args = MagicMock()
        mock_args.application_id = "test_application_id"
        mock_args.language = "python"
        mock_args.emr_execution_role_arn = "test_emr_execution_role_arn"
        emr_serverless_magic_utils = EMRServerlessMagicUtils(
            args=mock_args,
            session_name="test_session_name",
            kernel_name="test_kernel_name",
        )
        mock_ipy = MagicMock()
        mock_output.return_value.getvalue.return_value = (
            "sagemaker_studio_analytics_spark_session1"
        )
        emr_serverless_magic_utils._initiate_spark_session_in_ipython_kernel(
            livy_endpoint="test_livy_endpoint", ipy=mock_ipy
        )

        calls = [
            call("load_ext", "sparkmagic.magics", 2),
            call(
                "spark",
                "add -s test_session_name -l python -t Sagemaker_EMR_Serverless_Auth -u test_livy_endpoint",
            ),
            call("spark", "info"),
        ]
        mock_ipy.run_line_magic.assert_has_calls(calls)

    @patch("io.StringIO")
    def test_initiate_spark_session_in_ipython_kernel_fault(self, mock_output):
        mock_args = MagicMock()
        mock_args.application_id = "test_application_id"
        mock_args.language = "python"
        mock_args.emr_execution_role_arn = "test_emr_execution_role_arn"
        emr_serverless_magic_utils = EMRServerlessMagicUtils(
            args=mock_args,
            session_name="test_session_name",
            kernel_name="test_kernel_name",
        )
        mock_ipy = MagicMock()
        mock_output.return_value.getvalue.return_value = ""
        with pytest.raises(SparkSessionStartFailedFault):
            emr_serverless_magic_utils._initiate_spark_session_in_ipython_kernel(
                livy_endpoint="test_livy_endpoint", ipy=mock_ipy
            )
            calls = [
                call("load_ext", "sparkmagic.magics", 2),
                call(
                    "spark",
                    "add -s test_session_name -l python -t Sagemaker_EMR_Serverless_Auth -u test_livy_endpoint",
                ),
                call("spark", "info"),
            ]
            mock_ipy.run_line_magic.assert_has_calls(calls)

    @patch("io.StringIO")
    def test_initiate_spark_session_in_magic_kernel(self, mock_output):
        mock_args = MagicMock()
        mock_args.application_id = "test_application_id"
        mock_args.language = None
        mock_args.emr_execution_role_arn = "test_emr_execution_role_arn"
        emr_serverless_magic_utils = EMRServerlessMagicUtils(
            args=mock_args,
            session_name="test_session_name",
            kernel_name="test_kernel_name",
        )

        mock_ipy = MagicMock()

        emr_serverless_magic_utils._initiate_spark_session_in_magic_kernel(
            livy_endpoint="test_livy_endpoint", ipy=mock_ipy
        )

        mock_ipy.find_line_magic.assert_has_calls(
            [
                call("_do_not_call_change_endpoint"),
                call()("-s test_livy_endpoint -t Sagemaker_EMR_Serverless_Auth"),
            ]
        )

        mock_ipy.find_cell_magic.assert_has_calls([call("_do_not_call_start_session")])

    def test_initiate_spark_session_in_magic_kernel_fault(self):
        mock_args = MagicMock()
        mock_args.application_id = "test_application_id"
        mock_args.language = None
        mock_args.emr_execution_role_arn = "test_emr_execution_role_arn"
        emr_serverless_magic_utils = EMRServerlessMagicUtils(
            args=mock_args,
            session_name="test_session_name",
            kernel_name="test_kernel_name",
        )

        mock_ipy = MagicMock()
        mock_session_start_magic = MagicMock()
        mock_ipy.find_cell_magic.return_value = mock_session_start_magic
        mock_session_start_magic.return_value = False
        with pytest.raises(SparkSessionStartFailedFault):
            emr_serverless_magic_utils._initiate_spark_session_in_magic_kernel(
                livy_endpoint="test_livy_endpoint", ipy=mock_ipy
            )

            mock_ipy.find_line_magic.assert_has_calls(
                [
                    call("_do_not_call_change_endpoint"),
                    call()("-s test_livy_endpoint -t Sagemaker_EMR_Serverless_Auth"),
                ]
            )

            mock_ipy.find_cell_magic.assert_has_calls(
                [call("_do_not_call_start_session")]
            )
