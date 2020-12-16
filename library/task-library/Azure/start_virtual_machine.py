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

def get_credentials():
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )
    return credentials, subscription_id

def start_virtual_machine(compute_client):
    print('Start Virtual Machine {}'.format(VM_NAME))
    async_vm_start = compute_client.virtual_machines.start(
            RESOURCE_GROUP_NAME, VM_NAME)
    async_vm_start.wait()

def main():
    credentials, subscription_id = get_credentials()

    compute_client = ComputeManagementClient(credentials, subscription_id)

    try:

        start_virtual_machine(compute_client)

    except CloudError:
        print('VM stop operation failed:\n{}'.format(traceback.format_exc()))
    else:
        print('VM stop completed successfully!')


if __name__ == "__main__":
    main()