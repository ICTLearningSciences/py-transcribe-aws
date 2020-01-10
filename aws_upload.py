from __future__ import print_function
# import time
# import logging
# import boto3
# from botocore.exceptions import ClientError
# from boto3_type_annotations.s3 import Client as S3Client

from transcribe.aws import create_s3_client, s3_file_exists

print("HERE IN TEST!")
s3 = create_s3_client()

bucket = "mentorpal-videos"
key = "videos/mentors/mario-pais/mobile/s001p006s00021220e00032010XXX.mp4"

exists = s3_file_exists(s3, bucket, key)
print(f"exists? = {exists}")
