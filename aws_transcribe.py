from __future__ import print_function
import time
import boto3
from uuid import uuid1
print("HERE IN TEST!")
transcribe = boto3.client('transcribe')
job_name = f"test_api_{uuid1()}"
job_uri = "https://s3.us-east-2.amazonaws.com/mentorpal-videos/videos/mentors/mario-pais/mobile/s001p006s00021220e00032010.mp4"
transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': job_uri},
    MediaFormat='mp4',
    LanguageCode='en-US',
)
while True:
    status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break
    print("Not ready yet...")
    time.sleep(5)
print(status)
