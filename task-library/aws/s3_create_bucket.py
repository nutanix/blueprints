ACCESS_KEY = '@@{cred_aws.username}@@'
SECRET_KEY = '@@{cred_aws.secret}@@'
AWS_REGION = '@@{clusters_geolocation}@@'
BUCKET_NAME = '@@{bucket_name}@@'

import boto3

boto3.setup_default_session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

def create_bucket(bucket_name, region=None):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    
    if region is None:
        print('here')
        s3_client = boto3.client('s3')
        s3_client.create_bucket(Bucket=bucket_name)
    else:
        s3_client = boto3.client('s3', region_name=region)
        location = {'LocationConstraint': region}
        s3_client.create_bucket(Bucket=bucket_name,
                                CreateBucketConfiguration=location)
    return True
    
create_bucket(BUCKET_NAME,AWS_REGION)