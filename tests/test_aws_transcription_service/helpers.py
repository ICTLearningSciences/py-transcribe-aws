from dataclasses import dataclass, field
import os
import requests_mock
from typing import Any, Dict, List, Tuple
from unittest.mock import call, Mock
from uuid import uuid1

from transcribe import (
    TranscribeBatchResult,
    TranscribeJobRequest,
    TranscribeJobsUpdate,
)
from transcribe.aws import AWSTranscriptionService

from tests.helpers import Bunch


@dataclass
class AwsTranscribeGetJobCall:
    name: str
    result: Dict[str, Any] = field(default_factory=lambda: {})
    transcribe_url_response: Dict[str, str] = field(default_factory=lambda: {})

    def is_success_result(self) -> bool:
        return (
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
    default_batch_id: str = ""
    requests: List[TranscribeJobRequest] = field(default_factory=lambda: [])
    get_job_calls: List[AwsTranscribeGetJobCall] = field(default_factory=lambda: [])
    list_jobs_calls: List[AwsTranscribeListJobsCall] = field(default_factory=lambda: [])
    expected_on_update_calls: List[TranscribeJobsUpdate] = field(default_factory=lambda: [])
    expected_result: TranscribeBatchResult = field(
        default_factory=lambda: TranscribeBatchResult()
    )


TEST_TRANSCRIBE_SOURCE_BUCKET = "test_transcribe_source_bucket"
TEST_AWS_REGION = "fake_aws_region"


def create_service(mock_boto3_client) -> Tuple[AWSTranscriptionService, Any, Any]:
    os.environ["AWS_ACCESS_KEY_ID"] = "fake_aws_access_key_id"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "fake_aws_secret_access_key"
    os.environ["AWS_REGION"] = TEST_AWS_REGION
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
    return (
        AWSTranscriptionService(TEST_TRANSCRIBE_SOURCE_BUCKET),
        mock_s3_client,
        mock_transcribe_client,
    )


def run_transcribe_test(mock_boto3_client, fixture: TranscribeTestFixture):
    transcribe_service, mock_s3_client, mock_transcribe_client = create_service(
        mock_boto3_client
    )
    batch_id = uuid1()
    spy_on_update = Mock()
    expected_upload_file_calls = []
    expected_start_transcription_job_calls = []
    for r in fixture.requests:
        input_s3_path = transcribe_service.get_s3_path(r.sourceFile, r.get_fq_id())
        expected_upload_file_calls.append(
            call(
                r.sourceFile,
                TEST_TRANSCRIBE_SOURCE_BUCKET,
                input_s3_path,
                ExtraArgs={"ACL": "public-read"},
            )
        )
        expected_start_transcription_job_calls.append(
            call(
                TranscriptionJobName=r.get_fq_id(),
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
            call(JobNameContains=batch_id, NextToken=c.next_token)
        )
        mock_list_call_responses.append(c.result)
    mock_transcribe_client.list_transcription_jobs.side_effect = (
        mock_list_call_responses
    )
    expected_get_job_calls = []
    mock_get_job_responses = []
    with requests_mock.Mocker() as mock_requests:
        for c in fixture.get_job_calls:
            expected_get_job_calls.append(call(TranscriptionJobName=c.name))
            if c.is_success_result():
                t_url = c.get_transcription_url()
                mock_requests.get(t_url, json=c.transcribe_url_response)
            mock_get_job_responses.append(c.result)
        mock_transcribe_client.get_transcription_job.side_effect = (
            mock_get_job_responses
        )
        result = transcribe_service.transcribe(
            fixture.requests,
            on_update=spy_on_update,
            batch_id=batch_id,
            poll_interval=0,
        )
        mock_s3_client.upload_file.assert_has_calls(expected_upload_file_calls)
        mock_transcribe_client.start_transcription_job.assert_has_calls(
            expected_start_transcription_job_calls
        )
        assert result.to_dict() == fixture.expected_result.to_dict()
        if fixture.expected_on_update_calls:
            expected_on_update_calls = [call(u) for u in fixture.expected_on_update_calls]
            spy_on_update.assert_has_calls(expected_on_update_calls)
