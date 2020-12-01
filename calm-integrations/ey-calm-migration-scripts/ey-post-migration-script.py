#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO- Add authentication
# TODO- Add skip registration flag

# pylint: disable= E402

import gevent.monkey
gevent.monkey.patch_all()
import sys
import logging
import warnings
import os
import requests
import json

from calm.common.config import get_config

from calm.common.flags import gflags

from calm.lib.model.store.db import create_db_connection
from calm.pkg.common.scramble import init_scramble
from calm.lib.model.store.db_session import create_session, set_session_type, flush_session
import calm.lib.model as model

from helper import change_project

warnings.filterwarnings("ignore")
log = logging.getLogger('category')
logging.basicConfig(level=logging.INFO,
                    format="%(message)s",
                    datefmt='%H:%M:%S')

DEST_PC_IP = "10.46.7.50"
PC_PORT = 9440
LENGTH = 100

dest_base_url = "https://{}:{}/api/nutanix/v3".format(DEST_PC_IP,str(PC_PORT))
dest_pc_auth = { "username": os.environ['DEST_PC_USER'], "password": os.environ['DEST_PC_PASS']}

#dest_account_uuid = "1bf4ea28-fb88-4e53-a179-a9bde68d5f3f"
dest_account_uuid = os.environ['DEST_ACCOUNT_UUID']
dest_project = os.environ['DEST_PROJECT']
headers = {'content-type': 'application/json', 'Accept': 'application/json'}

def init_contexts():
    cfg = get_config()
    keyfile = cfg.get('security', 'keyfile')
    init_scramble(keyfile)
    set_session_type('green', cfg.get('store', 'flush_parallelisation_factor'), cfg.get('store', 'bulk_size'))
    create_db_connection(register_entities=False)

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

def get_vm(base_url, auth, uuid):
    method = 'GET'
    url = base_url + "/vms/{}".format(uuid)
 
    resp = requests.request(
            method,
            url,
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
    )
    if resp.ok:
        resp_json = resp.json()
        return resp_json
    else:
        log.info("Failed to get get VM '{}'.".format(uuid))
        log.info('Status code: {}'.format(resp.status_code))
        log.info('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        raise

def main():
    try:
        total_vms = 1
        offset = 0

        init_contexts()
        create_session()

        while offset < total_vms:
            vm_entities, total_vms = get_vm_list(dest_base_url, dest_pc_auth, offset)
        
            for vm in vm_entities:
                instance_id = vm["metadata"]["uuid"]
                NSE = model.NutanixSubstrateElement.query(instance_id=instance_id)
                if NSE:
                    NSE = NSE[0]
                    if NSE.spec.resources.account_uuid != dest_account_uuid:
                        print instance_id
                        vm_spec = get_vm(dest_base_url, dest_pc_auth, instance_id)
                        NSE.spec.resources.account_uuid = dest_account_uuid
                        NSE.spec.resources.cluster_uuid = vm_spec["status"]["cluster_reference"]["uuid"]
                        for i in range(len(NSE.spec.resources.nic_list)):
                            NSE.spec.resources.nic_list[i].nic_type = vm_spec["status"]["resources"]["nic_list"][i]["nic_type"]
                            NSE.spec.resources.nic_list[i].subnet_reference = vm_spec["status"]["resources"]["nic_list"][i]["subnet_reference"]
                            NSE.spec.resources.nic_list[i].ip_endpoint_list = vm_spec["status"]["resources"]["nic_list"][i]["ip_endpoint_list"]
                        NSE.save()
                        NS = NSE.replica_group
                        NS.spec.resources.account_uuid = dest_account_uuid
                        for i in range(len(NS.spec.resources.nic_list)):
                            NS.spec.resources.nic_list[i].nic_type = vm_spec["status"]["resources"]["nic_list"][i]["nic_type"]
                            NS.spec.resources.nic_list[i].subnet_reference = vm_spec["status"]["resources"]["nic_list"][i]["subnet_reference"]
                            NS.spec.resources.nic_list[i].ip_endpoint_list = vm_spec["status"]["resources"]["nic_list"][i]["ip_endpoint_list"]
                        NS.save()
                        NSC = NS.config
                        NSC.spec.resources.account_uuid = dest_account_uuid
                        for i in range(len(NSC.spec.resources.nic_list)):
                            NSC.spec.resources.nic_list[i].nic_type = vm_spec["status"]["resources"]["nic_list"][i]["nic_type"]
                            NSC.spec.resources.nic_list[i].subnet_reference = vm_spec["status"]["resources"]["nic_list"][i]["subnet_reference"]
                            NSC.spec.resources.nic_list[i].ip_endpoint_list = vm_spec["status"]["resources"]["nic_list"][i]["ip_endpoint_list"]
                        NSC.save()
                        flush_session()
                        app_name = model.Application.get_object(NSE.application_reference).name
                        change_project(app_name, dest_project)
            offset += LENGTH
    except Exception as e:
        log.info("Exception: %s" % e)
        raise

if __name__ == '__main__':
    main()