ACCESS_KEY = '@@{cred_aws.username}@@'
SECRET_KEY = '@@{cred_aws.secret}@@'
AWS_REGION = '@@{clusters_geolocation}@@'
ROLE_NAME = '@@{role_name}@@'
ROLE_PERMISSIONS = '@@{role_permissions}@@' # YAML format
"""
    Version: '2012-10-17'
    Statement:
        - Effect: Allow
          Principal: 
            Service: lambda.amazonaws.com
          Action: sts:AssumeRole
"""
POLICY_ARN = '@@{policy_arn}@@'

from boto3 import client
from boto3 import setup_default_session

setup_default_session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

client = client('iam')

response = client.create_role(RoleName=ROLE_NAME,
    AssumeRolePolicyDocument=json.dumps(yaml.load(ROLE_PERMISSIONS))
)
print(response)

response = client.attach_role_policy(RoleName=ROLE_NAME, 
    PolicyArn=POLICY_ARN
)
print(response)