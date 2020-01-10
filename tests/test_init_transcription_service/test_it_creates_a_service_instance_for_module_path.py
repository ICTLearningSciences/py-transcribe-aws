from unittest.mock import patch
from transcribe import init_transcription_service, TranscriptionService
from .helpers import TEST_SERVICE_CONFIG


@patch("boto3.client")
def test_it_initializes_from_the_module_path(mock_boto3_client):
    service = init_transcription_service(
        module_path="transcribe_aws", config=TEST_SERVICE_CONFIG
    )
    assert isinstance(service, TranscriptionService)
    mock_boto3_client.assert_any_call(
        "s3",
        region_name="fake-region",
        aws_access_key_id="fake-access-key-id",
        aws_secret_access_key="fake-secret-access-key",
    )
    mock_boto3_client.assert_any_call(
        "transcribe",
        region_name="fake-region",
        aws_access_key_id="fake-access-key-id",
        aws_secret_access_key="fake-secret-access-key",
    )
