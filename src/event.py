import os
import json
import boto3
from botocore.exceptions import ClientError

S3_BUCKET = os.environ.get('S3_BUCKET')
OBJECT_KEY = os.environ.get('OBJECT_KEY')
INSTANCE_ID = os.environ.get('INSTANCE_ID')

def lambda_handler(event, context):
    
    s3_client = boto3.client('s3')
    ec2_client = boto3.client('ec2')
    
    # if ec2_client.describe_instance_status(InstanceIds=[ INSTANCE_ID ]) != 'running':
    try:
        response = s3_client.put_object(Bucket=S3_BUCKET, Key=OBJECT_KEY, Body=json.dumps(event))
        print('response from s3', response)
    except ClientError as e:
        print('error:', e)

    try:
        response = ec2_client.start_instances(
            InstanceIds=[ INSTANCE_ID ]
        )
        print('response from ec2:', response)
    except ClientError as e:
        print('error:', e)
    return None