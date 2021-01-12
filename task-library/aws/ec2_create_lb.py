'''
Creates:
    A security group for LB with rules to accept connection from specified CIDR to LB listener port
    ELB
    Target group

* Does not create VPC, subnets or instances. Use the create_vpc.py task library script for VPC creation
'''

ACCESS_KEY = '@@{cred_aws.username}@@'
SECRET_KEY = '@@{cred_aws.secret}@@'
AWS_REGION = '@@{clusters_geolocation}@@'
VPC_ID = '@@{vpc_id}@@'
SUBNET_IDS = '@@{subnet_ids}@@' # multiline string macro, each subnet ID on a different line
SECURITY_GROUP_NAME = '@@{security_group_name}@@'
SG_CIDR = '@@{sg_cidr}@@' # CIDR from which connections to LB(security group) are allowed
ELB_NAME = '@@{elb_name}@@' # should be unique in a region
ELB_SCHEME = '@@{elb_scheme}@@' # internet-facing or internal
ELB_LISTENER_PORT = '@@{elb_LISTENER_port}@@'
ELB_PROTOCOL = '@@{elb_protocol}@@' # HTTP or HTTPS for application load balancer
TARGET_PROTOCOL = '@@{target_protocol}@@' # HTTP or HTTPS for application load balancer
TARGET_GROUP_NAME = '@@{target_group_name}@@' # Name of target group attached to ELB
TARGET_INSTANCES = '@@{target_instances}@@' # multiline string macro, Instance IDs of EC2 instances to be registered under target group
TARGET_INSTANCE_PORT = '@@{target_instance_port}@@' # EC2 Instance port to which ELB forwards connections

import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import WaiterError


def setup():
    '''create client'''
    boto3.setup_default_session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=AWS_REGION
    )
    return boto3.client('ec2'), boto3.client('elbv2')


def create_lb_and_dependencies(ec2_client, elb_client, waiter):
    subnet_list = SUBNET_IDS.split()
    # Create Load Balancer Security group
    print("Creating security group for LB")
    lb_security_group = ec2_client.create_security_group(Description="LB Security Group", GroupName=SECURITY_GROUP_NAME, VpcId=VPC_ID)
    sg_group_id = lb_security_group['GroupId']
    ec2_client.authorize_security_group_ingress(GroupId=sg_group_id, CidrIp=SG_CIDR,FromPort=int(ELB_LISTENER_PORT), ToPort=int(ELB_LISTENER_PORT), IpProtocol='tcp')

    # Create Load Balancer
    print("Creating load balancer")
    lb = elb_client.create_load_balancer(Name=ELB_NAME, Subnets=subnet_list, SecurityGroups=[lb_security_group['GroupId']], Scheme=ELB_SCHEME)
    lb_arn = lb['LoadBalancers'][0]['LoadBalancerArn']
    lb_dns_name = lb['LoadBalancers'][0]['DNSName']
    print("Waiting for lb to be active")
    waiter.wait(LoadBalancerArns=[lb_arn]) # default 10 minutes, polling every 15 seconds

    # Create target group
    print("Creating ELB target group")
    target_group = elb_client.create_target_group(Name=TARGET_GROUP_NAME, Protocol=TARGET_PROTOCOL, Port=int(TARGET_INSTANCE_PORT), VpcId=VPC_ID)
    target_group_arn = target_group['TargetGroups'][0]['TargetGroupArn']

    # Create listeners
    print("Creating listeners")
    elb_client.create_listener(LoadBalancerArn=lb_arn, Protocol=ELB_PROTOCOL, Port=int(ELB_LISTENER_PORT), DefaultActions=[{'Type': 'forward', 'TargetGroupArn': target_group_arn }])

    # Register instances to target group
    target_list = []
    for instance_id in TARGET_INSTANCES.split():
        target_list.append({'Id': instance_id, 'Port': int(TARGET_INSTANCE_PORT)})
    print("Registering target instances to target group")
    targets = elb_client.register_targets(TargetGroupArn=target_group_arn, Targets=target_list)
    print("### Completed Load Balancer creation with arn '{}'' and DNS name '{}'####".format(lb_arn, lb_dns_name))


def main():
    try:
        ec2_client, elb_client = setup()
        waiter = elb_client.get_waiter('load_balancer_available')
        create_lb_and_dependencies(ec2_client, elb_client, waiter)
    except ClientError as e:
        print("Unexpected error: " + str(e))
        raise
    except WaiterError as e:
        print("LB creation failed to complete in 10 minutes")
        print(str(e))
        raise


if __name__ == '__main__':
    main()
