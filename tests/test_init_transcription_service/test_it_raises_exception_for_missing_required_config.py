#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from typing import Optional
from unittest.mock import patch
from transcribe import init_transcription_service

from .helpers import TEST_SERVICE_CONFIG


@patch("boto3.client")
def test_it_raises_exception_for_missing_required_aws_region(mock_boto3_client):
    _test_with_var_missing(
        mock_boto3_client,
        TEST_SERVICE_CONFIG,
        "AWS_REGION",
        "TRANSCRIBE_AWS_REGION|AWS_REGION",
    )


@patch("boto3.client")
def test_it_raises_exception_for_missing_required_aws_secret_access_key(
    mock_boto3_client,
):
    _test_with_var_missing(
        mock_boto3_client,
        TEST_SERVICE_CONFIG,
        "AWS_SECRET_ACCESS_KEY",
        "TRANSCRIBE_AWS_SECRET_ACCESS_KEY|AWS_SECRET_ACCESS_KEY",
    )


@patch("boto3.client")
def test_it_raises_exception_for_missing_required_aws_access_key_id(mock_boto3_client):
    _test_with_var_missing(
        mock_boto3_client,
        TEST_SERVICE_CONFIG,
        "AWS_ACCESS_KEY_ID",
        "TRANSCRIBE_AWS_ACCESS_KEY_ID|AWS_ACCESS_KEY_ID",
    )


@patch("boto3.client")
def test_it_raises_exception_for_missing_required_TRANSCRIBE_AWS_S3_BUCKET_SOURCE(
    mock_boto3_client,
):
    _test_with_var_missing(
        mock_boto3_client, TEST_SERVICE_CONFIG, "TRANSCRIBE_AWS_S3_BUCKET_SOURCE"
    )


def _test_with_var_missing(
    mock_boto3_client, config: dict, missing_var: str, err: str = ""
):
    test_config = {k: v for k, v in config.items() if k != missing_var}
    ex_caught: Optional[EnvironmentError] = None
    try:
        init_transcription_service(module_path="transcribe_aws", config=test_config)
    except EnvironmentError as ex:
        ex_caught = ex
    assert ex_caught is not None
    assert str(ex_caught) == f"missing required env var {err or missing_var}"
