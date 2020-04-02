import pytest
from unittest.mock import patch

from transcribe import (
    TranscribeBatchResult,
    TranscribeJob,
    TranscribeJobRequest,
    TranscribeJobStatus,
    TranscribeJobsUpdate,
)

from .helpers import (
    run_transcribe_test,
    AwsTranscribeGetJobCall,
    AwsTranscribeListJobsCall,
    AwsTranscribeStartJobCall,
    TranscribeTestFixture,
    TEST_AWS_REGION,
    TEST_TRANSCRIBE_SOURCE_BUCKET,
)


@patch("boto3.client")
@pytest.mark.parametrize(
    "fixture",
    [
        (
            TranscribeTestFixture(
                batch_id="b1",
                requests=[
                    TranscribeJobRequest(jobId="m1-u1", sourceFile="/audio/m1/u1.wav")
                ],
                override_expected_start_job_calls=[
                    AwsTranscribeStartJobCall(
                        expected_args={
                            "TranscriptionJobName": "b1-m1-u1",
                            "LanguageCode": "en-US",
                            "Media": {
                                "MediaFileUri": f"https://s3.{TEST_AWS_REGION}.amazonaws.com/{TEST_TRANSCRIBE_SOURCE_BUCKET}/b1-m1-u1.wav"
                            },
                            "MediaFormat": "wav",
                        }
                    )
                ],
                list_jobs_calls=[
                    AwsTranscribeListJobsCall(
                        result={
                            "TranscriptionJobSummaries": [
                                {
                                    "TranscriptionJobName": "b1-m1-u1",
                                    "TranscriptionJobStatus": "COMPLETED",
                                }
                            ]
                        }
                    )
                ],
                get_job_calls=[
                    AwsTranscribeGetJobCall(
                        name="b1-m1-u1",
                        result={
                            "TranscriptionJob": {
                                "TranscriptionJobStatus": "COMPLETED",
                                "Transcript": {
                                    "TranscriptFileUri": "http://fake/b1-m1-u1"
                                },
                            }
                        },
                        transcribe_url_response={
                            "results": {
                                "transcripts": [{"transcript": ""}],
                                "items": [],
                            },
                            "status": "COMPLETED",
                        },
                    )
                ],
                expected_sleep_calls=[],
                expected_result=TranscribeBatchResult(
                    transcribeJobsById={
                        "b1-m1-u1": TranscribeJob(
                            batchId="b1",
                            jobId="m1-u1",
                            sourceFile="/audio/m1/u1.wav",
                            mediaFormat="wav",
                            status=TranscribeJobStatus.SUCCEEDED,
                            transcript="",
                        )
                    }
                ),
                expected_on_update_calls=[
                    TranscribeJobsUpdate(
                        result=TranscribeBatchResult(
                            transcribeJobsById={
                                "b1-m1-u1": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u1",
                                    sourceFile="/audio/m1/u1.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.SUCCEEDED,
                                    transcript="",
                                )
                            }
                        ),
                        idsUpdated=["b1-m1-u1"],
                    )
                ],
            )
        )
    ],
)
def test_it_accepts_a_completed_result_with_empty_transcript(
    mock_boto3_client, fixture: TranscribeTestFixture
):
    run_transcribe_test(mock_boto3_client, fixture)
