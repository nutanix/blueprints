import os
import traceback

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

from msrestazure.azure_exceptions import CloudError

# Location
DC_LOCATION = 'eastus2'

# Resource group name
RESOURCE_GROUP_NAME = 'calmrg'

# Network
VNET_NAME = 'calm-virtual-network-eastus2'
SUBNET_NAME = 'subnet1'

VM_NAME = "test-azure-crud-task-library"
IP_CONFIG_NAME = VM_NAME + "-config"
NIC_NAME = VM_NAME + "-nic"
PUBLIC_IP_ADDRESS_NAME = VM_NAME + "-public-ip"

LOGIN_USERNAME = "centos"
LOGIN_PASSWORD = "xxxxxxxx"

VM_REFERENCE = {
    'linux': {
        'publisher': 'OpenLogic',
        'offer': 'CentOS-HPC',
        'sku': '7.7',
        'version': '7.7.201910230'
    },
    'windows': {
        'publisher': 'MicrosoftWindowsServer',
        'offer': 'WindowsServer',
        'sku': '2016-Datacenter',
        'version': 'latest'
    }
}

def get_credentials():
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )
    return credentials, subscription_id

def create_nic(network_client):
    subnet_get = network_client.subnets.get(
        RESOURCE_GROUP_NAME,
        VNET_NAME,
        SUBNET_NAME
    )
    subnet_info = subnet_get

    parameters = {
            'location': DC_LOCATION,
            'ip_configurations': [{
                'name': IP_CONFIG_NAME,
                'subnet': {
                    'id': subnet_info.id
                }
            }]
        }

    if PUBLIC_IP_ADDRESS_NAME:
        public_ip_address = create_public_ip_address(network_client)
        parameters["ip_configurations"][0]["public_ip_address"] = { 'id' : public_ip_address.id } 

    print('Creating Nic {}'.format(NIC_NAME))

    async_nic_creation = network_client.network_interfaces.create_or_update(
        RESOURCE_GROUP_NAME,
        NIC_NAME,
        parameters
    )
    return async_nic_creation.result()

def create_public_ip_address(network_client):
    print('Creating public IP address')
    async_public_ip_creation = network_client.public_ip_addresses.create_or_update(
        RESOURCE_GROUP_NAME,
        PUBLIC_IP_ADDRESS_NAME,
        {
            'location': DC_LOCATION
        }
    )
    return async_public_ip_creation.result()

def create_virtual_machine(vm_parameters, compute_client):
    print('Creating VM {}'.format(VM_NAME))
    async_vm_creation = compute_client.virtual_machines.create_or_update(
        RESOURCE_GROUP_NAME, VM_NAME, vm_parameters)
    async_vm_creation.wait()

def create_vm_parameters(nic_id, vm_reference):
    """Create the VM parameters structure.
    """
    return {
        'location': DC_LOCATION,
        'os_profile': {
            'computer_name': VM_NAME,
            'admin_username': LOGIN_USERNAME,
            'admin_password': LOGIN_PASSWORD
        },
        'hardware_profile': {
            'vm_size': 'Standard_DS1_v2'
        },
        'storage_profile': {
            'image_reference': {
                'publisher': vm_reference['publisher'],
                'offer': vm_reference['offer'],
                'sku': vm_reference['sku'],
                'version': vm_reference['version']
            },
        },
        'network_profile': {
            'network_interfaces': [{
                'id': nic_id,
            }]
        },
    }

def main():
    credentials, subscription_id = get_credentials()

    compute_client = ComputeManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)

    try:
        nic = create_nic(network_client)

        vm_parameters = create_vm_parameters(nic.id, VM_REFERENCE['linux'])

        create_virtual_machine(vm_parameters, compute_client)

    except CloudError:
        print('A VM operation failed:\n{}'.format(traceback.format_exc()))
    else:
        print('VM creation completed successfully!')


if __name__ == "__main__":
    main()