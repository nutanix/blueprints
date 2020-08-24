# region headers
# * author:     jose.gomez@nutanix.com
# * version:    v1.0 - initial version
# * date:       25/07/2020
# task_name:    AWS_Create_Lambda
# description:  Create AWS Lambda function
# type:         Execute
# input vars:   clusters_geolocation, role_name, s3_bucket_name, s3_bucket_file, lambda_name, lambda_runtime, lambda_handler
# credentials:  cred_aws
# output vars:  none
# endregion

# region capture Calm variables
access_key = '@@{cred_aws.username}@@'
secret_key = '@@{cred_aws.secret}@@'
aws_region = '@@{clusters_geolocation}@@'
role_name = '@@{role_name}@@'
s3_bucket_name = '@@{s3_bucket_name}@@'
s3_bucket_file = '@@{s3_bucket_file}@@'
lambda_name = '@@{lambda_name}@@'
lambda_runtime = '@@{lambda_runtime}@@' # 'nodejs'|'nodejs4.3'|'nodejs6.10'|'nodejs8.10'|'nodejs10.x'|'nodejs12.x'|'java8'|'java11'|'python2.7'|'python3.6'|'python3.7'|'python3.8'|'dotnetcore1.0'|'dotnetcore2.0'|'dotnetcore2.1'|'dotnetcore3.1'|'nodejs4.3-edge'|'go1.x'|'ruby2.5'|'ruby2.7'|'provided'
lambda_handler = '@@{lambda_handler}@@'
# endregion

# region load AWS SDK libraries
from boto3 import client
from boto3 import setup_default_session
# endregion

# region - retrieve AWS credentials
setup_default_session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=aws_region
)
# endregion

# region - Create Lambda function from S3 (PaaS)
lam = client('lambda')
iam = client('iam')

role = iam.get_role(RoleName=role_name)

response = lam.create_function(
    FunctionName=lambda_name,
    Runtime=lambda_runtime,
    Role=role['Role']['Arn'],
    Handler=lambda_handler,
    Code={
        'S3Bucket': s3_bucket_name,
        'S3Key': s3_bucket_file,
    }
)

print(response)
# endregion
