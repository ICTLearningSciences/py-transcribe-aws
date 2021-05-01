#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from dataclasses import dataclass, field
import requests_mock
from typing import Any, Callable, Dict, List, Optional, Tuple
from unittest.mock import call, patch, Mock

from transcribe import TranscribeBatchResult, TranscribeJobRequest, TranscribeJobsUpdate
from transcribe_aws import AWSTranscriptionService

from tests.helpers import Bunch


class FakeLimitExceededException(BaseException):
    def __init__(self):
        super().__init__("LimitExceeded (fake)")


def raise_limit_exceeded():
    raise FakeLimitExceededException()


@dataclass
class AwsTranscribeStartJobCall:
    expected_args: Dict[str, Any]
    side_effect: Optional[Callable[[], None]] = None


@dataclass
class AwsTranscribeGetJobCall:
    name: str
    result: Dict[str, Any] = field(default_factory=lambda: {})
    transcribe_url_response: Dict[str, Any] = field(default_factory=lambda: {})

    def is_success_result(self) -> bool:
        return bool(
            self.result
            and "TranscriptionJob" in self.result
            and self.result["TranscriptionJob"].get("TranscriptionJobStatus")
            == "COMPLETED"
        )

    def get_transcription_url(self) -> bool:
        return self.result["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]


@dataclass
class AwsTranscribeListJobsCall:
    next_token: str = ""
    result: Dict[str, Any] = field(default_factory=lambda: {})


@dataclass
class TranscribeTestFixture:
    batch_id: str = ""
    mock_next_batch_id: str = "b1"
    requests: List[TranscribeJobRequest] = field(default_factory=lambda: [])
    get_job_calls: List[AwsTranscribeGetJobCall] = field(default_factory=lambda: [])
    list_jobs_calls: List[AwsTranscribeListJobsCall] = field(default_factory=lambda: [])
    override_expected_start_job_calls: List[AwsTranscribeStartJobCall] = field(
        default_factory=lambda: []
    )
    expected_on_update_calls: List[TranscribeJobsUpdate] = field(
        default_factory=lambda: []
    )
    expected_result: TranscribeBatchResult = field(
        default_factory=lambda: TranscribeBatchResult()
    )
    expected_sleep_calls: List[float] = field(default_factory=lambda: [])


TEST_TRANSCRIBE_SOURCE_BUCKET = "test_transcribe_source_bucket"
TEST_AWS_REGION = "fake_aws_region"


def create_service(mock_boto3_client) -> Tuple[AWSTranscriptionService, Any, Any]:
    mock_s3_client = Bunch(upload_file=Mock())
    mock_transcribe_client = Bunch(
        get_transcription_job=Mock(),
        list_transcription_jobs=Mock(),
        start_transcription_job=Mock(),
    )

    def return_clients(client_type, **kwargs):
        return (
            mock_s3_client
            if client_type == "s3"
            else mock_transcribe_client
            if client_type == "transcribe"
            else None
        )

    mock_boto3_client.side_effect = return_clients
    service = AWSTranscriptionService()
    service.init_service(
        config={
            "AWS_REGION": TEST_AWS_REGION,
            "AWS_SECRET_ACCESS_KEY": "fake_aws_secret_access_key",
            "AWS_ACCESS_KEY_ID": "fake_aws_access_key_id",
            "TRANSCRIBE_AWS_S3_BUCKET_SOURCE": TEST_TRANSCRIBE_SOURCE_BUCKET,
        }
    )
    return (service, mock_s3_client, mock_transcribe_client)


def run_transcribe_test(mock_boto3_client: Mock, fixture: TranscribeTestFixture):
    with patch("time.sleep") as mock_sleep, patch(
        "transcribe_aws.next_batch_id"
    ) as mock_next_batch_id:
        transcribe_service, mock_s3_client, mock_transcribe_client = create_service(
            mock_boto3_client
        )
        mock_next_batch_id.return_value = fixture.mock_next_batch_id
        batch_id_effective = fixture.batch_id or fixture.mock_next_batch_id
        spy_on_update = Mock()
        expected_upload_file_calls = []
        expected_start_transcription_job_calls = (
            [call(**c.expected_args) for c in fixture.override_expected_start_job_calls]
            if fixture.override_expected_start_job_calls
            else []
        )
        if fixture.override_expected_start_job_calls:
            start_transcription_job_side_effects = [
                sjc.side_effect for sjc in fixture.override_expected_start_job_calls
            ]

            def _side_effect(*arg, **kwargs):
                if start_transcription_job_side_effects:
                    e = start_transcription_job_side_effects.pop(0)
                    if e:
                        e()

            mock_transcribe_client.start_transcription_job.side_effect = _side_effect
        for r in fixture.requests:
            fqid = f"{batch_id_effective}-{r.jobId}"
            input_s3_path = transcribe_service.get_s3_path(r.sourceFile, fqid)
            expected_upload_file_calls.append(
                call(
                    r.sourceFile,
                    TEST_TRANSCRIBE_SOURCE_BUCKET,
                    input_s3_path,
                    ExtraArgs={"ACL": "public-read"},
                )
            )
            if not fixture.override_expected_start_job_calls:
                expected_start_transcription_job_calls.append(
                    call(
                        TranscriptionJobName=fqid,
                        Media={
                            "MediaFileUri": f"https://s3.{TEST_AWS_REGION}.amazonaws.com/{TEST_TRANSCRIBE_SOURCE_BUCKET}/{input_s3_path}"
                        },
                        MediaFormat=r.get_media_format(),
                        LanguageCode=r.get_language_code(),
                    )
                )
        expected_list_jobs_calls = []
        mock_list_call_responses = []
        for c in fixture.list_jobs_calls:
            expected_list_jobs_calls.append(
                call(JobNameContains=batch_id_effective, NextToken=c.next_token)
            )
            mock_list_call_responses.append(c.result)
        mock_transcribe_client.list_transcription_jobs.side_effect = (
            mock_list_call_responses
        )
        expected_get_job_calls = []
        mock_get_job_responses = []
        with requests_mock.Mocker() as mock_requests:
            for gjc in fixture.get_job_calls:
                expected_get_job_calls.append(call(TranscriptionJobName=gjc.name))
                if gjc.is_success_result():
                    t_url = gjc.get_transcription_url()
                    mock_requests.get(t_url, json=gjc.transcribe_url_response)
                mock_get_job_responses.append(gjc.result)
            mock_transcribe_client.get_transcription_job.side_effect = (
                mock_get_job_responses
            )
            result = transcribe_service.transcribe(
                fixture.requests, on_update=spy_on_update, batch_id=fixture.batch_id
            )
            mock_s3_client.upload_file.assert_has_calls(expected_upload_file_calls)
            mock_transcribe_client.start_transcription_job.assert_has_calls(
                expected_start_transcription_job_calls
            )
            if fixture.expected_sleep_calls:
                mock_sleep.assert_has_calls(
                    [
                        call(sleep_interval)
                        for sleep_interval in fixture.expected_sleep_calls
                    ]
                )
            assert result.to_dict() == fixture.expected_result.to_dict()
            if fixture.expected_on_update_calls:
                expected_on_update_calls = [
                    call(u) for u in fixture.expected_on_update_calls
                ]
                spy_on_update.assert_has_calls(expected_on_update_calls)
