# region headers
# * author:     jose.gomez@nutanix.com
# * version:    v1.0 - initial version
# * date:       25/07/2020
# task_name:    Azure_Launch_ARM
# description:  Launch ARM template
# type:         Execute
# input vars:   azure_subscription_id, azure_client_id, azure_tenant_id, azure_secret, azure_resource_group, azure_location, arm_template_uri
# credentials:  cred_os
# output vars:  none
# endregion

# region capture Calm variables
az_subscription_id = '@@{azure_subscription_id}@@'
az_client_id = '@@{azure_client_id}@@'
az_tenant_id = '@@{azure_tenant_id}@@'
az_secret = '@@{azure_secret}@@'
az_resource_group_name = '@@{azure_resource_group}@@'
az_location = '@@{azure_location}@@' # ex. uksouth
arm_template = '@@{arm_template_uri}@@' # ex. https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-vm-simple-linux/azuredeploy.json
os_username = '@@{cred_os.username}@@' # ex. ubuntu
os_password = '@@{cred_os.secret}@@' # ex. NutanixCalm/4u
vm_name = '@@{name}@@' # ex. calm-az-sdk-arm
# endregion


r = urlreq(arm_template)
if r.ok:
    template = json.loads(r.content)
else:
    print("Post request failed", r.content)
    exit(1)

# region load Azure SDK libraries
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
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

# region - Create RG if it doesn't exist
credentials, subscription_id = get_credentials()
client = ResourceManagementClient(credentials,subscription_id)
client.resource_groups.create_or_update(
    az_resource_group_name,
    {
        'location': az_location
    }
)
# endregion

# region - Set variable values
parameters = {
    'adminUsername': os_username,
    'adminPasswordOrKey': os_password,
    'vmName': vm_name
}
parameters = {k: {'value': v} for k, v in parameters.items()}
# endregion

# region - Build json payload
deployment_properties = {
    'mode': DeploymentMode.incremental,
    'template': template,
    'parameters': parameters
}
# endregion

# region - Create resources with ARM template
deployment_async_operation = client.deployments.create_or_update(
    az_resource_group_name,
    'azure-sample',
    deployment_properties
)
# endregion

# region - Monitor provisioning task and return FQDN/IP for connection
deployment_async_operation.wait()
print("Keep Calm and Deploy ARM templates!")
# endregion
