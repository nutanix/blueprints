# region headers
# * author:     jose.gomez@nutanix.com
# * version:    v1.0 - initial version
# * date:       25/06/2020
# task_name:    Azure_Create_MySQL
# description:  Create MySQL DB using Azure Database for MySQL (PaaS)
# type:         Set Variable
# input vars:   azure_subscription_id, azure_client_id, azure_tenant_id, azure_secret, azure_resource_group, azure_location
# credentials:  cred_db
# output vars:  AZ_DB_IP
# endregion

# region capture Calm variables
az_subscription_id = '@@{azure_subscription_id}@@'
az_client_id = '@@{azure_client_id}@@'
az_tenant_id = '@@{azure_tenant_id}@@'
az_secret = '@@{azure_secret}@@'
az_resource_group_name = '@@{azure_resource_group}@@'
az_location = '@@{azure_location}@@'
mysql_name = '@@{calm_application_uuid}@@'
mysql_username = '@@{cred_db.username}@@'
mysql_password = '@@{cred_db.secret}@@'
# endregion

# region load Azure SDK libraries
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.rdbms.mysql import MySQLManagementClient
from azure.mgmt.rdbms.mysql.models import ServerForCreate, ServerPropertiesForDefaultCreate, ServerVersion
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

# region - Create MySQL DB using Azure Database for MySQL (PaaS)
credentials, subscription_id = get_credentials()
client = MySQLManagementClient(credentials,subscription_id)

mysql_properties = ServerPropertiesForDefaultCreate(
    administrator_login=mysql_username,
    administrator_login_password=mysql_password,
    version=ServerVersion.five_full_stop_seven,
    ssl_enforcement='Disabled'
)

server_properties = ServerForCreate(
    location=az_location,
    properties=mysql_properties
)

server_creation_poller = client.servers.create(
    az_resource_group_name,
    mysql_name,
    server_properties
)
# endregion

# region - Monitor provisioning task and return FQDN/IP for connection
server = server_creation_poller.result()
print("AZ_DB_IP={}.mysql.database.azure.com".format(mysql_name))
# endregion