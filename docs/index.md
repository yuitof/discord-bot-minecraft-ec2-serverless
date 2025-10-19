## Discord bot for Minecraft on AWS 

### Index
1. Introduction
    1. Self introduction
    2. What to do?

2. Getting started
    1. Prerequisite for AWS
    2. Your first lambda function

3. Discord API
    1. Discord application
    2. Register commands

4. Implementation
    1. Create Lambda function
    2. Configure Cloudformation
    3. Docker Minecraft Server

4. Summary

## Outline

### Introduction
#### Self introduction

My name is Yuito Fujiwara, an undergard at Keio University.
Feel free to get in touch via email or DMs on social media. I put the link below.

The source code of this project is available on https://github.com/yuitof/discord-bot-minecraft-ec2-serverless. Please reference if you would like. 

Website: https://www.yuitof.com, X: @yuito_fujiwara, GitHub: @yuitof, Email: mail@yuitof.com

#### What to do?

I assume that you may have come accross the cases where you and a friend are playing Minecraft. Because its server is running on their computer, you can't play if not they keep the PC running. It's not satisfying.

By creating a Minecraft server on AWS and enable us to start and stop it from Discord, even if a friend can't join, you can play Minecraft, vice versa.

AWS is the shorthand for Amazon Web Services, one of the cloud computing services. It provide enterprise-level computing resources and infrastructure. Discord is a chat application. Gamers tend to prefer it.  

### Gettings started
In this tutorial, I'll walk you though the set-up procedure and deployment to AWS Lamnda.

Here is the structure of the project.

```
.
├── __init__.py
├── commands
│   ├── __pycache__
│   │   └── utils.cpython-312.pyc
│   ├── commands.py
│   └── utils.py
├── events
│   └── event.json
├── LICENSE
├── README.md
├── requirements.txt
├── samconfig.toml
├── src
│   ├── __init__.py
│   ├── app.py
│   ├── follow_up.py
│   ├── modules
│   └── requirements.txt
├── template.yaml
└── tests
    ├── __init__.py
    ├── integration
    │   ├── __init__.py
    │   └── test_api_gateway.py
    ├── requirements.txt
    └── unit
        ├── __init__.py
        └── test_handler.py
```


#### Prerequisite

Sign up for an AWS account. Consult this page if necessary: https://docs.aws.amazon.com/accounts/latest/reference/accounts-welcome.html) Keep in mind that Amazon accounts that you may use for online shopping are completely separated from AWS accounts. Therefore, even if you already have an Amazon account, you need to create an AWS account. In addition, I recently realized that AWS added another type of account named AWS Builder ID. It is just for learning purposes. You don't need to create one at this time.

Install AWS CLI, AWS SAM CLI, and Docker to your local computer. To sign in AWS account, execute the command below and sign in the account you created earlier.
```
aws configure
```
AWS SAM is an abbreviation for Serverless Application Model. It provide a suite of tools that is useful when building serverless applications.

##### Pitfall
> If you are using MacOS, you might want to install AWS SAM CLI with Homebrew. Unfortunately AWS no longer maintain the Homebrew installer for AWS SAM CLI. It is desirable to follow the process introduced on the official documents. (cf: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)

#### Your first lambda function
This section explains the same things as the  official document. Although I'm going to try to unpack things that are not introduced therev as much as possible, I recommend to you referencing to the source (https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started-hello-world.html).
Lambda is a serverless runtime provided by AWS. Serverless runtime only runs when specific events calls them. Therefore, you don't need to much money if the traffic is low because the cost is charged depending on how many times functions are called and how long they take. To create a scaffold of our application, let's execute the initialization command.

```
sam init
```

Choose a template you want to use. In this tutorial, I adopt Hello World Example.

After the scaffold are created, execute this command.
```
sam build
sam deploy
```
By executing these commands, you can deploy the application according to the configuration files—samconfig.toml and template.yaml.
samconfig.toml has the settings for deployment and template.yaml is a setting file for AWS CloudFormation. I'll explain these later.

If you access the API Gateway endpoint URL and see "Hello World", it succeeded.

##### Recap
We made it to deploy an application to Lamnda.

### Discord API 
#### Discord application
First of all, let me briefly explain the specification of the Discord API and tell you the concept of our application.
Discord now provides webhooks. The applications send outgoing http requests under the hood only when registered events occur, enabling Discord applications to run on the serverless environment. Before that, you have to keep application running to observe events being called. Although it is a innovative features, it has certain requirements. First, responses have to be returned within 3 seconds after the Discord application has sent http requests. Second, if a request's type is 1, you also need to return a response with type 1, which can be done with a library(https://github.com/discord/discord-interactions-python).

Visit this site(https://discord.com/developers/applications), create a new application, and save its application id, public key and token. The application id and token are used when registering commands and the public key when sending responses.

For more detail, reference to the official document(https://discord.com/developers/docs/quick-start/getting-started)

#### Register commands
To use commands via Discord applications, we have to register the commands beforehand. Make the commands folder and create commands.py and utils.py  the under it. AWS SAM provides execution environment using Docker containers and manual creation of virtual environments isn't necessary. On the other hand, as I mentioned before, when it comes to the registration, you have to manually create virtual environment(recommended) and install dependencies.


```python title="commands.py
from utils import InstallGlobalCommands

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

if __name__ == __main__:
    InstallGlobalCommands(os.environ.get('APP_ID'), ALL_COMMANDS)
```

```python title='utils.py'
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
```
Make sure to create a file named .env and set the environment variables as follows.
```
APP_ID=123456789
DISCORD_TOKEN=abcdefghijklmnopqrstuvwxyz
```

Finally, try executing commands.py
```shell
python ./commands/commands.py
```

### Implementation
#### Create Lambda functions
I'm going to create a function returns responses and invokes ec2 instance.

Here is a minimal prototype.
```python title="app.py"
import awsgi
from flask import Flask, jsonify, request, abort
from discord_interactions import verify_key_decorator, InteractionType, InteractionResponseType, InteractionResponseFlags

PUBLIC_KEY = os.environ.get('APPLICATION_PUBLIC_KEY')

app = Flask(__name__)

@app.route('/interactions', methods=['POST'])
@verify_key_decorator(PUBLIC_KEY)
def interactions():
    return jsonify({
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'content': 'Hello World!'
            }
        })

def lambda_handler(event, context):
    return awsgi.response(app, event, context)
```
I'm using Flask for routing. AWSGI makes Flask run on Lamda.

#### Configure CloudFormation
```yaml title=template.yaml
Globals:
  Function:
    Timeout: 15
    Environment:
        Variables:
          APPLICATION_PUBLIC_KEY: your_public_key
          REGION: us-west-1

Resources:
  InteractionFunction:
    Type: AWS::Serverless::Function # More info about Function Resource: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Properties:
      CodeUri: src/
      Handler: app.lambda_handler
      Runtime: python3.13
      Architectures:
        - x86_64
      MemorySize: 1024
      Events:
        Interaction:
          Type: Api # More info about API Event Source: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api
          Properties:
            Path: /interactions
            Method: post
 ```
Set the application's public key as an environment variables because we'll use it later.

#### Docker Minecraft server
First of all, create EC2 insatce

```yaml title=template.yaml
Ec2Instance:
    Type : AWS::EC2::Instance
    Properties:
      ImageId: ami-00142eb1747a493d9
      InstanceType: t2.small
      SecurityGroupIds:
        - !Ref InstanceSecurityGroup
      Tags:
        - Key: Name
          Value: discord-bot-minecraft-ec2-serverless
  InstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Enable SSH access via port 22
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 25565
          ToPort: 25565
          CidrIp: 0.0.0.0/0
        - IpProtocol: udp
          FromPort: 25565
          ToPort: 25565
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: discord-bot-minecraft-ec2-serverless
```

We also need to give lambda functions permissions to invoke the instance. Add these code under the function setting.

InteractionFunction
```yaml template.yaml
Policies:
    - Statement:
        - Effect: Allow
        Action:
            - ec2:StopInstances
            - ec2:StartInstances
            - ec2:DescribeInstanceStatus
        Resource: "*"
```

Next, let's make the interactions function invoke the EC2 instace we've created. 
Tweak app.py by editing interactions function

Boto3 is a python library to access AWS services. You don't need to extra authentication if you have already signed in AWS CLI and it also works without authentication on Lambda functions.

Install boto3 to your project and import boto3. ClientError is a error class defined by boto3 namespace.

```python title="app.py"
INSTANCE_ID = os.environ.get('INSTANCE_ID')
S3_BUCKET = os.environ.get('S3_BUCKET')
OBJECT_KEY = os.environ.get('OBJECT_KEY')

ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')

def interactions():
    data = request.json
    if data['type'] == InteractionType.APPLICATION_COMMAND:
        ec2_status = ec2_client.describe_instance_status(
                        InstanceIds=[ INSTANCE_ID ],
                        IncludeAllInstances=True
                    )
        instance_state = ec2_status['InstanceStatuses'][0]['InstanceState']['Name']
        print(instance_state)

        if data['data']['name'] in ['status', 'start', 'stop']:

            if data['data']['name'] == 'status':
                return jsonify({
                    'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    'data': {
                        'content': f'Instance is {instance_state}'
                    }
                })

            if data['data']['name'] == 'start' and instance_state == 'stopped':
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

            if data['data']['name'] == 'stop' and instance_state == 'running':
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
                    abort(401, 'failed to stop instance')
        
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
```
```yaml title="template.yaml"
OBJECT_KEY: tmp.json
INSTANCE_ID: !Ref Ec2Instance
```
I use this docker image.

https://hub.docker.com/r/itzg/minecraft-server

Since Amazon Linux doesn't have a pakcage manager providing Docker by default. You need to add the package manager for CentOS. This Q&A in the AWS forum is helpful.

https://repost.aws/questions/QU1jeKaTRYQ7WeA7XobfP21g/how-do-i-install-docker-version-27-3-1-on-amazon-linux-2023

Add the following code to as an attribute of Ec2Instance inside template.yaml. 
```yaml title="template.yaml"
UserData:
    Fn::Base64: !Sub |
        #!/bin/bash
        sudo dnf update -y
        sudo dnf remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine
        sudo dnf -y install dnf-plugins-core
        sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo sed -i 's/$releasever/9/g' /etc/yum.repos.d/docker-ce.repo
        sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        sudo systemctl enable --now docker
        sudo mkdir /mc && sudo cd /mc
        sudo echo $'services:\n  mc:\n    image: itzg/minecraft-server\n    tty: true\n    stdin_open: true\n    ports:\n      - "25565:25565"\n    environment:\n      EULA: "TRUE"\n    volumes:\n      - ./data:/data\n    restart: always' > './docker-compose.yml'
        sudo docker compose -p minecraft-server up -d
```
The code you've wrote as UserData is executed once when deploying it.

Now, we have to create a function that update the message previously sent by the interactions function
Create another file named follow_up.py under /src

```python title="follow_up.py"
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
```
We configure this function to be called when the status of the EC2 instance changes. Set the event attribute as follows.
```yaml title=template.yaml
Events:
    EC2StateChange:
        Type: EventBridgeRule
        Properties:
        Pattern:
            source: 
                - "aws.ec2"
            detail-type:
                - "EC2 Instance State-change Notification"
            detail:
                state:
                  - "running"
                  - "stopped"
```

You may have already noticed that, in order to patch the messages, their application ids and tokens are required. We must implement feature that pass these information from the interactions function to follow_up function. In this case, this application is only for personal use and multiple instances aren't planned to be created, so I've adopted AWS S3.

AWS S3 is the abbreviation for Simple Storage Service. It is famous for its stability and data integrity. We'll create a single file and save the application id and token of a request inside it.

Add the following code to template.yaml

##### Pitfall
> S3 Buckets are required to have globally unique name across all AWS accounts and region. The code below is configuring to append random letters after the bucket name. I borrow this code from a conversation on stackoverflow(cf: https://stackoverflow.com/questions/54897459/how-to-set-semi-random-name-for-s3-bucket-using-cloud-formation)

```yaml title=template.yaml
SamTempBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Join
        - "-"
        - - "sam-temp-bucket"
          - !Select
            - 0
            - !Split
              - "-"
              - !Select
                - 2
                - !Split
                  - "/"
                  - !Ref "AWS::StackId"
```
```
S3_BUCKET: !Ref SamTempBucket
```
And give permissions to both lambda functions

```yaml template.yaml
- s3:GetObject
- s3:PutObject
```

### Summary
Create a Minecraft server on AWS and enable us to invoke it from a Discord application. AWS is the shorthand for Amazon Web Services, one of the cloud computing services. 

