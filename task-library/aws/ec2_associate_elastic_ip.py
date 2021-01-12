ACCESS_KEY = '@@{cred_aws.username}@@'
SECRET_KEY = '@@{cred_aws.secret}@@'
AWS_REGION = '@@{clusters_geolocation}@@'
INSTANCE_ID = '@@{ec2_instance_id}@@'

import boto3

boto3.setup_default_session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

client = boto3.client('ec2')

try:
    # Allocate elatic PublicIp
    allocation = client.allocate_address(Domain='vpc')
    print("Allocation Id: "+ allocation['AllocationId'] + " Public IP: " + allocation['PublicIp'])

    # Associate Elastic IP with an ec2 instance
    response = client.associate_address(AllocationId=allocation['AllocationId'],
                                     InstanceId=INSTANCE_ID)
    print(response)
except ClientError as e:
    print(e)
