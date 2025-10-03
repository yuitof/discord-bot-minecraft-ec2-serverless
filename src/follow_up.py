import os
import json
import requests
import boto3
from botocore.exceptions import ClientError

INSTANCE_ID = os.environ.get('INSTANCE_ID')
S3_BUCKET = os.environ.get('S3_BUCKET')
OBJECT_KEY = os.environ.get('OBJECT_KEY')

ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=OBJECT_KEY)
        content = response["Body"].read().decode('utf-8')
        data = json.loads(content)
        print('received data:', data)

        if data['data']['name'] == 'start':
            try:
                response = ec2_client.describe_instances(
                    InstanceIds=[ INSTANCE_ID ],
                )
                print(response)
                address = response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['Association']['PublicDnsName']
                url = f'https://discord.com/api/v10/webhooks/{data["application_id"]}/{data["token"]}/messages/@original'
                body = { "content": f"✅ Instance is running\nAddress: {address}" }
                requests.patch(url, json=body)
            except ClientError as e:
                print('error:', e)
        if data['data']['name'] == 'stop':
            url = f'https://discord.com/api/v10/webhooks/{data["application_id"]}/{data["token"]}/messages/@original'
            body = { "content": "✅ Instance stopped" }
            requests.patch(url, json=body)
    except ClientError as e:
        print('error:', e)
    finally:
        response = s3_client.delete_object(Bucket=S3_BUCKET, Key=OBJECT_KEY)
        print(response)
    return None
