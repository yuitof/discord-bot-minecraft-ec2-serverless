import os
import awsgi
from flask import Flask, jsonify, request, abort
from discord_interactions import verify_key_decorator, InteractionType, InteractionResponseType, InteractionResponseFlags

PUBLIC_KEY = os.environ.get('APPLICATION_PUBLIC_KEY')

app = Flask(__name__)

@app.route('/interactions', methods=['POST'])
@verify_key_decorator(PUBLIC_KEY)
def interactions():
    type = request.json['type']
    data = request.json['data']
    if type == InteractionType.APPLICATION_COMMAND:
        if data['name'] == 'test':
            return jsonify({
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': 'Hello world'
                }
            })
        print(f'unknown command: {data['name']}')
        abort(401, 'unknown command')

    print('unknown interaction type', type)
    abort(401, 'unknown interaction type')

def lambda_handler(event, context):
    return awsgi.response(app, event, context)
