# region headers
# * author:     jose.gomez@nutanix.com
# * version:    v1.0 - initial version
# * date:       25/06/2020
# task_name:    AWS_Create_MySQL
# description:  Create MySQL DB using RDS (PaaS)
# type:         Set Variable
# input vars:   aws_access_key, aws_secret_key, aws_region
# credentials:  cred_db
# output vars:  RDS_DB_IP
# endregion

# region capture Calm variables
aws_access_key = '@@{aws_access_key}@@'
aws_secret_key = '@@{aws_secret_key}@@'
aws_region = '@@{aws_region}@@'
aws_rds_instance = '@@{calm_application_uuid}@@'
mysql_username = '@@{cred_db.username}@@'
mysql_password = '@@{cred_db.secret}@@'
# endregion


# region load AWS SDK libraries
import boto3

from boto3 import setup_default_session
# endregion

# region - retrieve AWS credentials
setup_default_session(
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)
# endregion

# region - Create MySQL DB using RDS (PaaS)
client = boto3.client('rds')

response = client.create_db_instance(
    AllocatedStorage=5,
    DBInstanceClass='db.t2.micro',
    DBInstanceIdentifier=aws_rds_instance,
    Engine='MySQL',
    MasterUserPassword=mysql_password,
    MasterUsername=mysql_username,
)

print(response)
# endregion

# region - Monitor provisioning task and return FQDN/IP for connection
waiter = client.get_waiter('db_instance_available')
waiter.wait(DBInstanceIdentifier=aws_rds_instance)

response = client.describe_db_instances(DBInstanceIdentifier=aws_rds_instance)

print("RDS_DB_IP={}".format(response['DBInstances'][0]['Endpoint']['Address']))
# endregion
