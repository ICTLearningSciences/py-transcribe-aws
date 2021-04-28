#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from unittest.mock import patch
from transcribe import init_transcription_service, TranscriptionService
from .helpers import TEST_SERVICE_CONFIG


@patch("boto3.client")
def test_it_creates_a_service_instance_for_module_path(mock_boto3_client):
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
