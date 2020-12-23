import os
import traceback

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption

from msrestazure.azure_exceptions import CloudError

# Location
DC_LOCATION = 'eastus2'

# Resource group name
RESOURCE_GROUP_NAME = 'calmrg'

VM_NAME = "test-azure-crud-task-library"
DISK_NAME = VM_NAME + '-disk1'

def get_credentials():
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )
    return credentials, subscription_id

def get_virtual_machine(compute_client):
    print('Get Virtual Machine {}'.format(VM_NAME))
    return compute_client.virtual_machines.get(
            RESOURCE_GROUP_NAME,
            VM_NAME
        )

def create_managed_disk(compute_client, size):
    print('Create (empty) managed Data Disk')
    async_disk_creation = compute_client.disks.create_or_update(
        RESOURCE_GROUP_NAME,
        DISK_NAME,
        {
            'location': DC_LOCATION,
            'disk_size_gb': size,
            'creation_data': {
                'create_option': DiskCreateOption.empty
            }
        }
    )
    return async_disk_creation.result()

def attach_data_disk(compute_client, virtual_machine, data_disk, lun):
    print('Attach Data Disk')
    virtual_machine.storage_profile.data_disks.append({
        'lun': lun,
        'name': DISK_NAME,
        'create_option': DiskCreateOption.attach,
        'managed_disk': {
            'id': data_disk.id
        }
    })
    async_disk_attach = compute_client.virtual_machines.create_or_update(
        RESOURCE_GROUP_NAME,
        virtual_machine.name,
        virtual_machine
    )
    async_disk_attach.wait()

def main():
    credentials, subscription_id = get_credentials()

    compute_client = ComputeManagementClient(credentials, subscription_id)

    try:

        virtual_machine = get_virtual_machine(compute_client)
        disk = create_managed_disk(compute_client, 10)
        attach_data_disk(compute_client, virtual_machine, disk, 0)

    except CloudError:
        print('A VM update operation failed:\n{}'.format(traceback.format_exc()))
    else:
        print('VM update completed successfully!')


if __name__ == "__main__":
    main()