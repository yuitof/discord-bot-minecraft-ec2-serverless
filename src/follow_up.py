import os
import json
import requests
import boto3
from botocore.exceptions import ClientError

S3_BUCKET = os.environ.get('S3_BUCKET')
OBJECT_KEY = os.environ.get('OBJECT_KEY')

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=OBJECT_KEY)
        content = response["Body"].read().decode('utf-8')
        data = json.loads(content)
        print('received data:', data)
        url = f'https://discord.com/api/v10/webhooks/{data["application_id"]}/{data["token"]}/messages/@original'
        body = { "content": "✅ Done processing your request" }
        requests.patch(url, json=body)
    except ClientError as e:
        print('error:', e)
