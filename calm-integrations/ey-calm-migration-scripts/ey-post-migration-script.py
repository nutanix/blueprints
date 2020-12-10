#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
import json

from calm.common.flags import gflags

from calm.lib.model.store.db_session import flush_session
import calm.lib.model as model

from helper import change_project, init_contexts, log


if 'DEST_PC_IP' not in os.environ:
    raise Exception("Please export 'DEST_PC_IP'.")

DEST_PC_IP = os.environ['DEST_PC_IP']
PC_PORT = 9440
LENGTH = 100

if (
    'DEST_PROJECT_NAME' not in os.environ or
    'DEST_PC_USER' not in os.environ or
    'DEST_PC_PASS' not in os.environ
    ):
    raise Exception("Please export 'DEST_PROJECT_NAME', 'DEST_PC_USER' &  'DEST_PC_PASS'.")

dest_base_url = "https://{}:{}/api/nutanix/v3".format(DEST_PC_IP,str(PC_PORT))
dest_pc_auth = { "username": os.environ['DEST_PC_USER'], "password": os.environ['DEST_PC_PASS']}

DEST_PROJECT = os.environ['DEST_PROJECT_NAME']
headers = {'content-type': 'application/json', 'Accept': 'application/json'}

def get_vm_list(base_url, auth, offset):
    method = 'POST'
    url = base_url + "/vms/list"
 
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
        log.info("Failed to get vms list.")
        log.info('Status code: {}'.format(resp.status_code))
        log.info('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        raise Exception("Failed to get vms list.")

def get_account_uuid_map():

    nutanix_pc_accounts = model.NutanixPCAccount.query(deleted=False)
    dest_account_uuid_map = {}
    for account in nutanix_pc_accounts:
        if account.data.server == DEST_PC_IP:
            pc_account = account
            break
    for pe in pc_account.data.nutanix_account:
        dest_account_uuid_map[pe.data.cluster_uuid] = str(pe.uuid)
    
    return dest_account_uuid_map

def update_substrate_info(vm, dest_account_uuid_map):

    instance_id = vm["metadata"]["uuid"]
    vm_name = vm["status"]["name"]
    cluster_uuid = vm["status"]["cluster_reference"]["uuid"]

    NSE = model.NutanixSubstrateElement.query(instance_id=instance_id)
    if NSE:
        NSE = NSE[0]
        if NSE.spec.resources.account_uuid not in dest_account_uuid_map.values():
            log.info("Updating VM substrate for '{}' with instance_id '{}'.".format(vm_name, instance_id))
            NSE.spec.resources.account_uuid = dest_account_uuid_map[cluster_uuid]
            NSE.spec.resources.cluster_uuid = cluster_uuid
            for i in range(len(NSE.spec.resources.nic_list)):
                NSE.spec.resources.nic_list[i].nic_type = vm["status"]["resources"]["nic_list"][i]["nic_type"]
                NSE.spec.resources.nic_list[i].subnet_reference = vm["status"]["resources"]["nic_list"][i]["subnet_reference"]
                NSE.spec.resources.nic_list[i].ip_endpoint_list = vm["status"]["resources"]["nic_list"][i]["ip_endpoint_list"]
            NSE.save()
            NS = NSE.replica_group
            NS.spec.resources.account_uuid = dest_account_uuid_map[cluster_uuid]
            for i in range(len(NS.spec.resources.nic_list)):
                NS.spec.resources.nic_list[i].nic_type = vm["status"]["resources"]["nic_list"][i]["nic_type"]
                NS.spec.resources.nic_list[i].subnet_reference = vm["status"]["resources"]["nic_list"][i]["subnet_reference"]
                NS.spec.resources.nic_list[i].ip_endpoint_list = vm["status"]["resources"]["nic_list"][i]["ip_endpoint_list"]
            NS.save()
            NSC = NS.config
            NSC.spec.resources.account_uuid = dest_account_uuid_map[cluster_uuid]
            for i in range(len(NSC.spec.resources.nic_list)):
                NSC.spec.resources.nic_list[i].nic_type = vm["status"]["resources"]["nic_list"][i]["nic_type"]
                NSC.spec.resources.nic_list[i].subnet_reference = vm["status"]["resources"]["nic_list"][i]["subnet_reference"]
                NSC.spec.resources.nic_list[i].ip_endpoint_list = vm["status"]["resources"]["nic_list"][i]["ip_endpoint_list"]
            NSC.save()

def update_substrates():

    total_vms = 1
    offset = 0
    dest_account_uuid_map = get_account_uuid_map()

    while offset < total_vms:
        vm_entities, total_vms = get_vm_list(dest_base_url, dest_pc_auth, offset)
    
        for vm in vm_entities:
            update_substrate_info(vm, dest_account_uuid_map)
        offset += LENGTH
    flush_session()

def update_app_project():
    app_names = set()
    total_vms = 1
    offset = 0

    while offset < total_vms:

        vm_entities, total_vms = get_vm_list(dest_base_url, dest_pc_auth, offset)
    
        for vm in vm_entities:
            instance_id = vm["metadata"]["uuid"]
            NSE = model.NutanixSubstrateElement.query(instance_id=instance_id)
            if NSE:
                NSE = NSE[0]
                app_name = model.AppProfileInstance.get_object(NSE.app_profile_instance_reference).application.name
                app_names.add(app_name)
        offset += LENGTH

    for app_name in app_names:
        change_project(app_name, DEST_PROJECT)

def main():
    try:
        
        init_contexts()

        update_substrates()

        update_app_project()

    except Exception as e:
        log.info("Exception: %s" % e)
        raise

if __name__ == '__main__':
    main()