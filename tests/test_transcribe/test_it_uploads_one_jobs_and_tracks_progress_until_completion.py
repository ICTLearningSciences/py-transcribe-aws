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
    TranscribeTestFixture,
)


@patch("boto3.client")
@pytest.mark.parametrize(
    "fixture",
    [
        (
            TranscribeTestFixture(
                requests=[
                    TranscribeJobRequest(
                        batchId="b1", jobId="m1-u1", sourceFile="/audio/m1/u1.wav"
                    )
                ],
                list_jobs_calls=[
                    AwsTranscribeListJobsCall(
                        result={
                            "TranscriptionJobSummaries": [
                                {
                                    "TranscriptionJobName": "b1-m1-u1",
                                    "TranscriptionJobStatus": "QUEUED",
                                }
                            ]
                        }
                    ),
                    AwsTranscribeListJobsCall(
                        result={
                            "TranscriptionJobSummaries": [
                                {
                                    "TranscriptionJobName": "b1-m1-u1",
                                    "TranscriptionJobStatus": "QUEUED",
                                }
                            ]
                        }
                    ),
                    AwsTranscribeListJobsCall(
                        result={
                            "TranscriptionJobSummaries": [
                                {
                                    "TranscriptionJobName": "b1-m1-u1",
                                    "TranscriptionJobStatus": "IN_PROGRESS",
                                }
                            ]
                        }
                    ),
                    AwsTranscribeListJobsCall(
                        result={
                            "TranscriptionJobSummaries": [
                                {
                                    "TranscriptionJobName": "b1-m1-u1",
                                    "TranscriptionJobStatus": "IN_PROGRESS",
                                }
                            ]
                        }
                    ),
                    AwsTranscribeListJobsCall(
                        result={
                            "TranscriptionJobSummaries": [
                                {
                                    "TranscriptionJobName": "b1-m1-u1",
                                    "TranscriptionJobStatus": "COMPLETED",
                                }
                            ]
                        }
                    ),
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
                            "Transcript": "some transcript for mentor m1 and utterance u1"
                        },
                    )
                ],
                expected_result=TranscribeBatchResult(
                    transcribeJobsById={
                        "b1-m1-u1": TranscribeJob(
                            batchId="b1",
                            jobId="m1-u1",
                            sourceFile="/audio/m1/u1.wav",
                            mediaFormat="wav",
                            status=TranscribeJobStatus.SUCCEEDED,
                            transcript="some transcript for mentor m1 and utterance u1",
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
                                    status=TranscribeJobStatus.QUEUED,
                                )
                            }
                        ),
                        idsUpdated=["b1-m1-u1"],
                    ),
                    TranscribeJobsUpdate(
                        result=TranscribeBatchResult(
                            transcribeJobsById={
                                "b1-m1-u1": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u1",
                                    sourceFile="/audio/m1/u1.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.IN_PROGRESS,
                                )
                            }
                        ),
                        idsUpdated=["b1-m1-u1"],
                    ),
                    TranscribeJobsUpdate(
                        result=TranscribeBatchResult(
                            transcribeJobsById={
                                "b1-m1-u1": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u1",
                                    sourceFile="/audio/m1/u1.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.SUCCEEDED,
                                    transcript="some transcript for mentor m1 and utterance u1",
                                )
                            }
                        ),
                        idsUpdated=["b1-m1-u1"],
                    ),
                ],
            )
        )
    ],
)
def test_it_uploads_one_jobs_and_tracks_progress_until_completion(
    mock_boto3_client, fixture: TranscribeTestFixture
):
    run_transcribe_test(mock_boto3_client, fixture)
