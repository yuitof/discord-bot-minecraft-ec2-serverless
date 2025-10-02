import boto3

INSTANCE_ID = 'i-0e7c09e4002429fb0'

ec2_client = boto3.client('ec2')
response = ec2_client.describe_instances(
                InstanceIds=[ INSTANCE_ID ],
            )
print(response)
print()