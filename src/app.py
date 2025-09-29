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
# REGION = os.environ.get("REGION")

app = Flask(__name__)

@app.route('/interactions', methods=['POST'])
@verify_key_decorator(PUBLIC_KEY)
def interactions():
    # print(request.json)
    data = request.json
    if data['type'] == InteractionType.APPLICATION_COMMAND:
        if data['data']['name'] == 'foo':
            return jsonify({
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': 'Hello world'
                }
            })
        if data['data']['name'] == 'test':
            s3_client = boto3.client('s3')
            try:
                response = s3_client.put_object(Bucket=S3_BUCKET, Key=OBJECT_KEY, Body=json.dumps(data))
                print('response from s3', response)
            except ClientError as e:
                print('error:', e)
            
            ec2_client = boto3.client('ec2')
            try:
                response = ec2_client.start_instances(
                    InstanceIds=[ INSTANCE_ID ]
                )
                print('response from ec2:', response)
            except ClientError as e:
                print('error:', e)

            return jsonify({
                'type': InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE,
            })
        
        print(f'unknown command: {data['name']}')
        abort(401, 'unknown command')

    print('unknown interaction type', type)
    abort(401, 'unknown interaction type')

def lambda_handler(event, context):
    return awsgi.response(app, event, context)
