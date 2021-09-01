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

def get_vm(base_url, auth, uuid):
    method = 'GET'
    url = base_url + "/vms/{0}".format(uuid)
 
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
        log.info("Failed to get vms.")
        log.info('Status code: {}'.format(resp.status_code))
        log.info('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        raise Exception("Failed to get vms.")

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

def update_substrate_info(vm_uuid, vm, dest_account_uuid_map, vm_uuid_map):

    instance_id = vm_uuid
    vm_name = vm["status"]["name"]
    cluster_uuid = vm["status"]["cluster_reference"]["uuid"]
    NSE = model.NutanixSubstrateElement.query(instance_id=instance_id, deleted=False)
    if NSE:
        NSE = NSE[0]

        log.info("Updating VM substrate element for '{}' with instance_id '{}'.".format(vm_name, instance_id))
        if instance_id != vm_uuid_map[instance_id]:
            log.info("Updating 'instance_id' from '{}' to '{}'.".format(vm_name, instance_id, vm_uuid_map[instance_id]))
            NSE.instance_id = vm_uuid_map[instance_id]
            instance_id = vm_uuid_map[instance_id]

        NSE.spec.resources.account_uuid = dest_account_uuid_map[cluster_uuid]
        NSE.spec.resources.cluster_uuid = cluster_uuid
        NSE.platform_data = json.dumps(vm)
        for i in range(len(NSE.spec.resources.nic_list)):
            NSE.spec.resources.nic_list[i].nic_type = vm["status"]["resources"]["nic_list"][i]["nic_type"]
            NSE.spec.resources.nic_list[i].subnet_reference = vm["status"]["resources"]["nic_list"][i]["subnet_reference"]
            NSE.spec.resources.nic_list[i].ip_endpoint_list = vm["status"]["resources"]["nic_list"][i]["ip_endpoint_list"]
        NSE.save()

        log.info("Updating VM substrate for '{}' with instance_id '{}'.".format(vm_name, instance_id))
        NS = NSE.replica_group
        NS.spec.resources.account_uuid = dest_account_uuid_map[cluster_uuid]
        for i in range(len(NS.spec.resources.nic_list)):
            NS.spec.resources.nic_list[i].nic_type = vm["status"]["resources"]["nic_list"][i]["nic_type"]
            NS.spec.resources.nic_list[i].subnet_reference = vm["status"]["resources"]["nic_list"][i]["subnet_reference"]
            NS.spec.resources.nic_list[i].ip_endpoint_list = vm["status"]["resources"]["nic_list"][i]["ip_endpoint_list"]

        log.info("Updating 'create_Action' under substrate for '{}' with instance_id '{}'.".format(vm_name, instance_id))
        for action in NS.actions:
            if action.name == "action_create":
                for task in action.runbook.get_all_tasks():
                    if task.type == "PROVISION_NUTANIX":
                        for i, nic in enumerate(task.attrs.resources.nic_list):
                            nic.subnet_reference.uuid = vm["status"]["resources"]["nic_list"][i]["subnet_reference"]["uuid"]
                    task.save()
        NS.save()

        log.info("Updating VM substrate cfg for '{}' with instance_id '{}'.".format(vm_name, instance_id))
        NSC = NS.config
        NSC.spec.resources.account_uuid = dest_account_uuid_map[cluster_uuid]
        for i in range(len(NSC.spec.resources.nic_list)):
            NSC.spec.resources.nic_list[i].nic_type = vm["status"]["resources"]["nic_list"][i]["nic_type"]
            NSC.spec.resources.nic_list[i].subnet_reference = vm["status"]["resources"]["nic_list"][i]["subnet_reference"]
            NSC.spec.resources.nic_list[i].ip_endpoint_list = vm["status"]["resources"]["nic_list"][i]["ip_endpoint_list"]
        NSC.save()

        log.info("Updating VM clone blueprint for '{}' with instance_id '{}'.".format(vm_name, instance_id))
        application = model.AppProfileInstance.get_object(NSE.app_profile_instance_reference).application
        clone_bp = application.app_blueprint_config
        clone_bp_intent_spec_dict = json.loads(clone_bp.intent_spec)
        for substrate_cfg in clone_bp_intent_spec_dict.get("resources").get("substrate_definition_list"):
            nic_list = substrate_cfg.get("create_spec").get("resources").get("nic_list")
            for i, nic in enumerate(nic_list):
                nic["subnet_reference"] = vm["status"]["resources"]["nic_list"][i]["subnet_reference"]
            substrate_cfg["create_spec"]["resources"]["account_uuid"] = dest_account_uuid_map[cluster_uuid]

        clone_bp.intent_spec = json.dumps(clone_bp_intent_spec_dict)
        clone_bp.save()

def update_substrates(vm_uuid_map):

    dest_account_uuid_map = get_account_uuid_map()

    for vm_uuid in vm_uuid_map.keys():
        try:
            vm = get_vm(dest_base_url, dest_pc_auth, vm_uuid_map[vm_uuid])
            update_substrate_info(vm_uuid, vm, dest_account_uuid_map, vm_uuid_map)
        except Exception as e:
            log.info("Failed to udpate substrate of {0}".format(vm_uuid))
            log.info(e)

    flush_session()

def update_app_project(vm_uuid_map):
    app_names = set()
    
    for instance_id in vm_uuid_map.keys():
        NSE = model.NutanixSubstrateElement.query(instance_id=vm_uuid_map[instance_id], deleted=False)
        if NSE:
            NSE = NSE[0]
            app_name = model.AppProfileInstance.get_object(NSE.app_profile_instance_reference).application.name
            app_names.add(app_name)

    for app_name in app_names:
        change_project(app_name, DEST_PROJECT)

def get_recovery_plan_jobs_list(base_url, auth, offset):
    method = 'POST'
    url = base_url + "/recovery_plan_jobs/list"
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
            headers=headers,
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


def get_vm_source_dest_uuid_map():
    vm_source_dest_uuid_map = {}
    recovery_plan_jobs_list = []
    total_matches = 1
    offset = 0
    while offset < total_matches:
        entities, total_matches = get_recovery_plan_jobs_list(dest_base_url, dest_pc_auth, offset)
        for entity in entities:
            if (
                entity["status"]["resources"]["execution_parameters"]["action_type"] == "FAILOVER" and 
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
            if step_execution_status_src["operation_type"] == "ENTITY_RECOVERY":
                step_uuid = step_execution_status_src["step_uuid"]
                src_vm_uuid = step_execution_status_src["any_entity_reference_list"][0]["uuid"]
                for step_execution_status_dest in step_execution_status_list:
                    if (
                        step_execution_status_dest["parent_step_uuid"] == step_uuid and
                        step_execution_status_dest["operation_type"] == "ENTITY_RESTORATION"
                    ):
                        dest_vm_uuid = step_execution_status_dest["any_entity_reference_list"][0]["uuid"]
                vm_source_dest_uuid_map[src_vm_uuid] = dest_vm_uuid

    return vm_source_dest_uuid_map


def main():
    try:
        
        vm_uuid_map = get_vm_source_dest_uuid_map()

        init_contexts()

        update_substrates(vm_uuid_map)

        update_app_project(vm_uuid_map)

    except Exception as e:
        log.info("Exception: %s" % e)
        raise

if __name__ == '__main__':
    main()