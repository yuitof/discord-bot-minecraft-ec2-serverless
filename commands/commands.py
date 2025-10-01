import os
from dotenv import load_dotenv
from utils import InstallGlobalCommands
load_dotenv()

START_COMMAND = {
    'name': 'start',
    'description': 'Start instance',
    'type': 1,
    'integration_types': [0, 1],
    'contexts': [0, 1, 2],
}

STOP_COMMAND = {
    'name': 'stop',
    'description': 'Stop instance',
    'type': 1,
    'integration_types': [0, 1],
    'contexts': [0, 1, 2],
}

STATUS_COMMAND ={
    'name': 'status',
    'description': 'Get instance\'s current status',
    'type': 1,
    'integration_types': [0, 1],
    'contexts': [0, 1, 2],
}

ALL_COMMANDS = [START_COMMAND, STOP_COMMAND, STATUS_COMMAND]

InstallGlobalCommands(os.environ.get('APP_ID'), ALL_COMMANDS)