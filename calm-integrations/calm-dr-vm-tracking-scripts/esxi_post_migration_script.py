#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from copy import deepcopy

from calm.common.flags import gflags

from aplos.insights.entity_capability import EntityCapability
from calm.lib.model.substrates.vmware import VcenterSubstrateElement
from helper import change_project_of_vmware_dr_apps, init_contexts, log, get_vm_source_dest_uuid_map, get_mh_vm
from calm.lib.model.tasks.vmware import VcenterVdiskInfo, VcenterVControllerInfo, VcenterNicInfo, VcenterFolderInfo, VcenterTagInfo
from calm.lib.model.store.db_session import flush_session
from calm.common.api_helpers.vmware_helper import get_vmware_resources

import calm.lib.model as model


REQUIRED_ATTRS = ['DEST_PC_IP', 'DEST_PC_USER', 'DEST_PC_PASS', 'SOURCE_PROJECT_NAME', 'DEST_ACCOUNT_NAME', 'DEST_PROJECT_NAME']
msg = ""
for attr in REQUIRED_ATTRS:
    if attr not in os.environ:
        msg = msg + attr + ", "
if msg:
    raise Exception("Please export {}". format(msg))

# constants
PC_PORT = 9440
LENGTH = 100
DR_KEY = "VM_VCENTER_UUID"
DEST_PROJECT = os.environ['DEST_PROJECT_NAME']
SRC_PROJECT = os.environ['SOURCE_PROJECT_NAME']
TEMPLATE_NAME = os.environ['TEMPLATE_NAME']
_TEMPLATE_UUID = ""

dest_base_url = "https://{}:{}/api/nutanix/v3".format(os.environ['DEST_PC_IP'], str(PC_PORT))
dest_pc_auth = {"username": os.environ['DEST_PC_USER'], "password": os.environ['DEST_PC_PASS']}



def get_vcenter_details(account_name):
    vcenter_details = {}
    account = model.Account.query(name=account_name)
    if account:
        account = account[0]
        vcenter_details["server"] = account.data.server
        vcenter_details["username"] = account.data.username
        vcenter_details["password"] =  account.data.password.blob
        vcenter_details["port"] =  account.data.port
        vcenter_details["datacenter"] =  account.data.datacenter
        vcenter_details["account_uuid"] = str(account.uuid)
    else:
        raise Exception("Could not find sepecified account {}".format(account_name))
    return vcenter_details


def get_template_id(vcenter_details):
    global _TEMPLATE_UUID
    if not _TEMPLATE_UUID:
        tmp_data = get_vmware_resources('template', {"account_uuid": vcenter_details["account_uuid"]})
        tmp_list = json.loads(tmp_data[0])
        tmp_map = {
            _t["name"]: _t["config.instanceUuid"] for _t in tmp_list
        }
        _TEMPLATE_UUID = tmp_map.get("TEMPLATE_NAME")
    return _TEMPLATE_UUID


def get_vm_path(content, vm_name):
    """
    Function to find the path of virtual machine.
    Args:
        content: VMware content object
        vm_name: virtual machine managed object

    Returns: Folder of virtual machine if exists, else None
    """
    folder_name = None
    folder = vm_name.parent
    if folder:
        folder_name = folder.name
        fp = folder.parent
        # climb back up the tree to find our path, stop before the root folder
        while fp is not None and fp.name is not None and fp != content.rootFolder:
            folder_name = fp.name + '/' + folder_name
            try:
                fp = fp.parent
            except BaseException:
                break
        folder_name = '/' + folder_name
    return folder_name

def get_vm_platform_data(vcenter_details, new_instance_id):
    """
    Function to get platform data of the vm
    Args:
        vcenter_details: vcenter_details
        new_instance_id: new_instance_id

    Returns: vm platform data
    """

    filters = {
        "uuid": new_instance_id,
        "account_uuid": vcenter_details["account_uuid"]
    }
    platform_data = get_vmware_resources('vm_detail', filters)
    return platform_data


def update_create_spec_object(create_spec, platform_data, vcenter_details):

    create_spec.resources.account_uuid = vcenter_details["account_uuid"]
    create_spec.datastore = platform_data["datastore"][0]["URL"]
    create_spec.host = platform_data["host"]
    create_spec.cluster = platform_data["cluster"]
    """create_spec.template = ""
    create_spec.resources.template_nic_list = []
    create_spec.resources.template_disk_list = []
    create_spec.resources.template_controller_list = []"""

    create_spec.template = get_template_id(vcenter_details)
    for _i in create_spec.resources.template_nic_list:
        _i.is_deleted = True
    for _i in create_spec.resources.template_disk_list:
        _i.is_deleted = True
    for _i in create_spec.resources.template_controller_list:
        _i.is_deleted = True

    # Treat all nics as normal nics
    create_spec.resources.nic_list = [VcenterNicInfo(net_name=pn.get('net_name', ''), nic_type=pn.get('nic_type', None))
                                  for pn in platform_data["nics"]]

    # Treat all disks as normal disks
    create_spec.resources.disk_list = [VcenterVdiskInfo(disk_size_mb=d.get('disk_size_mb', 0),
                                     disk_type=d.get('disk_type', None),
                                     controller_key=d.get('controller_key', None),
                                     device_slot=d.get('disk_slot', None),
                                     iso_path=d.get('iso_path', ""),
                                     adapter_type=d.get('adapter_type', None),
                                     location=d.get('location', None),
                                     disk_mode=d.get('disk_mode', None)) for d in platform_data["disks"]]
    
    # Treat all controllers as normal controllers
    create_spec.resources.controller_list = [VcenterVControllerInfo(controller_type=pc.get('controller_type', None),
                                                                bus_sharing=pc.get('bus_sharing', ""),
                                                                key=pc.get('key', -1)) for pc in
                                                                platform_data["controllers"]]

    # Move everything under existing path
    create_spec.folder = VcenterFolderInfo(existing_path=platform_data["folder"], new_path="", delete_empty_folder=False)

    # Adding tags
    create_spec.resources.tag_list = [VcenterTagInfo(tag_id=_tag) for _tag in platform_data.get("tags", [])]


def update_substrate_info(old_instance_id, new_instance_id, vcenter_details):

    sub_ele = VcenterSubstrateElement.query(instance_id=old_instance_id, deleted=False)
    if not sub_ele:
        return
    
    sub_ele = sub_ele[0]
    current_platform_data = json.loads(sub_ele.platform_data)
    new_platform_data = json.loads(get_vm_platform_data(vcenter_details, new_instance_id)[0])
    current_platform_data.update(new_platform_data)

    # update substrate element, clear all the snapshot info 
    sub_ele.platform_data = json.dumps(current_platform_data)
    sub_ele.instance_id = new_instance_id
    update_create_spec_object(sub_ele.spec, current_platform_data, vcenter_details)
    current_snapshot_ids = sub_ele.snapshot_info
    sub_ele.snapshot_info = []
    sub_ele.save()

    try:
        from calm.lib.model.snapshot_group import VcenterSnapshotInfo, VcenterSnapshotGroup
        for _id in current_snapshot_ids:
            db_snapshot_info = VcenterSnapshotInfo.fetch_one(snapshot_id=_id, substrate_element_reference=str(sub_ele.uuid))
            snapshot_info_id = db_snapshot_info.uuid
            snapshot_group_query = {
                'substrate_reference': str(sub_ele.replica_group_reference),
                'action_runlog_reference': str(db_snapshot_info['action_runlog_reference']),
            }
            db_snapshot_info.delete()
            snapshot_group = VcenterSnapshotGroup.fetch_one(**snapshot_group_query)
            if snapshot_group and snapshot_info_id:
                snapshot_group.update_snapshot_info_references(snapshot_info_id, "remove")
                if not snapshot_group.snapshots:
                    snapshot_group.delete()
    except Exception:
        pass

    # Get the substrate from substrate element
    log.info("Updating VM substrate for substrate element {}". format(str(sub_ele.uuid)))
    substrate = sub_ele.replica_group
    update_create_spec_object(substrate.spec, current_platform_data, vcenter_details)

    # update create action
    log.info("Updating 'create_Action' for substrate {}.".format(str(substrate.uuid)))
    for action in substrate.actions:
        if action.name == "action_create":
            for task in action.runbook.get_all_tasks():
                if task.type == "PROVISION_VCENTER":
                    update_create_spec_object(task.attrs, current_platform_data, vcenter_details)
                    task.save()
                    break
            break
    substrate.save()

    # Get the substrate config from substrate object
    log.info("Updating VM substrate config for substrate element {}". format(str(sub_ele.uuid)))
    sub_config = substrate.config
    update_create_spec_object(sub_config.spec, current_platform_data, vcenter_details)
    sub_config.save()

    # Updating intent spec
    application = model.AppProfileInstance.get_object(sub_ele.app_profile_instance_reference).application
    clone_bp = application.app_blueprint_config
    clone_bp_intent_spec_dict = json.loads(clone_bp.intent_spec)
    for _nic in current_platform_data["nics"]:
        _nic.pop("key", None)
    for _disk in current_platform_data["disks"]:
        _disk["device_slot"] = _disk.pop("disk_slot", -1)
        _disk.pop("key", None)
        _disk.pop("disk_name", None)
    for substrate_cfg in clone_bp_intent_spec_dict.get("resources").get("substrate_definition_list"):
        if substrate_cfg["uuid"] == str(sub_config.uuid):
            create_spec = substrate_cfg["create_spec"]
            create_spec["datastore"] = current_platform_data["datastore"][0]["URL"]
            create_spec["host"] = current_platform_data["host"]

            # NOTE: For now, we are template data, Just setting every attribute as deleted
            """create_spec["template"] = ""
            create_spec["resources"]["template_nic_list"] = []
            create_spec["resources"]["template_disk_list"] = []
            create_spec["resources"]["template_controller_list"] = []"""

            create_spec["template"] = get_template_id(vcenter_details)
            for _tnic in create_spec["resources"]["template_nic_list"]:
                _tnic["is_deleted"] = True
            for _tdisk in create_spec["resources"]["template_disk_list"]:
                _tdisk["is_deleted"] = True
            for _tcontroller in create_spec["resources"]["template_controller_list"]:
                _tcontroller["is_deleted"] = True
            create_spec["resources"]["nic_list"] = current_platform_data["nics"]
            create_spec["resources"]["disk_list"] = current_platform_data["disks"]
            create_spec["resources"]["controller_list"] = current_platform_data["controllers"]
            create_spec["resources"]["account_uuid"] = vcenter_details["account_uuid"]
    clone_bp.intent_spec = json.dumps(clone_bp_intent_spec_dict)
    clone_bp.save()

    # TODO update patch config action
    '''log.info("Updating patch config action for '{}' with instance_id '{}'.".format(current_platform_data["instance_name"], new_instance_id))
    for patch in application.active_app_profile_instance.patches:
        patch_config_attr = patch.attrs_list[0]
        patch_data = patch_config_attr.data

        if patch_config_attr.target == '''

def update_substrates(vm_uuid_map, vcenter_details):

    for older_vcenter_vm_uuid, newer_vcenter_vm_uuid in vm_uuid_map.items():

        # Update substrates using older_vcenter_vm_uuid
        try:
            update_substrate_info(older_vcenter_vm_uuid, newer_vcenter_vm_uuid, vcenter_details)
        except Exception as e:
            log.info("Failed to udpate substrate of {0}".format(older_vcenter_vm_uuid))
            log.info(e)
    flush_session()


def update_app_project(vm_uuid_map):
    app_names = set()
    app_kind = "app"

    for _, instance_id in vm_uuid_map.items():
        NSE = VcenterSubstrateElement.query(instance_id=instance_id, deleted=False)
        if NSE:
            NSE = NSE[0]
            app_name = model.AppProfileInstance.get_object(NSE.app_profile_instance_reference).application.name
            app_uuid = model.AppProfileInstance.get_object(NSE.app_profile_instance_reference).application.uuid
            entity_cap = EntityCapability(kind_name=app_kind, kind_id=str(app_uuid))
            if entity_cap.project_name == SRC_PROJECT:
                app_names.add(app_name)

    for app_name in app_names:
        change_project_of_vmware_dr_apps(app_name, DEST_PROJECT)


def main():
    try:

        init_contexts()

        # Get the account
        vcenter_details= get_vcenter_details(os.environ['DEST_ACCOUNT_NAME'])

        pc_vm_uuid_map = get_vm_source_dest_uuid_map(dest_base_url, dest_pc_auth)
        # This will contain pc-vm-uuid(source) to pc-vm-uuid(destination)

        calm_vm_uuid_map = {}
        for _, dpc_vm_uuid in pc_vm_uuid_map.items():
            dest_vm_data = get_mh_vm(dest_base_url, dest_pc_auth, dpc_vm_uuid)
            old_instance_uuid = dest_vm_data["metadata"].get("categories", {}).get(DR_KEY, "")
            new_instance_uuid = dest_vm_data["status"]["resources"]["hypervisor_specific_id"]
            if not (old_instance_uuid or new_instance_uuid):
                continue
            calm_vm_uuid_map[old_instance_uuid] = new_instance_uuid

        update_substrates(calm_vm_uuid_map, vcenter_details)

        update_app_project(calm_vm_uuid_map)

    except Exception as e:
        log.info("Exception: %s" % e)
        raise

if __name__ == '__main__':
    main()
