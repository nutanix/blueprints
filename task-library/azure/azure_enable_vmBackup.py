# region headers
# * author:     jose.gomez@nutanix.com
# * version:    v1.0 - initial version
# * date:       25/03/2020
# task_name:    Azure_Enable_Backup
# description:  Enable backup for an Azure VM
# type:         Execute
# input vars:   azure_subscription_id, azure_client_id, azure_tenant_id, azure_secret, azure_storage_account_name, az_recovery_services_vault_name, az_recovery_services_backup_policy_name
# output vars:  none
# endregion

# region capture Calm variables
az_subscription_id = '@@{azure_subscription_id}@@'
az_client_id = '@@{azure_client_id}@@'
az_tenant_id = '@@{azure_tenant_id}@@'
az_secret = '@@{azure_secret}@@'
az_resource_group_name = '@@{resource_group}@@'
az_vm_name = '@@{name}@@'
az_recovery_services_vault_name = '@@{azure_recovery_services_vault_name}@@'
az_recovery_services_backup_policy_name = '@@{azure_recovery_services_backup_policy_name}@@'
# endregion

# region load Azure SDK libraries
import datetime
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.recoveryservicesbackup import RecoveryServicesBackupClient
from azure.mgmt.recoveryservicesbackup.models import (AzureIaaSComputeVMProtectedItem, BackupRequestResource,
                                                      IaasVMBackupRequest,
                                                      IaasVMILRRegistrationRequest, IaasVMRestoreRequest,
                                                      ILRRequestResource, JobStatus,
                                                      OperationStatusValues, ProtectedItemResource, ProtectionState,
                                                      RecoveryType,
                                                      RestoreRequestResource,
                                                      BackupManagementType)
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

# region function - Enable backup for Azure VM   
def enable_recovery_services_backup():
    credentials, subscription_id = get_credentials()
    backup_client = RecoveryServicesBackupClient(credentials, subscription_id)
    
    container_name = "iaasvmcontainer;iaasvmcontainerv2;{};{}".format(az_resource_group_name,az_vm_name)
    fabric_name = "Azure"
    protected_item_name = "vm;iaasvmcontainerv2;{};{}".format(az_resource_group_name,az_vm_name)
    policy = backup_client.protection_policies.get(az_recovery_services_vault_name, az_resource_group_name, az_recovery_services_backup_policy_name)

    response = backup_client.protection_containers.refresh(az_recovery_services_vault_name, az_resource_group_name, fabric_name, raw=True)

    _get_operation_response(
        response,
        lambda operation_id: backup_client.protection_container_refresh_operation_results.get(
            az_recovery_services_vault_name, az_resource_group_name, fabric_name, operation_id, raw=True,
        ),
        None,
    )

    iaasvm_odata_filter = "backupManagementType eq '{}'".format('AzureIaasVM')
    protectable_items = backup_client.backup_protectable_items.list(az_recovery_services_vault_name, az_resource_group_name, filter=iaasvm_odata_filter, raw=True)

    for protectable_item in protectable_items:
        if protectable_item.name.lower() in container_name.lower():
            desired_protectable_item = protectable_item.properties
    
    protected_item_resource = ProtectedItemResource(
            properties=AzureIaaSComputeVMProtectedItem(policy_id=policy.id, source_resource_id=desired_protectable_item.virtual_machine_id)
            )

    response = backup_client.protected_items.create_or_update(
            az_recovery_services_vault_name, az_resource_group_name, fabric_name, container_name, protected_item_name,
            protected_item_resource, raw=True
            )

    job_response = _get_operation_response(
        response,
        lambda operation_id: backup_client.protected_item_operation_results.get(
            az_recovery_services_vault_name, az_resource_group_name, fabric_name, container_name, protected_item_name, operation_id, raw=True,
            ),
        lambda operation_id: backup_client.protected_item_operation_statuses.get(
            az_recovery_services_vault_name, az_resource_group_name, fabric_name, container_name, protected_item_name, operation_id,
            ),
        )

    wait_for_job_completion(job_response.job_id)
    
    print('Backup enabled for {}'.format(az_vm_name))
    exit(0)
# endregion

# region function - Helpers   
def _dummy_wait_and_return_true(timeout_in_sec):
    sleep(timeout_in_sec)
    return True

def wait_for_job_completion(job_id):
    retry_action_with_timeout(
        lambda: get_job_status(job_id),
        lambda job_status: not is_job_in_progress(job_status),
        3 * 60 * 60,  # 3 Hours
        lambda status_code: _dummy_wait_and_return_true,
        )

def get_job_status(job_id):
    credentials, subscription_id = get_credentials()
    backup_client = RecoveryServicesBackupClient(credentials, subscription_id)
    
    response = backup_client.job_details.get(az_recovery_services_vault_name, az_resource_group_name, job_id)
    return response.properties.status

def is_job_in_progress(job_status):
    in_progress = job_status in [JobStatus.in_progress.value, JobStatus.cancelling.value]
    if in_progress:
        sleep(60)
    return in_progress

def time_in_sec():
    return int(datetime.datetime.now().strftime("%s"))

def retry_action_with_timeout(action, validator, timeout, should_retry):
    end_time = time_in_sec() + timeout
    result = None
    validator_result = False if result is None else validator(result)

    while time_in_sec() < end_time and not validator_result:
        result = action()
        validator_result = validator(result)

    return result

def _get_operation_response(raw_response, get_operation_result_func, get_operation_status_func):
    operation_id_url = raw_response.response.headers["Location"]
    operation_id = (operation_id_url.split('?'))[0].rsplit('/')[-1]
    operation_response = get_operation_result_func(operation_id)

    while operation_response.response.status_code == 202:
        sleep(5)
        operation_response = get_operation_result_func(operation_id)

    if get_operation_status_func:
        operation_status_response = get_operation_status_func(operation_id)
        return operation_status_response.properties

    return operation_response
# endregion

# region execute function 
enable_recovery_services_backup()
# endregion
