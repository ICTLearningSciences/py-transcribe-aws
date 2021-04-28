#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import logging
import requests
import os
import re
from typing import Any, Callable, Dict, Iterable, List, Optional
import time

import boto3

from botocore.exceptions import ClientError
from boto3_type_annotations.s3 import Client as S3Client
from boto3_type_annotations.transcribe import Client as TranscribeClient

from transcribe import (
    copy_shallow,
    requests_to_job_batch,
    require_env,
    register_transcription_service_factory,
    TranscribeBatchResult,
    TranscribeJob,
    TranscribeJobRequest,
    TranscribeJobsUpdate,
    TranscribeJobStatus,
    TranscriptionService,
)

_TRANSCRIBE_JOB_STATUS_BY_AWS_STATUS: Dict[str, TranscribeJobStatus] = {
    "QUEUED": TranscribeJobStatus.QUEUED,
    "IN_PROGRESS": TranscribeJobStatus.IN_PROGRESS,
    "FAILED": TranscribeJobStatus.FAILED,
    "COMPLETED": TranscribeJobStatus.SUCCEEDED,
}

DEFAULT_POLL_INTERVAL: float = 5.0


def _create_s3_client(
    aws_access_key_id: str = "", aws_secret_access_key: str = "", aws_region: str = ""
) -> S3Client:
    return boto3.client(
        "s3",
        region_name=require_env("AWS_REGION", aws_region),
        aws_access_key_id=require_env("AWS_ACCESS_KEY_ID", aws_access_key_id),
        aws_secret_access_key=require_env(
            "AWS_SECRET_ACCESS_KEY", aws_secret_access_key
        ),
    )


def _create_transcribe_client(
    aws_access_key_id: str = "", aws_secret_access_key: str = "", aws_region: str = ""
) -> TranscribeClient:
    return boto3.client(
        "transcribe",
        region_name=require_env("AWS_REGION", aws_region),
        aws_access_key_id=require_env("AWS_ACCESS_KEY_ID", aws_access_key_id),
        aws_secret_access_key=require_env(
            "AWS_SECRET_ACCESS_KEY", aws_secret_access_key
        ),
    )


def _parse_aws_status(
    aws_status: str, default_status: TranscribeJobStatus = TranscribeJobStatus.NONE
) -> TranscribeJobStatus:
    return _TRANSCRIBE_JOB_STATUS_BY_AWS_STATUS.get(aws_status, default_status)


def _s3_file_exists(s3: S3Client, bucket: str, key: str) -> bool:
    try:
        s3.head_object(Bucket=bucket, Key=key)
    except ClientError as e:
        logging.error(e)
        return int(e.response["Error"]["Code"]) != 404
    return True


class AWSTranscriptionService(TranscriptionService):
    def _get_batch_status(self, batch_id: str) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        cur_result_page = self.transcribe_client.list_transcription_jobs(
            JobNameContains=batch_id
        )
        while True:
            cur_result_summaries: List[Dict[str, Any]] = cur_result_page.get(
                "TranscriptionJobSummaries"
            )
            for r in cur_result_summaries:
                result.append(r)
            next_token = cur_result_page.get("NextToken", "")
            if not next_token:
                break
            cur_result_page = self.transcribe_client.list_transcription_jobs(
                JobNameContains=batch_id, NextToken=next_token
            )
        return result

    def _load_transcript(self, aws_job_name: str) -> str:
        aws_job = self.transcribe_client.get_transcription_job(
            TranscriptionJobName=aws_job_name
        )
        url = (
            aws_job.get("TranscriptionJob", {})
            .get("Transcript", {})
            .get("TranscriptFileUri", "")
        )
        if not url:
            raise Exception(f"unable to parse url for job '{aws_job_name}': {aws_job}")
        transcript_res = requests.get(url)
        transcript_res.raise_for_status()
        transcript_json = transcript_res.json()
        try:
            return transcript_json["results"]["transcripts"][0]["transcript"]
        except Exception:
            raise Exception(
                f"unable to parse transcript for job '{aws_job_name} and url {url}': {transcript_json}"
            )

    def get_s3_path(self, source_file: str, id: str) -> str:
        file_name = f"{id.lower()}{os.path.splitext(source_file)[1]}"
        return f"{self.s3_root_path}/{file_name}" if self.s3_root_path else file_name

    def init_service(self, config: Dict[str, Any] = {}, **kwargs):
        self.aws_region = config.get("AWS_REGION") or require_env("AWS_REGION")
        self.s3_bucket_source = config.get(
            "TRANSCRIBE_AWS_S3_BUCKET_SOURCE"
        ) or require_env("TRANSCRIBE_AWS_S3_BUCKET_SOURCE")
        self.s3_root_path = config.get(
            "TRANSCRIBE_AWS_S3_ROOT_PATH",
            os.environ.get("TRANSCRIBE_AWS_S3_ROOT_PATH", ""),
        )
        aws_access_key_id = config.get("AWS_ACCESS_KEY_ID") or require_env(
            "AWS_ACCESS_KEY_ID"
        )
        aws_secret_access_key = config.get("AWS_SECRET_ACCESS_KEY") or require_env(
            "AWS_SECRET_ACCESS_KEY"
        )
        self.s3_client = _create_s3_client(
            aws_region=self.aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.transcribe_client = _create_transcribe_client(
            aws_region=self.aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.poll_interval = config.get("POLL_INTERVAL", DEFAULT_POLL_INTERVAL)

    def transcribe(
        self,
        transcribe_requests: Iterable[TranscribeJobRequest],
        batch_id: str = "",
        on_update: Optional[Callable[[TranscribeJobsUpdate], None]] = None,
        **kwargs,
    ) -> TranscribeBatchResult:
        logging.info(f"transcribe: assigning batch id {batch_id} to all jobs")
        result = TranscribeBatchResult(
            transcribeJobsById={
                j.get_fq_id(): j
                for j in requests_to_job_batch(batch_id, transcribe_requests)
            }
        )
        for i, job in enumerate(result.jobs()):
            result = self._upload_one(job, i, result, on_update)
            result = self._try_ensure_all_jobs_started(result, batch_id, on_update)
        while result.has_any_unresolved():
            if self.poll_interval > 0:
                time.sleep(self.poll_interval)
            result = self._try_ensure_all_jobs_started(result, batch_id, on_update)
            result = self._update_status(result, batch_id, on_update)
        return result

    def _send_on_update(
        self,
        result: TranscribeBatchResult,
        ids_updated: List[str],
        on_update: Optional[Callable[[TranscribeJobsUpdate], None]],
    ):
        if on_update and len(ids_updated) > 0:
            assert on_update is not None
            try:
                on_update(
                    TranscribeJobsUpdate(result=result, idsUpdated=sorted(ids_updated))
                )
            except Exception as ex:
                logging.exception(f"update handler raise exception: {ex}")
        return result

    def _try_ensure_all_jobs_started(
        self,
        result: TranscribeBatchResult,
        batch_id: str,
        on_update: Optional[Callable[[TranscribeJobsUpdate], None]],
    ):
        if not any(j.status == TranscribeJobStatus.UPLOADED for j in result.jobs()):
            return result
        result = copy_shallow(result)
        job_ids_started = []
        try:
            for job in result.jobs():
                if job.status != TranscribeJobStatus.UPLOADED:
                    continue
                jid = job.get_fq_id()
                item_s3_path = self.get_s3_path(job.sourceFile, jid)
                self.transcribe_client.start_transcription_job(
                    TranscriptionJobName=jid,
                    LanguageCode=job.languageCode,
                    Media={
                        "MediaFileUri": f"https://s3.{self.aws_region}.amazonaws.com/{self.s3_bucket_source}/{item_s3_path}"
                    },
                    MediaFormat=job.mediaFormat,
                )
                result.update_job(jid, status=TranscribeJobStatus.QUEUED)
                job_ids_started.append(jid)
        except BaseException as ex:
            if re.search("limitexceeded", str(ex), re.IGNORECASE):
                logging.info(
                    "received a limit-exceeded response from aws. Will try again to start this job shortly"
                )
            else:
                logging.exception(f"exception on start jobs: {ex}")
        if job_ids_started:
            self._send_on_update(result, job_ids_started, on_update)
        return result

    def _update_status(
        self,
        result: TranscribeBatchResult,
        batch_id: str,
        on_update: Optional[Callable[[TranscribeJobsUpdate], None]],
    ) -> TranscribeBatchResult:
        job_updates = self._get_batch_status(batch_id)
        ids_updated: List[str] = []
        result = copy_shallow(result)
        for ju in job_updates:
            try:
                jid = ju.get("TranscriptionJobName", "")
                jstatus = _parse_aws_status(
                    ju.get("TranscriptionJobStatus", ""),
                    default_status=TranscribeJobStatus.NONE,
                )
                if jstatus == TranscribeJobStatus.NONE:
                    raise ValueError(
                        f"job status has unknown value of {ju.get('TranscriptionJobStatus')}"
                    )
                if result.job_completed(jid, jstatus):
                    continue
                transcript = (
                    self._load_transcript(jid)
                    if jstatus == TranscribeJobStatus.SUCCEEDED
                    else ""
                )
                if result.update_job(jid, status=jstatus, transcript=transcript):
                    ids_updated.append(jid)
            except Exception as ex:
                logging.exception(f"failed to handle update for {ju}: {ex}")
        summary = result.summary()
        logging.info(
            f"transcribe [{summary.get_count_completed()}/{summary.get_count_total()}] completed. Statuses [SUCCEEDED: {summary.get_count(TranscribeJobStatus.SUCCEEDED)}, FAILED: {summary.get_count(TranscribeJobStatus.FAILED)}, QUEUED: {summary.get_count(TranscribeJobStatus.QUEUED)}, IN_PROGRESS: {summary.get_count(TranscribeJobStatus.IN_PROGRESS)}]."
        )
        self._send_on_update(result, ids_updated, on_update)
        return result

    def _upload_one(
        self,
        job: TranscribeJob,
        job_index: int,
        result: TranscribeBatchResult,
        on_update: Optional[Callable[[TranscribeJobsUpdate], None]],
    ) -> TranscribeBatchResult:
        jid = job.get_fq_id()
        result = copy_shallow(result)
        item_s3_path = self.get_s3_path(job.sourceFile, jid)
        logging.info(
            f"transcribe [{job_index + 1}/{len(result.transcribeJobsById)}] uploading audio to s3 bucket {self.s3_bucket_source} and path {item_s3_path}"
        )
        self.s3_client.upload_file(
            job.sourceFile,
            self.s3_bucket_source,
            item_s3_path,
            ExtraArgs={"ACL": "public-read"},
        )
        result = copy_shallow(result)
        result.update_job(jid, status=TranscribeJobStatus.UPLOADED)
        self._send_on_update(result, [jid], on_update)
        return result


register_transcription_service_factory("transcribe_aws", AWSTranscriptionService)
