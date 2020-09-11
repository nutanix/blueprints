AZ_SUBSCRIPTION_ID = '@@{AZURE_SUBSCRIPTION_ID}@@'
AZ_CLIENT_ID = '@@{AZURE_CLIENT_ID}@@'
AZ_TENANT_ID = '@@{AZURE_TENANT_ID}@@'
AZ_SECRET = '@@{AZURE_SECRET}@@'
AZ_RESOURCE_GROUP_NAME = '@@{AZURE_RESOURCE_GROUP}@@'
AZ_LOCATION = '@@{AZURE_LOCATION}@@' # ex. uksouth
ARM_TEMPLATE = '@@{ARM_TEMPLATE_URI}@@' # ex. https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-vm-simple-linux/azuredeploy.json
OS_USERNAME = '@@{Cred_OS.username}@@' # ex. ubuntu
OS_PASSWORD = '@@{Cred_OS.secret}@@' # ex. NutanixCalm/4u
VM_NAME = '@@{name}@@' # ex. calm-az-sdk-arm

# ------------------------------------ #

r = urlreq(ARM_TEMPLATE)
if r.ok:
    template = json.loads(r.content)
else:
    print("Post request failed", r.content)
    exit(1)

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode

def get_credentials():
    subscription_id = AZ_SUBSCRIPTION_ID
    credentials = ServicePrincipalCredentials(
        client_id=AZ_CLIENT_ID,
        secret=AZ_SECRET,
        tenant=AZ_TENANT_ID
    )
    return credentials, subscription_id

credentials, subscription_id = get_credentials()
client = ResourceManagementClient(credentials,subscription_id)
client.resource_groups.create_or_update(
    AZ_RESOURCE_GROUP_NAME,
    {
        'location': AZ_LOCATION
    }
)

parameters = {
    'adminUsername': OS_USERNAME,
    'adminPasswordOrKey': OS_PASSWORD,
    'vmName': VM_NAME
}
parameters = {k: {'value': v} for k, v in parameters.items()}

deployment_properties = {
    'mode': DeploymentMode.incremental,
    'template': template,
    'parameters': parameters
}

deployment_async_operation = client.deployments.create_or_update(
    AZ_RESOURCE_GROUP_NAME,
    'azure-sample',
    deployment_properties
)

deployment_async_operation.wait()
print("Keep Calm and Deploy ARM templates!")