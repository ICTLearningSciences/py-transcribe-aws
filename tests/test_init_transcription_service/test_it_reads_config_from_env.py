#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
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
