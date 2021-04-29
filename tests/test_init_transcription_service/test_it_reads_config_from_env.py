#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from typing import Dict, TypedDict
from unittest.mock import patch

from transcribe import init_transcription_service, TranscriptionService


class AWSConfig(TypedDict):
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str


def _test_it_reads_config_from_env(
    mock_boto3_client,
    monkeypatch,
    test_env_dict: Dict[str, str],
    expected_aws_config: AWSConfig,
):
    for k, v in test_env_dict.items():
        monkeypatch.setenv(k, v)
    service = init_transcription_service(module_path="transcribe_aws")
    assert isinstance(service, TranscriptionService)
    mock_boto3_client.assert_any_call(
        "s3",
        region_name=expected_aws_config["region_name"],
        aws_access_key_id=expected_aws_config["aws_access_key_id"],
        aws_secret_access_key=expected_aws_config["aws_secret_access_key"],
    )
    mock_boto3_client.assert_any_call(
        "transcribe",
        region_name=expected_aws_config["region_name"],
        aws_access_key_id=expected_aws_config["aws_access_key_id"],
        aws_secret_access_key=expected_aws_config["aws_secret_access_key"],
    )


@patch("boto3.client")
def test_it_reads_plain_aws_vars(mock_boto3_client, monkeypatch):
    _test_it_reads_config_from_env(
        mock_boto3_client,
        monkeypatch,
        {
            "AWS_ACCESS_KEY_ID": "fake-access-key-id",
            "AWS_REGION": "fake-region",
            "AWS_SECRET_ACCESS_KEY": "fake-secret-access-key",
            "TRANSCRIBE_AWS_S3_BUCKET_SOURCE": "fake-bucket",
        },
        dict(
            aws_access_key_id="fake-access-key-id",
            aws_secret_access_key="fake-secret-access-key",
            region_name="fake-region",
        ),
    )


@patch("boto3.client")
def test_it_prefers_transcribe_prefixed_aws_vars(mock_boto3_client, monkeypatch):
    _test_it_reads_config_from_env(
        mock_boto3_client,
        monkeypatch,
        {
            "AWS_ACCESS_KEY_ID": "fake-access-key-id",
            "AWS_REGION": "fake-region",
            "AWS_SECRET_ACCESS_KEY": "fake-secret-access-key",
            "TRANSCRIBE_AWS_S3_BUCKET_SOURCE": "fake-bucket",
            "TRANSCRIBE_AWS_ACCESS_KEY_ID": "prefixed-fake-access-key-id",
            "TRANSCRIBE_AWS_REGION": "prefixed-fake-region",
            "TRANSCRIBE_AWS_SECRET_ACCESS_KEY": "prefixed-fake-secret-access-key",
        },
        dict(
            aws_access_key_id="prefixed-fake-access-key-id",
            aws_secret_access_key="prefixed-fake-secret-access-key",
            region_name="prefixed-fake-region",
        ),
    )
