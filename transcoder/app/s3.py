import os

import boto3

# Check environment
ENV = os.environ.get("ENV", "development")  # default to "development"

# Base session
session = boto3.session.Session()

# Common kwargs
s3_kwargs = {
    # "endpoint_url": os.environ.get("S3_ENDPOINT"),
    "aws_access_key_id": os.environ.get("S3_ACCESS_KEY"),
    "aws_secret_access_key": os.environ.get("S3_SECRET_KEY"),
}

# Add endpoint_url in development only
if ENV == "development":
    s3_kwargs["endpoint_url"] = os.environ.get("S3_ENDPOINT")
else:
    s3_kwargs["region_name"] = os.environ.get("S3_REGION", "us-east-1")

# Create the client
s3 = session.client("s3", **s3_kwargs)
