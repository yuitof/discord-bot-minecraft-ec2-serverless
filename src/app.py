import os
import json
import boto3
from botocore.exceptions import ClientError
import awsgi
from flask import Flask, jsonify, request, abort
from discord_interactions import verify_key_decorator, InteractionType, InteractionResponseType, InteractionResponseFlags

import time

PUBLIC_KEY = os.environ.get('APPLICATION_PUBLIC_KEY')
# REGION = os.environ.get("REGION")

start_time = time.time()
lambda_client = boto3.client('lambda')
end_time = time.time()
print('time:', end_time - start_time)

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

            start_time = time.time()
            lambda_client.invoke(
                FunctionName='discord-bot-minecraft-ec2-serverless-EventFunction-PEgLs8UrEwSj',
                InvocationType='Event',
                Payload=json.dumps(data)
            )
            end_time = time.time()
            print('time:', end_time - start_time)

            return jsonify({
                'type': InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE,
            })
            # else:
                # return jsonify({
                #     'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                #     'data': {
                #         'content': 'Instance is running'
                #     }
                # })
        
        print(f'unknown command: {data['name']}')
        abort(401, 'unknown command')

    print('unknown interaction type', type)
    abort(401, 'unknown interaction type')

def lambda_handler(event, context):
    return awsgi.response(app, event, context)
