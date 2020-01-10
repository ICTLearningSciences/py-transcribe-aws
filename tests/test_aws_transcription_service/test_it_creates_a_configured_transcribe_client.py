from unittest.mock import patch

from .helpers import (
    create_service,
)


@patch("boto3.client")
def test_it_creates_a_configured_transcribe_client(mock_boto3_client):
    create_service(mock_boto3_client)
    mock_boto3_client.assert_any_call(
        "transcribe",
        region_name="fake_aws_region",
        aws_access_key_id="fake_aws_access_key_id",
        aws_secret_access_key="fake_aws_secret_access_key",
    )
