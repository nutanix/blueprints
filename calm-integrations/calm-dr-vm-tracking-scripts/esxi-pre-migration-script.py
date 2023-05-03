#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
import json

from calm.common.flags import gflags

import calm.lib.model as model

from helper import init_contexts, log, is_category_key_present, create_category_key, create_category_value, add_category_to_vm, get_application_uuids


REQUIRED_ATTRS = ['DEST_PC_IP', 'DEST_PC_USER', 'DEST_PC_PASS', 'SOURCE_PROJECT_NAME', 'SOURCE_PC_IP', 'SOURCE_PC_USER', 'SOURCE_PC_PASSWORD']
msg = ""
for attr in REQUIRED_ATTRS:
    if attr not in os.environ:
        msg = msg + attr + ", "
if msg:
    raise Exception("Please export {}". format(msg))

#constants
PC_PORT = 9440
SOURCE_PC_IP = os.environ['SOURCE_PC_IP']
SOURCE_PROJECT_NAME = os.environ['SOURCE_PROJECT_NAME']


DELETED_STATE = 'deleted'
VMWARE_VM = "VMWARE_VM"
ESXI_HYPERVISOR_TYPE = "ESX"
PROTECTED = "UNPROTECTED"
LENGTH = 100
DR_KEY = "VM_VCENTER_UUID"
headers = {'content-type': 'application/json', 'Accept': 'application/json'}

source_base_url = "https://{}:{}/api/nutanix/v3".format(SOURCE_PC_IP, str(PC_PORT))
source_pc_auth = {"username": os.environ['SOURCE_PC_USER'], "password": os.environ['SOURCE_PC_PASSWORD']}

dest_base_url = "https://{}:{}/api/nutanix/v3".format(os.environ['DEST_PC_IP'], str(PC_PORT))
dest_pc_auth = {"username": os.environ['DEST_PC_USER'], "password": os.environ['DEST_PC_PASS']}

SYS_DEFINED_CATEGORY_KEY_LIST = [
    "ADGroup",
    "AnalyticsExclusions",
    "AppTier",
    "AppType",
    "CalmApplication",
    "CalmDeployment",
    "CalmService",
    "CalmPackage",
    "Environment",
    "OSType",
    "Quaratine",
    "CalmVmUniqueIdentifier",
    "CalmUser",
    "account_uuid",
    "TemplateType",
    "VirtualNetworkType"
]


# Step -1:
"""
Get the map of vm_uuid to Vcenter uuid using mh_vms api
"""
def get_mh_vms_list(base_url, auth, offset):    
    method = 'POST'
    url = base_url + "/mh_vms/list"
    payload = {"length": LENGTH, "offset": offset}
    resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
    )
    if resp.ok:
        resp_json = resp.json()
        return resp_json["entities"], resp_json["metadata"]["total_matches"]
    else:
        log.info("Failed to get mh_vms list.")
        log.info('Status code: {}'.format(resp.status_code))
        log.info('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        raise Exception("Failed to get mh_vms list.")


def get_vm_vcenter_uuid_pc_uuid_map(base_url, pc_auth):
    res = {}
    total_matches = 1
    offset = 0
    while offset < total_matches:
        entities, total_matches = get_mh_vms_list(base_url, pc_auth, offset)
        for entity in entities:
            if entity["status"]["resources"]["hypervisor_type"] == ESXI_HYPERVISOR_TYPE and entity["status"]["resources"]["protection_type"] == PROTECTED:
                res[entity["status"]["resources"]["hypervisor_specific_id"]] = entity["metadata"]["uuid"]
        offset += LENGTH
    return res


# Step -2:
"""
Iterate over all the vms in the source project and create a category
    name : VMVCenterUuid
    value : Vm uuid on vcenter 

And Create all vm categories on destination setup
"""

def create_dr_categories_on_source_pc_and_update_vm():

    log.info("Creating Dr categories on source pc")
    dr_key_present = is_category_key_present(source_base_url, source_pc_auth, DR_KEY)
    if not dr_key_present:
        create_category_key(source_base_url, source_pc_auth, DR_KEY)

    vm_uuid_map = get_vm_vcenter_uuid_pc_uuid_map(source_base_url, source_pc_auth)
    for vcenter_vm_uuid, pc_vm_uuid in vm_uuid_map.items():
        create_category_value(source_base_url, source_pc_auth, DR_KEY, vcenter_vm_uuid)
        add_category_to_vm(source_base_url, source_pc_auth, pc_vm_uuid, DR_KEY, vcenter_vm_uuid)


# Step-3
"""
   -> Create the DR key on source and destination setup
   -> Iterate over all the applications, and get the vm used in substrates
   -> Get the vcenter_vm_uuid and using mh_vms/list , get the pc_vm_uuid
   -> Create Category key for DR_key: Vcenter_uuid on source/destination setup
   -> Add the category to given vm
"""

def create_categories():

    log.info("Creating categories/values")

    dr_key_present = is_category_key_present(source_base_url, source_pc_auth, DR_KEY)
    if not dr_key_present:
        create_category_key(source_base_url, source_pc_auth, DR_KEY)

    dr_key_present = is_category_key_present(dest_base_url, dest_pc_auth, DR_KEY)
    if not dr_key_present:
        create_category_key(dest_base_url, dest_pc_auth, DR_KEY)

    init_contexts()
    vm_uuid_map = get_vm_vcenter_uuid_pc_uuid_map(source_base_url, source_pc_auth)
    application_uuid_list = get_application_uuids(SOURCE_PROJECT_NAME)
    for app_uuid in application_uuid_list:
        application =  model.Application.get_object(app_uuid)
        if application.state != DELETED_STATE:
            for dep in application.active_app_profile_instance.deployments:
                if dep.substrate.type == VMWARE_VM:
                    for element in dep.substrate.elements:
                        vcenter_vm_uuid = str(element.instance_id)
                        if vcenter_vm_uuid not in vm_uuid_map:
                            continue

                        # Create category value for hypervisor specific attributes at source pc, dest_pc and udpate vm with it
                        pc_vm_uuid = vm_uuid_map[vcenter_vm_uuid]
                        create_category_value(source_base_url, source_pc_auth, DR_KEY, vcenter_vm_uuid)
                        create_category_value(dest_base_url, dest_pc_auth, DR_KEY, vcenter_vm_uuid)
                        add_category_to_vm(source_base_url, source_pc_auth, pc_vm_uuid, DR_KEY, vcenter_vm_uuid)


def main():
    try:
        create_categories()
    except Exception as e:
        log.info("Exception: %s" % e)
        raise
if __name__ == '__main__':
    main()
