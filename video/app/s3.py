import os

import boto3

session = boto3.session.Session()

s3 = session.client(
    's3',
    # endpoint_url=os.environ.get("S3_ENDPOINT"),
    aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("S3_SECRET_KEY"),
    region_name=os.environ.get("S3_REGION"),
)

