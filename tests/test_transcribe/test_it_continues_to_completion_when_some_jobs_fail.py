#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import pytest
from unittest.mock import patch

from transcribe import (
    TranscribeBatchResult,
    TranscribeJob,
    TranscribeJobRequest,
    TranscribeJobStatus,
    TranscribeJobsUpdate,
)

from transcribe_aws import DEFAULT_POLL_INTERVAL

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
                    TranscribeJobRequest(jobId="m1-u1", sourceFile="/audio/m1/u1.wav"),
                    TranscribeJobRequest(jobId="m1-u2", sourceFile="/audio/m1/u2.wav"),
                    TranscribeJobRequest(jobId="m1-u3", sourceFile="/audio/m1/u3.wav"),
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
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u2",
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
                                    "TranscriptionJobStatus": "FAILED",
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u2",
                                    "TranscriptionJobStatus": "IN_PROGRESS",
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
                                    "TranscriptionJobStatus": "FAILED",
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u2",
                                    "TranscriptionJobStatus": "FAILED",
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
                                    "TranscriptionJobStatus": "FAILED",
                                },
                                {
                                    "TranscriptionJobName": "b1-m1-u2",
                                    "TranscriptionJobStatus": "FAILED",
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
                            "results": {
                                "transcripts": [
                                    {
                                        "transcript": "transcript for mentor m1 and utterance u3 even though other jobs failed"
                                    }
                                ]
                            }
                        },
                    )
                ],
                expected_sleep_calls=[
                    DEFAULT_POLL_INTERVAL,
                    DEFAULT_POLL_INTERVAL,
                    DEFAULT_POLL_INTERVAL,
                ],
                expected_result=TranscribeBatchResult(
                    transcribeJobsById={
                        "b1-m1-u1": TranscribeJob(
                            batchId="b1",
                            jobId="m1-u1",
                            sourceFile="/audio/m1/u1.wav",
                            mediaFormat="wav",
                            status=TranscribeJobStatus.FAILED,
                        ),
                        "b1-m1-u2": TranscribeJob(
                            batchId="b1",
                            jobId="m1-u2",
                            sourceFile="/audio/m1/u2.wav",
                            mediaFormat="wav",
                            status=TranscribeJobStatus.FAILED,
                        ),
                        "b1-m1-u3": TranscribeJob(
                            batchId="b1",
                            jobId="m1-u3",
                            sourceFile="/audio/m1/u3.wav",
                            mediaFormat="wav",
                            status=TranscribeJobStatus.SUCCEEDED,
                            transcript="transcript for mentor m1 and utterance u3 even though other jobs failed",
                        ),
                    }
                ),
                expected_on_update_calls=[
                    TranscribeJobsUpdate(
                        idsUpdated=["b1-m1-u1"],
                        result=TranscribeBatchResult(
                            transcribeJobsById={
                                "b1-m1-u1": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u1",
                                    sourceFile="/audio/m1/u1.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.UPLOADED,
                                ),
                                "b1-m1-u2": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u2",
                                    sourceFile="/audio/m1/u2.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.NONE,
                                ),
                                "b1-m1-u3": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u3",
                                    sourceFile="/audio/m1/u3.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.NONE,
                                ),
                            }
                        ),
                    ),
                    TranscribeJobsUpdate(
                        idsUpdated=["b1-m1-u1"],
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
                                    status=TranscribeJobStatus.NONE,
                                ),
                                "b1-m1-u3": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u3",
                                    sourceFile="/audio/m1/u3.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.NONE,
                                ),
                            }
                        ),
                    ),
                    TranscribeJobsUpdate(
                        idsUpdated=["b1-m1-u2"],
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
                                    status=TranscribeJobStatus.UPLOADED,
                                ),
                                "b1-m1-u3": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u3",
                                    sourceFile="/audio/m1/u3.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.NONE,
                                ),
                            }
                        ),
                    ),
                    TranscribeJobsUpdate(
                        idsUpdated=["b1-m1-u2"],
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
                                    status=TranscribeJobStatus.NONE,
                                ),
                            }
                        ),
                    ),
                    TranscribeJobsUpdate(
                        idsUpdated=["b1-m1-u3"],
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
                                    status=TranscribeJobStatus.UPLOADED,
                                ),
                            }
                        ),
                    ),
                    TranscribeJobsUpdate(
                        idsUpdated=["b1-m1-u3"],
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
                    ),
                    TranscribeJobsUpdate(
                        idsUpdated=["b1-m1-u1", "b1-m1-u2"],
                        result=TranscribeBatchResult(
                            transcribeJobsById={
                                "b1-m1-u1": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u1",
                                    sourceFile="/audio/m1/u1.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.FAILED,
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
                                    status=TranscribeJobStatus.QUEUED,
                                ),
                            }
                        ),
                    ),
                    TranscribeJobsUpdate(
                        idsUpdated=["b1-m1-u2", "b1-m1-u3"],
                        result=TranscribeBatchResult(
                            transcribeJobsById={
                                "b1-m1-u1": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u1",
                                    sourceFile="/audio/m1/u1.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.FAILED,
                                ),
                                "b1-m1-u2": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u2",
                                    sourceFile="/audio/m1/u2.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.FAILED,
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
                    ),
                    TranscribeJobsUpdate(
                        idsUpdated=["b1-m1-u3"],
                        result=TranscribeBatchResult(
                            transcribeJobsById={
                                "b1-m1-u1": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u1",
                                    sourceFile="/audio/m1/u1.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.FAILED,
                                ),
                                "b1-m1-u2": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u2",
                                    sourceFile="/audio/m1/u2.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.FAILED,
                                ),
                                "b1-m1-u3": TranscribeJob(
                                    batchId="b1",
                                    jobId="m1-u3",
                                    sourceFile="/audio/m1/u3.wav",
                                    mediaFormat="wav",
                                    status=TranscribeJobStatus.SUCCEEDED,
                                    transcript="transcript for mentor m1 and utterance u3 even though other jobs failed",
                                ),
                            }
                        ),
                    ),
                ],
            )
        )
    ],
)
def test_it_continues_to_completion_when_some_jobs_fail(
    mock_boto3_client, fixture: TranscribeTestFixture
):
    run_transcribe_test(mock_boto3_client, fixture)
