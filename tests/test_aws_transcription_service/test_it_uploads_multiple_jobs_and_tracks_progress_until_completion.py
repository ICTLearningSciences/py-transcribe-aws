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
                    ),
                    TranscribeJobRequest(
                        batchId="b1", jobId="m1-u2", sourceFile="/audio/m1/u2.wav"
                    ),
                    TranscribeJobRequest(
                        batchId="b1", jobId="m1-u3", sourceFile="/audio/m1/u3.wav"
                    ),
                ],
                list_jobs_calls=[
                    AwsTranscribeListJobsCall(
                        result={
                            "TranscriptionJobSummaries": [
                                {
                                    "TranscriptionJobName": "b1-m1-u1",
                                    "TranscriptionJobStatus": "QUEUED",
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u2",
                                    "TranscriptionJobStatus": "QUEUED",
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u3",
                                    "TranscriptionJobStatus": "QUEUED",
                                },
                            ]
                        }
                    ),
                    AwsTranscribeListJobsCall(
                        result={
                            "TranscriptionJobSummaries": [
                                {
                                    "TranscriptionJobName": "b1-m1-u1",
                                    "TranscriptionJobStatus": "IN_PROGRESS",
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u2",
                                    "TranscriptionJobStatus": "QUEUED",
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u3",
                                    "TranscriptionJobStatus": "QUEUED",
                                },
                            ]
                        }
                    ),
                    AwsTranscribeListJobsCall(
                        result={
                            "TranscriptionJobSummaries": [
                                {
                                    "TranscriptionJobName": "b1-m1-u1",
                                    "TranscriptionJobStatus": "COMPLETED",
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u2",
                                    "TranscriptionJobStatus": "IN_PROGRESS",
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u3",
                                    "TranscriptionJobStatus": "IN_PROGRESS",
                                },
                            ]
                        }
                    ),
                    AwsTranscribeListJobsCall(
                        result={
                            "TranscriptionJobSummaries": [
                                {
                                    "TranscriptionJobName": "b1-m1-u1",
                                    "TranscriptionJobStatus": "COMPLETED",
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u2",
                                    "TranscriptionJobStatus": "IN_PROGRESS",
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u3",
                                    "TranscriptionJobStatus": "COMPLETED",
                                },
                            ]
                        }
                    ),
                    AwsTranscribeListJobsCall(
                        result={
                            "TranscriptionJobSummaries": [
                                {
                                    "TranscriptionJobName": "b1-m1-u1",
                                    "TranscriptionJobStatus": "COMPLETED",
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u2",
                                    "TranscriptionJobStatus": "COMPLETED",
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u3",
                                    "TranscriptionJobStatus": "COMPLETED",
                                },
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
                    ),
                    AwsTranscribeGetJobCall(
                        name="b1-m1-u3",
                        result={
                            "TranscriptionJob": {
                                "TranscriptionJobStatus": "COMPLETED",
                                "Transcript": {
                                    "TranscriptFileUri": "http://fake/b1-m1-u3"
                                },
                            }
                        },
                        transcribe_url_response={
                            "Transcript": "out of order transcript for mentor m1 and utterance u3"
                        },
                    ),
                    AwsTranscribeGetJobCall(
                        name="b1-m1-u2",
                        result={
                            "TranscriptionJob": {
                                "TranscriptionJobStatus": "COMPLETED",
                                "Transcript": {
                                    "TranscriptFileUri": "http://fake/b1-m1-u2"
                                },
                            }
                        },
                        transcribe_url_response={
                            "Transcript": "last transcript for mentor m1 and utterance u2"
                        },
                    ),
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
                        ),
                        "b1-m1-u2": TranscribeJob(
                            batchId="b1",
                            jobId="m1-u2",
                            sourceFile="/audio/m1/u2.wav",
                            mediaFormat="wav",
                            status=TranscribeJobStatus.SUCCEEDED,
                            transcript="last transcript for mentor m1 and utterance u2",
                        ),
                        "b1-m1-u3": TranscribeJob(
                            batchId="b1",
                            jobId="m1-u3",
                            sourceFile="/audio/m1/u3.wav",
                            mediaFormat="wav",
                            status=TranscribeJobStatus.SUCCEEDED,
                            transcript="out of order transcript for mentor m1 and utterance u3",
                        ),
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
                                ),
                                "b1-m1-u2": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u2",
                                    sourceFile="/audio/m1/u2.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.QUEUED,
                                ),
                                "b1-m1-u3": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u3",
                                    sourceFile="/audio/m1/u3.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.QUEUED,
                                ),
                            }
                        ),
                        idsUpdated=["b1-m1-u1", "b1-m1-u2", "b1-m1-u3"],
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
                                ),
                                "b1-m1-u2": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u2",
                                    sourceFile="/audio/m1/u2.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.QUEUED,
                                ),
                                "b1-m1-u3": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u3",
                                    sourceFile="/audio/m1/u3.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.QUEUED,
                                ),
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
                                ),
                                "b1-m1-u2": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u2",
                                    sourceFile="/audio/m1/u2.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.IN_PROGRESS,
                                ),
                                "b1-m1-u3": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u3",
                                    sourceFile="/audio/m1/u3.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.IN_PROGRESS,
                                ),
                            }
                        ),
                        idsUpdated=["b1-m1-u1", "b1-m1-u2", "b1-m1-u3"],
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
                                ),
                                "b1-m1-u2": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u2",
                                    sourceFile="/audio/m1/u2.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.IN_PROGRESS,
                                ),
                                "b1-m1-u3": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u3",
                                    sourceFile="/audio/m1/u3.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.SUCCEEDED,
                                    transcript="out of order transcript for mentor m1 and utterance u3",
                                ),
                            }
                        ),
                        idsUpdated=["b1-m1-u3"],
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
                                ),
                                "b1-m1-u2": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u2",
                                    sourceFile="/audio/m1/u2.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.SUCCEEDED,
                                    transcript="last transcript for mentor m1 and utterance u2",
                                ),
                                "b1-m1-u3": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u3",
                                    sourceFile="/audio/m1/u3.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.SUCCEEDED,
                                    transcript="out of order transcript for mentor m1 and utterance u3",
                                ),
                            }
                        ),
                        idsUpdated=["b1-m1-u2"],
                    ),
                ],
            )
        )
    ],
)
def test_it_uploads_multiple_jobs_and_tracks_progress_until_completion(
    mock_boto3_client, fixture: TranscribeTestFixture
):
    run_transcribe_test(mock_boto3_client, fixture)
