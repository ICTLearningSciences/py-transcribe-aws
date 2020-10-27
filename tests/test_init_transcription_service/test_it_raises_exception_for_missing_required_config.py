from unittest.mock import patch
from transcribe import init_transcription_service

from .helpers import TEST_SERVICE_CONFIG


@patch("boto3.client")
def test_it_raises_exception_for_missing_required_aws_region(mock_boto3_client):
    _test_with_var_missing(mock_boto3_client, TEST_SERVICE_CONFIG, "AWS_REGION")


@patch("boto3.client")
def test_it_raises_exception_for_missing_required_aws_secret_access_key(
    mock_boto3_client,
):
    _test_with_var_missing(
        mock_boto3_client, TEST_SERVICE_CONFIG, "AWS_SECRET_ACCESS_KEY"
    )


@patch("boto3.client")
def test_it_raises_exception_for_missing_required_aws_access_key_id(mock_boto3_client):
    _test_with_var_missing(mock_boto3_client, TEST_SERVICE_CONFIG, "AWS_ACCESS_KEY_ID")


@patch("boto3.client")
def test_it_raises_exception_for_missing_required_TRANSCRIBE_AWS_S3_BUCKET_SOURCE(
    mock_boto3_client,
):
    _test_with_var_missing(
        mock_boto3_client, TEST_SERVICE_CONFIG, "TRANSCRIBE_AWS_S3_BUCKET_SOURCE"
    )


def _test_with_var_missing(mock_boto3_client, config: dict, missing_var: str):
    test_config = {k: v for k, v in config.items() if k != missing_var}
    ex_caught: EnvironmentError = None
    try:
        init_transcription_service(module_path="transcribe_aws", config=test_config)
    except EnvironmentError as ex:
        ex_caught = ex
    assert ex_caught is not None
    assert str(ex_caught) == f"missing required env var '{missing_var}'"
