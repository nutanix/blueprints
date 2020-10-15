ACCESS_KEY = '@@{cred_aws.username}@@'
SECRET_KEY = '@@{cred_aws.secret}@@'
AWS_REGION = '@@{clusters_geolocation}@@'
ROLE_NAME = '@@{role_name}@@'
S3_BUCKET_NAME = '@@{s3_bucket_name}@@'
S3_BUCKET_FILE = '@@{s3_bucket_file}@@'
LAMBDA_NAME = '@@{lambda_name}@@'
LAMBDA_RUNTIME = '@@{lambda_runtime}@@' # 'nodejs'|'nodejs4.3'|'nodejs6.10'|'nodejs8.10'|'nodejs10.x'|'nodejs12.x'|'java8'|'java11'|'python2.7'|'python3.6'|'python3.7'|'python3.8'|'dotnetcore1.0'|'dotnetcore2.0'|'dotnetcore2.1'|'dotnetcore3.1'|'nodejs4.3-edge'|'go1.x'|'ruby2.5'|'ruby2.7'|'provided'
LAMBDA_HANDLER = '@@{lambda_handler}@@'

from boto3 import client
from boto3 import setup_default_session

setup_default_session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

lam = client('lambda')
iam = client('iam')

role = iam.get_role(RoleName=ROLE_NAME)

response = lam.create_function(
    FunctionName=LAMBDA_NAME,
    Runtime=LAMBDA_RUNTIME,
    Role=role['Role']['Arn'],
    Handler=LAMBDA_HANDLER,
    Code={
        'S3Bucket': S3_BUCKET_NAME,
        'S3Key': S3_BUCKET_FILE,
    }
)

print(response)