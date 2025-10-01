import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def DiscordRequest(endpoint, options):
    print(options)
    url = 'https://discord.com/api/v10/' + endpoint

    res = requests.put(url, headers={
        'Authorization': f'Bot {os.environ.get('DISCORD_TOKEN')}',
        'User-Agent': 'DiscordBot (https://github.com/discord/discord-example-app, 1.0.0)',
    }, json=(options))

    if not res.ok:
        print(res.status_code)
        raise Exception(json.dumps(res.json()))
    
    return res

def InstallGlobalCommands(appId, commands):
    endpoint = f'applications/{appId}/commands'

    try:
        DiscordRequest(endpoint, commands)
    except Exception as e:
        print(e)
    