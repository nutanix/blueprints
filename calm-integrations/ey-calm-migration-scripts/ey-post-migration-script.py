#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import requests
import json

from calm.common.flags import gflags

from calm.lib.model.store.db_session import flush_session
import calm.lib.model as model

from helper import change_project, init_contexts

log = logging.getLogger('category')
logging.basicConfig(level=logging.INFO,
                    format="%(message)s",
                    datefmt='%H:%M:%S')

if 'DEST_PC_IP' not in os.environ:
    raise Exception("Please export 'DEST_PC_IP'.")

DEST_PC_IP = os.environ['DEST_PC_IP']
PC_PORT = 9440
LENGTH = 100

if (
    'DEST_ACCOUNT_UUID' not in os.environ or
    'DEST_PROJECT' not in os.environ or
    'DEST_PC_USER' not in os.environ or
    'DEST_PC_PASS' not in os.environ
    ):
    raise Exception("Please export 'DEST_ACCOUNT_UUID', 'DEST_PROJECT', 'DEST_PC_USER' &  'DEST_PC_PASS'.")

dest_base_url = "https://{}:{}/api/nutanix/v3".format(DEST_PC_IP,str(PC_PORT))
dest_pc_auth = { "username": os.environ['DEST_PC_USER'], "password": os.environ['DEST_PC_PASS']}

dest_account_uuid = os.environ['DEST_ACCOUNT_UUID']
dest_project = os.environ['DEST_PROJECT']
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
        raise

def main():
    try:
        app_names = set()
        total_vms = 1
        offset = 0

        init_contexts()

        while offset < total_vms:
            vm_entities, total_vms = get_vm_list(dest_base_url, dest_pc_auth, offset)
        
            for vm in vm_entities:
                instance_id = vm["metadata"]["uuid"]
                vm_name = vm["status"]["name"]
                NSE = model.NutanixSubstrateElement.query(instance_id=instance_id)
                if NSE:
                    NSE = NSE[0]
                    if NSE.spec.resources.account_uuid != dest_account_uuid:
                        log.info("Updating VM substrate for '{}' with instance_id '{}'.".format(vm_name, instance_id))
                        NSE.spec.resources.account_uuid = dest_account_uuid
                        NSE.spec.resources.cluster_uuid = vm["status"]["cluster_reference"]["uuid"]
                        for i in range(len(NSE.spec.resources.nic_list)):
                            NSE.spec.resources.nic_list[i].nic_type = vm["status"]["resources"]["nic_list"][i]["nic_type"]
                            NSE.spec.resources.nic_list[i].subnet_reference = vm["status"]["resources"]["nic_list"][i]["subnet_reference"]
                            NSE.spec.resources.nic_list[i].ip_endpoint_list = vm["status"]["resources"]["nic_list"][i]["ip_endpoint_list"]
                        NSE.save()
                        NS = NSE.replica_group
                        NS.spec.resources.account_uuid = dest_account_uuid
                        for i in range(len(NS.spec.resources.nic_list)):
                            NS.spec.resources.nic_list[i].nic_type = vm["status"]["resources"]["nic_list"][i]["nic_type"]
                            NS.spec.resources.nic_list[i].subnet_reference = vm["status"]["resources"]["nic_list"][i]["subnet_reference"]
                            NS.spec.resources.nic_list[i].ip_endpoint_list = vm["status"]["resources"]["nic_list"][i]["ip_endpoint_list"]
                        NS.save()
                        NSC = NS.config
                        NSC.spec.resources.account_uuid = dest_account_uuid
                        for i in range(len(NSC.spec.resources.nic_list)):
                            NSC.spec.resources.nic_list[i].nic_type = vm["status"]["resources"]["nic_list"][i]["nic_type"]
                            NSC.spec.resources.nic_list[i].subnet_reference = vm["status"]["resources"]["nic_list"][i]["subnet_reference"]
                            NSC.spec.resources.nic_list[i].ip_endpoint_list = vm["status"]["resources"]["nic_list"][i]["ip_endpoint_list"]
                        NSC.save()
                        app_name = model.AppProfileInstance.get_object(NSE.app_profile_instance_reference).application.name
                        app_names.add(app_name)
            offset += LENGTH
        flush_session()
        for app in app_names:
            change_project(app, dest_project)
    except Exception as e:
        log.info("Exception: %s" % e)
        raise

if __name__ == '__main__':
    main()