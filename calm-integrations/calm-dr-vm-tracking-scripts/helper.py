"Script to change application and its underlying vm's ownership"

# -*- coding: utf-8 -*-

import requests
import ujson
import logging
import json

from aplos.categories.category import Category, CategoryKey
from aplos.insights.entity_capability import EntityCapability
from aplos.lib.tenant.tenant_utils import TenantUtils

from calm.common.config import init_config, get_config
from calm.common.flags import gflags
from calm.common.project_util import ProjectUtil
from calm.lib.model import Application, Account
from calm.lib.constants import SUBSTRATE
from calm.lib.model.store.db import create_db_connection
from calm.lib.model.store.db_session import create_session, set_session_type
from calm.pkg.common.scramble import init_scramble
from calm.lib.model.store.db import get_insights_db
from calm.lib.proto import AbacEntityCapability

log = logging.getLogger('eylog')
logging.basicConfig(level=logging.INFO,
                    format="%(message)s",
                    datefmt='%H:%M:%S')

init_config()
LENGTH = 100
HEADERS = {'content-type': 'application/json', 'Accept': 'application/json'}
ESXI_HYPERVISOR_TYPE = "ESX"

# This is needed as when we import calm models, Flags needs be initialized


def init_contexts():
    """initiate context"""
    cfg = get_config()
    keyfile = cfg.get('security', 'keyfile')
    init_scramble(keyfile)
    set_session_type('green', cfg.get('store', 'flush_parallelisation_factor'), cfg.get('store', 'bulk_size'))
    create_db_connection(register_entities=False)
    create_session()


def change_project(application_name, new_project_name):
    """
    change_project method for the file
    Raises:
        Exception: when command line args are not exepcted
    Returns:
        None
    """
    tenant_uuid = TenantUtils.get_logged_in_tenant()
    project_handle = ProjectUtil()
    app_name = application_name
    new_project_name = new_project_name

    app_kind = "app"

    # Verify if supplied project name is valid
    project_proto = project_handle.get_project_by_name(new_project_name)
    if not project_proto:
        raise Exception("No project in system with name '{}'".format(new_project_name))
    new_project_uuid = str(project_proto.uuid)

    # Verify if supplied application name is valid
    apps = Application.query(name=app_name, deleted=False)
    if not apps:
        raise Exception("No app in system with name '{}'".format(app_name))
    app = apps[0]

    entity_cap = EntityCapability(kind_name=app_kind, kind_id=str(app.uuid))

    if entity_cap.project_name == new_project_name:
        log.info("Application '{}' is already in same project : '{}'".format(app_name, new_project_name))
        return

    # make sure app contains vms of type AHV or existing machine only
    pe_account_uuids = set()
    app_substratecfgs = []
    for deploy in app.active_app_profile_instance.deployments:
        if deploy.substrate.config.type not in [SUBSTRATE.KIND.NUTANIX, SUBSTRATE.KIND.Existing]:
            raise Exception("This script not supported to migrate app's containing VM's other than AHV and Existing Machine")
        else:
            app_substratecfgs.append(deploy.substrate.config)
            if deploy.substrate.config.type == SUBSTRATE.KIND.NUTANIX:
                pe_account_uuids.add(str(deploy.substrate.config.spec.resources.account_uuid))
    pc_account_uuid_object_map = {}
    pe_account_pc_account_uuid_map = {}
    for pe_account_uuid in pe_account_uuids:
        pe_account = Account.get_object(str(pe_account_uuid))
        pc_account_uuid = str(pe_account.data.pc_account_uuid)
        pe_account_pc_account_uuid_map[str(pe_account_uuid)] = pc_account_uuid
        pc_account_uuid_object_map[pc_account_uuid] = Account.get_object(str(pc_account_uuid))

    #for pc_account_uuid in pc_account_uuid_object_map:
        #if str(pc_account_uuid) not in project_proto.account_id_list:
            #raise Exception("'{}' Nutanix account used by '{}' application not present in '{}' project".format(pc_account_uuid_object_map[str(pc_account_uuid)].name, app.name, new_project_name))

    for substratecfg in app_substratecfgs:
        if substratecfg.type == SUBSTRATE.KIND.Existing:
            continue
        pc_account_uuid = pe_account_pc_account_uuid_map[str(substratecfg.spec.resources.account_uuid)]
        is_host_pc_subcfg = pc_account_uuid_object_map[pc_account_uuid].data.host_pc
        if is_host_pc_subcfg:

            # host pc networks are stored under network_id_list attribute
            project_nics_to_consider = project_proto.network_id_list
        else:

            # remote pc networks are stored under external_network_id_list attribute
            project_nics_to_consider = [network.uuid for network in project_proto.external_network_list]
        for nic in substratecfg.spec.resources.nic_list:
            if nic.subnet_reference and nic.subnet_reference.uuid:
                nic_uuid = str(nic.subnet_reference.uuid)
                if nic_uuid not in project_nics_to_consider:
                    msg = ("'{}' subnet used by '{}' application not present under '{}' project, please "
                           "consider whitelisting all subnets in new project which are white listed in old project".format(nic_uuid, app.name, new_project_name))
                    #raise Exception(msg)

    log.info("Moving '{}' application to new  project : '{}'".format(app_name, new_project_name))

    # To change ownership of an app to new project, we need to below things

    # 1. Find category uuid  corresponding to app's EC for {"Project", "old project name"} category
    # 2. Then remove category uuid found in step 1 from EC's category_id_list attribute
    # 3. Create a New category with key 'Project' and value as new_project_name and then add category uuid to EC's category_id_list attribute
    # 4. Then we need to update EC's project_name and project_reference to New Project
    # 5. Save EC

    # Step 1 to 3 are needed as API's populate project_reference under metadata based Project Category

    handle_entity_project_change("app", str(app.uuid), tenant_uuid, new_project_name, new_project_uuid)
    log.info("Successfully changed '{}' application's ownership to new project '{}'".format(app_name, new_project_name))
    log.info("**" * 30)
    log.info("Now moving '{}' app's VM to new project '{}'".format(app_name, new_project_name))

    if app.app_blueprint_config.source_marketplace_name:
        log.info("Moving Markeplace BP of application '{}' to '{}' project".format(app_name, new_project_name))
        handle_entity_project_change("blueprint", str(app.app_blueprint_config.uuid), tenant_uuid, new_project_name, new_project_uuid)
        log.info("Successfully moved Markeplace BP of application '{}' to '{}' project".format(app_name, new_project_name))

    if not pc_account_uuid_object_map:
        log.info("There are no AHV vm's in the app, hence no vm belonging to this app needs any change")
        log.info("Successfully moved '{}' application to  '{}' project ".format(app_name, new_project_name))
        return

    # Find out UUIDs of the all the AHV VM's from application
    vm_uuids = []
    for deploy in app.active_app_profile_instance.deployments:
        for de in deploy.elements:
            sub_el = de.substrate_element
            if sub_el.type == "AHV_VM":
                vm_uuids.append(str(sub_el.instance_id))

    # pc_account_uuid_object_map suppose to have just one entry as we just support one account of type in project
    pc_account_obj = pc_account_uuid_object_map.values()[0]
    is_app_remote_pc = not pc_account_obj.data.host_pc
    if is_app_remote_pc:
        pc_ip = pc_account_obj.data.server
        password = pc_account_obj.data.password.blob
        pc_username = pc_account_obj.data.username
    log.info("Application's vms are '{}', is app on remote pc {}".format(vm_uuids, is_app_remote_pc))

    # Change ownership of all vm's to New project
    # Same step mentioned for app need to follow for vm
    for vm_uuid in vm_uuids:

        # Based on whether vm reside on local pc or remote pc we need to take action here

        # 1. for remote pc vm, we needd to update CalmProject category to hold new project name as value
        # 2. For local pc vm, we need to update vm's EC to point to new project, for local pc vm we don't
        # see CalmProject, hence there is no need to update CalmProject category value
        if is_app_remote_pc:
            update_vm_in_remote_pc(pc_ip, pc_username, password, vm_uuid, new_project_name)
            log.info("Successfully updated remote pc  '{}' vm's categories to hold new project name".format(vm_uuid))
        else:
            handle_entity_project_change("vm", vm_uuid, tenant_uuid, new_project_name, new_project_uuid)
            log.info("Successfully moved '{}' vm which is part of '{}' application to new project '{}'".format(vm_uuid, app_name, new_project_name))
    log.info("Successfully moved all vm's of '{}' application to '{}' project".format(app_name, new_project_name))
    log.info("Successfully moved '{}' application to  '{}' project ".format(app_name, new_project_name))


def change_project_vmware(application_name, new_project_name):
    """
    change_project method for the file
    Raises:
        Exception: when command line args are not exepcted
    Returns:
        None
    """
    tenant_uuid = TenantUtils.get_logged_in_tenant()
    project_handle = ProjectUtil()
    app_name = application_name
    new_project_name = new_project_name

    app_kind = "app"

    # Verify if supplied project name is valid
    project_proto = project_handle.get_project_by_name(new_project_name)
    if not project_proto:
        raise Exception("No project in system with name '{}'".format(new_project_name))
    new_project_uuid = str(project_proto.uuid)

    # Verify if supplied application name is valid
    apps = Application.query(name=app_name, deleted=False)
    if not apps:
        raise Exception("No app in system with name '{}'".format(app_name))
    app = apps[0]

    entity_cap = EntityCapability(kind_name=app_kind, kind_id=str(app.uuid))

    if entity_cap.project_name == new_project_name:
        log.info("Application '{}' is already in same project : '{}'".format(app_name, new_project_name))
        return

    log.info("Moving '{}' application to new  project : '{}'".format(app_name, new_project_name))


    handle_entity_project_change("app", str(app.uuid), tenant_uuid, new_project_name, new_project_uuid)
    log.info("Successfully changed '{}' application's ownership to new project '{}'".format(app_name, new_project_name))
    log.info("**" * 30)
    log.info("Now moving '{}' app's VM to new project '{}'".format(app_name, new_project_name))

    if app.app_blueprint_config.source_marketplace_name:
        log.info("Moving Markeplace BP of application '{}' to '{}' project".format(app_name, new_project_name))
        handle_entity_project_change("blueprint", str(app.app_blueprint_config.uuid), tenant_uuid, new_project_name, new_project_uuid)
        log.info("Successfully moved Markeplace BP of application '{}' to '{}' project".format(app_name, new_project_name))

    # Find out UUIDs of the all the AHV VM's from application
    vm_uuids = []
    for deploy in app.active_app_profile_instance.deployments:
        for de in deploy.elements:
            sub_el = de.substrate_element
            if sub_el.type == "VMWARE_VM":
                vm_uuids.append(str(sub_el.instance_id))
    # Change ownership of all vm's to New project
    # Same step mentioned for app need to follow for vm
    for vm_uuid in vm_uuids:
        handle_entity_project_change("vm", vm_uuid, tenant_uuid, new_project_name, new_project_uuid)
        log.info("Successfully moved '{}' vm which is part of '{}' application to new project '{}'".format(vm_uuid, app_name, new_project_name))
    log.info("Successfully moved all vm's of '{}' application to '{}' project".format(app_name, new_project_name))
    log.info("Successfully moved '{}' application to  '{}' project ".format(app_name, new_project_name))

def handle_entity_project_change(entity_kind, entity_uuid, tenant_uuid, new_project_name, new_project_uuid):
    """
    Handles entity project change
    Args:
        entity_kind(str): Entity kind
        entity_uuid(str): Entity uuid
        tenant_uuid(str): Tenent uuid
        new_project_name(str): new project's name for the entity
        new_project_uuid(str): new project's uuid for the entity
    """

    # 1. Find category uuid  corresponding to entity's EC for {"Project", "old project name"} category
    entity_cap = EntityCapability(kind_name=entity_kind, kind_id=str(entity_uuid))
    project_category_uuid = None
    for c_uuid in entity_cap.category_id_list:
        category_obj = Category(uuid=c_uuid)
        project_category_key_uuid = str(category_obj.abac_category_key)
        category_key_obj = CategoryKey(uuid=project_category_key_uuid)
        if category_key_obj.name == "Project":
            project_category_uuid = str(c_uuid)
            break

    # 2. Then remove category uuid found in step 1 from EC's category_id_list attribute
    entity_cap.remove_categories([project_category_uuid])

    # 3. Create a New category with key 'Project' and value as new_project_name and then add category uuid to EC's category_id_list attribute
    category_obj = get_or_create_category("Project", new_project_name, tenant_uuid)
    entity_cap.add_categories([str(category_obj.uuid)])

    # 4. Then we need to update EC's project_name and project_reference attrs with  New Project
    entity_cap.change_project_reference(new_project_uuid, new_project_name)

    # 5. Save EC
    entity_cap.save()


def update_vm_in_remote_pc(pc_ip, pc_username, pc_password, vm_uuid, new_project_name):
    """
    Update vm with new category, key for category is Project and value is param new_project_name
    Args:
        pc_ip(str): PC ip
        pc_username(str): PC username
        pc_password(str): PC password
        vm_uuid(str): VM uuid
        new_project_name(str): value for Project category
    Raises:
        Exception when some operation fails
    """
    headers = {'content-type': 'application/json'}
    auth = (pc_username, pc_password)
    category_url = "https://{}:9440/api/nutanix/v3/categories/CalmProject/{}".format(pc_ip, new_project_name)
    response = requests.get(category_url, auth=auth, headers=headers, verify=False)
    if response.status_code == 404:
        log.info("Needed category (key: value) ({}, {}) does not exist on remote PC, need to create one".format("CalmProject", new_project_name))
        category_create_paylod = {"description": "Created by CALM", "value": new_project_name}
        response = requests.put(category_url, auth=auth, data=ujson.dumps(category_create_paylod), headers=headers, verify=False)
        if response.status_code not in [200, 202]:
            log.info("Response status code {}, respnse content {}".format(response.status_code, response.content))
            raise Exception("Failed to create category, please contact Nutanix-calm team")

    vm_api_url = "https://{}:9440/api/nutanix/v3/vms/{}".format(pc_ip, vm_uuid)
    log.info("VM GET URL: '{}'".format(vm_api_url))
    response = requests.get(vm_api_url, auth=auth, headers=headers, verify=False)
    if response.status_code not in [200, 202]:
        log.info("Response status code {}, respnse content {}".format(response.status_code, response.content))
        raise Exception("Failed to get VM from a remote PC, please contact Nutanix-calm team")
    vm_get_response_str = response.content
    vm_get_response = ujson.loads(vm_get_response_str)
    vm_get_response.pop('status')
    categories = vm_get_response.get('metadata', {}).get('categories', {})
    categories['CalmProject'] = new_project_name
    response = requests.put(vm_api_url, auth=auth, data=ujson.dumps(vm_get_response), headers=headers, verify=False)
    if response.status_code not in [200, 202]:
        log.info("Response status code {}, respnse content {}".format(response.status_code, response.content))
        raise Exception("Failed to update VM on remote PC, please contact Nutanix-calm team")


def get_or_create_category(name, value, tenant_uuid):
    """
    Get or create catgory for given arguments
    Args:
        name(str): Category key
        value(str): Category value
        tenant_uuid(str): Tenant uuid
    Returns:
        object: category object
    """
    category_obj = Category()
    category_obj.lookup_category_by_name_value(name, value)
    if hasattr(category_obj, "value") and category_obj.value == value:
        log.info("category with name '{}' and value '{}', already exists , hence no need to create".format(name, value))
        return category_obj
    category_obj.tenant_uuid = tenant_uuid
    category_obj.initialize(name, value, "Created by CALM", None, True)
    category_obj.save()
    return category_obj


def get_mh_vm(base_url, auth, uuid):
    method = 'GET'
    url = base_url + "/mh_vms/{0}".format(uuid)
    resp = requests.request(
            method,
            url,
            headers=HEADERS,
            auth=(auth["username"], auth["password"]),
            verify=False
    )
    if resp.ok:
        resp_json = resp.json()
        return resp_json
    else:
        raise Exception("Failed to get vm '{}'.".format(uuid))


def update_mh_vm(base_url, auth, uuid, payload):
    method = 'PUT'
    url = base_url + "/mh_vms/{0}".format(uuid)
    resp = requests.request(
            method,
            url,
            headers=HEADERS,
            auth=(auth["username"], auth["password"]),
            verify=False,
            data=payload
    )
    if resp.ok:
        resp_json = resp.json()
        return resp_json
    else:
        raise Exception("Failed to update vm '{}'.".format(uuid))


def is_category_key_present(base_url, auth, key):
    method = 'GET'
    url = base_url + "/categories/{}".format(key)
    resp = requests.request(
        method,
        url,
        headers=HEADERS,
        auth=(auth["username"], auth["password"]),
        verify=False
    )
    if resp.ok:
        return True
    else:
        False


def create_category_key(base_url, auth, key):
    method = 'PUT'
    url = base_url + "/categories/{}".format(key)
    payload = {
        "name": key
    }
    resp = requests.request(
        method,
        url,
        data=json.dumps(payload),
        headers=HEADERS,
        auth=(auth["username"], auth["password"]),
        verify=False
    )
    if resp.ok:
        return True
    else:
        log.info("Failed to create category key '{}'.".format(key))
        log.info('Status code: {}'.format(resp.status_code))
        log.info('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        raise Exception("Failed to create category key '{}'.".format(key))


def create_category_value(base_url, auth, key, value):
    method = 'PUT'
    url = base_url + "/categories/{}/{}".format(key, value)
    payload = {
        "value": value,
        "description": ""
    }
    resp = requests.request(
        method,
        url,
        data=json.dumps(payload),
        headers=HEADERS,
        auth=(auth["username"], auth["password"]),
        verify=False
    )
    if resp.ok:
        return True
    else:
        log.info("Failed to create category value '{}' for key '{}'.".format(value, key))
        log.info('Status code: {}'.format(resp.status_code))
        log.info('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        raise Exception("Failed to create category value '{}' for key '{}'.".format(value, key))


def add_category_to_vm(base_url, auth, vm_uuid, key, value):

    vm_data = get_mh_vm(base_url, auth, vm_uuid)
    vm_data.pop("status", None)

    vm_data["metadata"]["categories"] =  vm_data["metadata"].get("categories", {})
    vm_data["metadata"]["categories"][key] = value

    update_mh_vm(base_url, auth, vm_uuid, vm_data)


def get_application_uuids(project_name):

    project_handle = ProjectUtil()

    project_proto = project_handle.get_project_by_name(project_name)

    if not project_proto:
        raise Exception("No project in system with name '{}'".format(project_name))
    project_uuid = str(project_proto.uuid)

    application_uuid_list = []

    db_handle = get_insights_db()
    applications = db_handle.fetch_many(AbacEntityCapability,kind="app",project_reference=project_uuid,select=['kind_id', '_created_timestamp_usecs_'])
    for application in applications:
        application_uuid_list.append(application[1][0])

    return application_uuid_list


def get_recovery_plan_jobs_list(base_url, auth, offset):
    method = 'POST'
    url = base_url + "/recovery_plan_jobs/list"
    payload = {"length": LENGTH, "offset": offset}
    resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=HEADERS,
            auth=(auth["username"], auth["password"]),
            verify=False
    )
    if resp.ok:
        resp_json = resp.json()
        return resp_json["entities"], resp_json["metadata"]["total_matches"]
    else:
        log.info("Failed to get recovery plan jobs list.")
        log.info('Status code: {}'.format(resp.status_code))
        log.info('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        raise Exception("Failed to get recovery plan jobs list.")

def get_recovery_plan_job_execution_status(base_url, auth, job_uuid):
    method = 'GET'
    url = base_url + "/recovery_plan_jobs/{0}/execution_status".format(job_uuid)
    resp = requests.request(
            method,
            url,
            headers=HEADERS,
            auth=(auth["username"], auth["password"]),
            verify=False
    )
    if resp.ok:
        resp_json = resp.json()
        return resp_json
    else:
        log.info("Failed to get recovery plan jobs {0} exucution status.".format(job_uuid))
        log.info('Status code: {}'.format(resp.status_code))
        log.info('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        raise Exception("Failed to get recovery plan jobs {0} exucution status.".format(job_uuid))


def get_vm_source_dest_uuid_map(base_url, auth):
    vm_source_dest_uuid_map = {}
    recovery_plan_jobs_list = []
    total_matches = 1
    offset = 0
    while offset < total_matches:
        entities, total_matches = get_recovery_plan_jobs_list(base_url, auth, offset)
        for entity in entities:
            if (
                entity["status"]["resources"]["execution_parameters"]["action_type"] in ["MIGRATE", "FAILOVER"] and
                (
                    entity["status"]["execution_status"]["status"] == "COMPLETED" or
                    entity["status"]["execution_status"]["status"] == "COMPLETED_WITH_WARNING"
                )
            ):
                recovery_plan_jobs_list.append(entity["metadata"]["uuid"])
        offset += LENGTH

    for recovery_plan_job in recovery_plan_jobs_list:
        job_execution_status = get_recovery_plan_job_execution_status(dest_base_url, dest_pc_auth, recovery_plan_job)
        step_execution_status_list = job_execution_status["operation_status"]["step_execution_status_list"]
        for step_execution_status_src in step_execution_status_list:
            if step_execution_status_src["operation_type"] == "ENTITY_RECOVERY" :
                step_uuid = step_execution_status_src["step_uuid"]
                src_vm_uuid = step_execution_status_src["any_entity_reference_list"][0]["uuid"]
                for step_execution_status_dest in step_execution_status_list:
                    if (
                        step_execution_status_dest["parent_step_uuid"] == step_uuid and
                        step_execution_status_dest["operation_type"] in ["ENTITY_RESTORATION", "ENTITY_MIGRATION"]
                    ):
                        dest_vm_uuid = step_execution_status_dest["any_entity_reference_list"][0]["uuid"]
                vm_source_dest_uuid_map[src_vm_uuid] = dest_vm_uuid

    return vm_source_dest_uuid_map
