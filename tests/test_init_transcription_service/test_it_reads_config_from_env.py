import os
from unittest.mock import patch

import pytest

from transcribe import init_transcription_service, TranscriptionService

from .helpers import TEST_SERVICE_ENV


@pytest.fixture(autouse=True)
def after_each_clear_env():
    for k, v in TEST_SERVICE_ENV.items():
        os.environ[k] = v
    yield
    for k, v in TEST_SERVICE_ENV.items():
        if k in os.environ:
            del os.environ[k]


@patch("boto3.client")
def test_it_reads_config_from_env(mock_boto3_client):
    service = init_transcription_service(module_path="transcribe_aws")
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
