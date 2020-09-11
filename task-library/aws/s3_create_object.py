ACCESS_KEY = '@@{cred_aws.username}@@'
SECRET_KEY = '@@{cred_aws.secret}@@'
AWS_REGION = '@@{clusters_geolocation}@@'
BUCKET_NAME = '@@{bucket_name}@@'
OBJECT_NAME = '@@{object_name}@@'
BINARY_DATA = '@@{binary_data}@@'

import boto3

boto3.setup_default_session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

def create_object(bucket_name, object_name, binary_data):
    """Create an S3 object in a specified bucket

    :param bucket_name: Bucket to use
    :param object_name: Object to create
    :param binary_data: Binart data for object
    :return: True if object created, else False
    """

    # Create object
    
    client = boto3.client('s3')
    client.put_object(Body=binary_data, Bucket=bucket_name, Key=object_name)
    
create_object(BUCKET_NAME,OBJECT_NAME,BINARY_DATA)