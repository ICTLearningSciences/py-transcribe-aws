from unittest.mock import patch
from transcribe import init_transcription_service, TranscriptionService

service_config = {
    "AWS_REGION": "fake-region",
    "AWS_S3_BUCKET": "fake-bucket",
    "AWS_ACCESS_KEY_ID": "fake-access-key-id",
    "AWS_SECRET_ACCESS_KEY": "fake-secret-access-key",
}
@patch("boto3.client")
def test_it_initializes_given_module_path(mock_boto3_client):
    service = init_transcription_service(
        module_path="transcribe_aws", config=service_config
    )
    assert isinstance(service, TranscriptionService)
