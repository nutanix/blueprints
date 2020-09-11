ACCESS_KEY = '@@{cred_aws.username}@@'
SECRET_KEY = '@@{cred_aws.secret}@@'
AWS_REGION = '@@{clusters_geolocation}@@'

import boto3

boto3.setup_default_session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

client = boto3.client('ec2')
response = client.describe_instances()
print(response)