import os
import json
import boto3
from botocore.exceptions import ClientError
import awsgi
from flask import Flask, jsonify, request, abort
from discord_interactions import verify_key_decorator, InteractionType, InteractionResponseType, InteractionResponseFlags

import time

PUBLIC_KEY = os.environ.get('APPLICATION_PUBLIC_KEY')
S3_BUCKET = os.environ.get('S3_BUCKET')
OBJECT_KEY = os.environ.get('OBJECT_KEY')
INSTANCE_ID = os.environ.get('INSTANCE_ID')

start_time = time.time()
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')
end_time = time.time()
print('time:', end_time - start_time)

app = Flask(__name__)

@app.route('/interactions', methods=['POST'])
@verify_key_decorator(PUBLIC_KEY)
def interactions():
    data = request.json
    if data['type'] == InteractionType.APPLICATION_COMMAND:
        ec2_status = ec2_client.describe_instance_status(
                        InstanceIds=[ INSTANCE_ID ],
                        IncludeAllInstances=True
                    )
        instance_state = ec2_status['InstanceStatuses'][0]['InstanceState']['Name']
        print(instance_state)

        if data['data']['name'] == 'status':
            return jsonify({
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': f'Instance\'s current status is {instance_state}'
                }
            })
        
        if instance_state in ['running', 'stopped']:
            if data['data']['name'] == 'start':
                try:
                    response_s3 = s3_client.put_object(Bucket=S3_BUCKET, Key=OBJECT_KEY, Body=json.dumps(data))
                    print('response from s3', response_s3)
                    response_ec2 = ec2_client.start_instances(
                        InstanceIds=[ INSTANCE_ID ]
                    )
                    print('response from ec2:', response_ec2)
                    return jsonify({
                        'type': InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE,
                    })
                except ClientError as e:
                    print('error:', e)
                    abort(401, 'failed to start instance')

            if data['data']['name'] == 'stop':
                try:
                    response_s3 = s3_client.put_object(Bucket=S3_BUCKET, Key=OBJECT_KEY, Body=json.dumps(data))
                    print('response from s3', response_s3)
                    response_ec2 = ec2_client.stop_instances(
                        InstanceIds=[ INSTANCE_ID ]
                    )
                    print('response from ec2:', response_ec2)
                    return jsonify({
                        'type': InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE,
                    })
                except ClientError as e:
                    print('error:', e)
                    abort(401, 'failed to start instance')
        else:
            return jsonify({
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': f'Instance is {instance_state}'
                }
            })
        
        print(f'unknown command: {data['data']['name']}')
        abort(401, 'unknown command')

    print('unknown interaction type', data['type'])
    abort(401, 'unknown interaction type')

def lambda_handler(event, context):
    return awsgi.response(app, event, context)
