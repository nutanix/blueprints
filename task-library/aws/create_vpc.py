'''
Creates:
    An Elastic IP for NAT Gateway(external connection for private subnet)
    VPC
    Private and Public subnets for the VPC
    Internet gateway
    Route tables for private and public subnets
    NAT Gateway

* Access to VMs in public subnet will be restricted based on security group policies
* VMs created under private subnet will only be accessible from VMs in public subnet
* Direct access would require creation of a VPN(Site-to-Site VPN) under VPC
'''

ACCESS_KEY = '@@{cred_aws.username}@@'
SECRET_KEY = '@@{cred_aws.secret}@@'
AWS_REGION = '@@{clusters_geolocation}@@'
ELASTIC_IP_NAME_TAG = '@@{elastic_ip_name_tag}@@'
VPC_NAME = '@@{vpc_name}@@'
VPC_CIDR_BLOCK = '@@{vpc_cidr_block}@@'
PUBLIC_SUBNET_NAME = '@@{public_subnet_name}@@'
PUBLIC_SUBNET_CIDR = '@@{public_subnet_cidr}'
PRIVATE_SUBNET_NAME = '@@{private_subnet_name}@@'
PRIVATE_SUBNET_CIDR = '@@{private_subnet_cidr}@@'
INTERNET_GATEWAY_NAME = '@@{internet_gateway_name}@@'
PUBLIC_ROUTE_TABLE_NAME = '@@{public_route_table_name}@@'
PRIVATE_ROUTE_TABLE_NAME = '@@{private_route_table_name}@@'
NAT_GATEWAY_NAME = '@@{nat_gateway_name}@@'

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
    return boto3.client('ec2'), boto3.resource('ec2')

def allocate_elastic_ip(client):
    '''allocate elastic IP for VPC internet gateway'''
    print("Allocating Elastic IP for for NAT Gateway")
    allocation = client.allocate_address(Domain='vpc')
    print("Allocation Id: "+ allocation['AllocationId'] + " Public IP: " + allocation['PublicIp'])
    client.create_tags(Resources=[allocation['AllocationId']], Tags=[{"Key": "Name", "Value": ELASTIC_IP_NAME_TAG}])
    print("Added Name tag: " + ELASTIC_IP_NAME_TAG + " to Elastic IP")
    return allocation['AllocationId']

def create_vpc_and_dependencies(resource):

    print("Creating VPC")
    # create VPC
    vpc = resource.create_vpc(CidrBlock=VPC_CIDR_BLOCK)
    vpc.create_tags(Tags=[{"Key": "Name", "Value": VPC_NAME}])
    vpc.wait_until_available()
    print("Created VPC: " + vpc.id)

    print("Creating Subnets and Internet Gateway")
    # Create public and private subnets
    public_subnet = resource.create_subnet(CidrBlock=PUBLIC_SUBNET_CIDR, VpcId=vpc.id)
    public_subnet.create_tags(Tags=[{"Key": "Name", "Value": PUBLIC_SUBNET_NAME}])
    private_subnet = resource.create_subnet(CidrBlock=PRIVATE_SUBNET_CIDR, VpcId=vpc.id)
    private_subnet.create_tags(Tags=[{"Key": "Name", "Value": PRIVATE_SUBNET_NAME}])

    # Create internet gateway
    internet_gateway = resource.create_internet_gateway()
    internet_gateway.create_tags(Tags=[{"Key": "Name", "Value": INTERNET_GATEWAY_NAME}])
    vpc.attach_internet_gateway(InternetGatewayId=internet_gateway.id)

    print("Creating route tables")
    # Create a route table and route for public subnet
    public_route_table = vpc.create_route_table()
    public_route_table.create_tags(Tags=[{"Key": "Name", "Value": PUBLIC_ROUTE_TABLE_NAME}])
    public_route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=internet_gateway.id)
    # Associate the route table with public subnet
    public_route_table.associate_with_subnet(SubnetId=public_subnet.id)

    # Create private route table and assosiate it with the private subnet
    private_route_table = vpc.create_route_table()
    private_route_table.create_tags(Tags=[{"Key": "Name", "Value": PRIVATE_ROUTE_TABLE_NAME}])
    private_route_table.associate_with_subnet(SubnetId=private_subnet.id)

    return public_subnet.id, private_route_table

def create_gateway(waiter, client, eip, public_sub, private_rt):
    # Create NAT gateway for private subnet
    print("Creating NAT Gateway for private subnet")
    gateway_creation_response = client.create_nat_gateway(AllocationId=eip, SubnetId=public_sub)
    gateway_id = gateway_creation_response['NatGateway']['NatGatewayId']
    client.create_tags(Resources=[gateway_id], Tags=[{"Key": "Name", "Value": NAT_GATEWAY_NAME}])
    print("Waiting for NAT gateway to be available")
    waiter.wait(NatGatewayIds=[gateway_id])
    print("Created NAT Gateway: " + gateway_id)

    # Add destiantion route with NAT gateway to private route table
    private_rt.create_route(DestinationCidrBlock='0.0.0.0/0', NatGatewayId=gateway_id)
    print("##### VPC creation is complete #####")

def main():
    try:
        ec2_client, ec2_resource = setup()
        waiter = ec2_client.get_waiter('nat_gateway_available')
        elastic_ip_allocation_id = allocate_elastic_ip(ec2_client)
        pub_subnet_id, priv_route_table = create_vpc_and_dependencies(ec2_resource)
        create_gateway(waiter, ec2_client, elastic_ip_allocation_id, pub_subnet_id, priv_route_table)
    except ClientError as e:
        print("Unexpected error: " + str(e))
        raise
    except WaiterError as e:
        print("NAT Gateway creation failed to complete in 10 minutes")
        print(str(e))
        raise

if __name__ == '__main__':
    main()
