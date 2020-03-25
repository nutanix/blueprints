# region headers
# * author:     jose.gomez@nutanix.com
# * version:    v1.0 - initial version
# * date:       25/03/2020
# task_name:    Azure_Enable_Boot_Diagnostics
# description:  Enable Boot diagnostics for an Azure VM
# type:         Execute
# input vars:   azure_subscription_id, azure_client_id, azure_tenant_id, azure_secret, azure_storage_account_name
# output vars:  none
# endregion

# region capture Calm variables
az_subscription_id = '@@{azure_subscription_id}@@'
az_client_id = '@@{azure_client_id}@@'
az_tenant_id = '@@{azure_tenant_id}@@'
az_secret = '@@{azure_secret}@@'
az_resource_group_name = '@@{resource_group}@@'
az_vm_name = '@@{name}@@'
az_location = '@@{platform.azureData.location}@@' 
az_storage_account_name = '@@{azure_storage_account_name}@@'
# endregion

# region load Azure SDK libraries
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
# endregion

# region function - retrieve Azure credentials
def get_credentials():
    subscription_id = az_subscription_id
    credentials = ServicePrincipalCredentials(
        client_id=az_client_id,
        secret=az_secret,
        tenant=az_tenant_id
    )
    return credentials, subscription_id
# endregion

# region function - set Boot diagnostics for Azure VM
def set_bootDiagnostics():
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)

    # Set Boot diagnostics for the virtual machine
    az_storage_uri = 'https://{}.blob.core.windows.net/'.format(az_storage_account_name)
    
    async_vm_update = compute_client.virtual_machines.create_or_update(
        az_resource_group_name,
        az_vm_name,
        {
            'location': az_location,
            'diagnostics_profile': {
                'boot_diagnostics': {
                    'enabled': True,
                    'additional_properties': {},
                    'storage_uri': az_storage_uri
                }
            }
        }
    )
    print('\nConfiguring Boot diagnostics. Please wait...')
    async_vm_update.wait()
    
    # Get the virtual machine by name
    print('\nBoot diagnostics status')
    virtual_machine = compute_client.virtual_machines.get(
        az_resource_group_name,
        az_vm_name,
        expand='instanceview'
    )

    return virtual_machine.diagnostics_profile.boot_diagnostics
# endregion

# region execute function 
print set_bootDiagnostics()
# endregion
