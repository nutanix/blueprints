'''Filter instances based on tag name and value'''
ACCESS_KEY = '@@{cred_aws.username}@@'
SECRET_KEY = '@@{cred_aws.secret}@@'
AWS_REGION = '@@{clusters_geolocation}@@'
TAG_KEY = '@@{tag_name}@@'
TAG_VALUE =  '@@{tag_value}@@'

import boto3

boto3.setup_default_session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

client = boto3.client('ec2')

try:
    response = client.describe_instances(Filters=[{'Name': 'tag:'+TAG_KEY, 'Values': [ TAG_VALUE ]}])

    if response['Reservations']:
        print('Matching instance(s) with "{}" tag, and "{}" value:'.format(TAG_KEY, TAG_VALUE))
        for i in response['Reservations']:
            print(i['Instances'][0]['InstanceId'])
    else:
        print('No matching instances with "{}" tag and "{}" value'.format(TAG_KEY, TAG_VALUE))
except ClientError as e:
    print(e)
