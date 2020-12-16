from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

# Location
DC_LOCATION = 'eastus2'

# Resource group name
RESOURCE_GROUP_NAME = 'calmrg'

# VM Name
VM_NAME = "test-azure-crud-task-library"

def get_credentials():
    subscription_id = "@@{subscription_id}@@"
    credentials = ServicePrincipalCredentials(
        client_id="@@{client_id}@@",
        secret="@@{secret}@@",
        tenant="@@{tenant}@@"
    )
    return credentials, subscription_id

def get_virtual_machine(compute_client):
    print('Get Virtual Machine {}'.format(VM_NAME))
    return compute_client.virtual_machines.get(
            RESOURCE_GROUP_NAME,
            VM_NAME
        )

def get_public_ip_address(nic_name, network_client):
    print('Get public IP address name for nic {}'.format(nic_name))
    async_network_interfaces_get = network_client.network_interfaces.get(
                RESOURCE_GROUP_NAME,
                nic_name
            )
    public_ip_address = async_network_interfaces_get.ip_configurations[0].public_ip_address
    if public_ip_address:
        return public_ip_address.id.split('/')[-1]
    else:
        return None

def delete_virtual_machine(vm_name, compute_client):
    print('Deleting VM {}'.format(vm_name))
    async_vm_delete = compute_client.virtual_machines.delete(
            RESOURCE_GROUP_NAME, 
            vm_name
            )
    async_vm_delete.wait()

def delete_public_ip_address(public_ip_address, network_client):
    print('Deleting Public IP address {}'.format(public_ip_address))
    async_public_ip_address_delete = network_client.public_ip_addresses.delete(
                RESOURCE_GROUP_NAME,
                public_ip_address
            )
    async_public_ip_address_delete.wait()

def delete_nic(nic_name, network_client):
    print('Deleting nic {}'.format(nic_name))
    async_nic_delete = network_client.network_interfaces.delete(
            RESOURCE_GROUP_NAME,
            nic_name
            )
    async_nic_delete.wait()

def delete_disk(disk_name, compute_client):
    print('Deleting disk {}'.format(disk_name))
    async_disk_delete = compute_client.disks.delete(
            RESOURCE_GROUP_NAME,
            disk_name
        )
    async_disk_delete.wait()

credentials, subscription_id = get_credentials()

compute_client = ComputeManagementClient(credentials, subscription_id)
network_client = NetworkManagementClient(credentials, subscription_id)
nic_list = []
disk_list = []

virtual_machine = get_virtual_machine(compute_client)

os_disk_name = virtual_machine.storage_profile.os_disk.name
disk_list.append(os_disk_name)

for disk in virtual_machine.storage_profile.data_disks:
    disk_list.append(disk.name)

for nic in virtual_machine.network_profile.network_interfaces:
    nic_name = nic.id.split('/')[-1]
    nic_list.append(nic_name)

delete_virtual_machine(VM_NAME, compute_client)

for disk_name in disk_list:
    delete_disk(disk_name, compute_client)

for nic_name in nic_list:
    public_ip_address_name = get_public_ip_address(nic_name, network_client)
    delete_nic(nic_name, network_client)
    if public_ip_address_name:
        delete_public_ip_address(public_ip_address_name, network_client)

