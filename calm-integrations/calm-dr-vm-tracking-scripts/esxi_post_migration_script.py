#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

from copy import deepcopy
from calm.lib.model.substrates.vmware import VcenterSubstrateElement
from calm.cloud.vmware.vmware import VMware, get_virtual_disk_info, get_network_device_info
from calm.common.api_helpers.brownfield_helper import get_vcenter_vm
from helper import change_project, init_contexts, log, get_vm_source_dest_uuid_map, get_mh_vm
from calm.lib.model.tasks.vmware import VcenterVdiskInfo, VcenterVControllerInfo, VcenterNicInfo, VcenterFolderInfo
from pyVmomi import vim

import calm.lib.model as model


REQUIRED_ATTRS = ['DEST_PC_IP', 'DEST_PC_USER', 'DEST_PC_PASS', 'SOURCE_PROJECT_NAME', 'DEST_ACCOUNT_NAME']
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

    # Get the vcenter vm data
    handler = VMware(vcenter_details['data']['server'], vcenter_details['data']['username'],
                     vcenter_details['data']['password'], vcenter_details['data']['port'])

    try:
        vm = handler.get_vm_in_dc(vcenter_details['data']['datacenter'], new_instance_id)
    except:
        log.info("Couldn't find vm with uuid: {}". format(new_instance_id))

    folderPath = get_vm_path(handler.si.content, vm)

    # get the device list
    device_list = vm.config.hardware.device

    # Get the host id from host given
    vm_host_uuid = ""
    host_list = handler.get_hosts_list(vcenter_details['data']['datacenter'])
    for _host in host_list:
        if _host["name"] == vm.runtime.host.name:
            vm_host_uuid = _host["summary.hardware.uuid"]
            break

    # Get the protgroups for finding netname of nics
    pg_list = handler.get_portgroups(vcenter_details['data']['datacenter'], host_id=vm_host_uuid)
    pg_dict = {i["name"]: i["id"] for i in pg_list}
    nic_list = []
    vm_nic_info = get_network_device_info(device_list, handler.si.content)
    for _, dev in vm_nic_info.items():
        nic_list.append(
            {
                "nic_type": dev["nicType"],
                "key": dev["key"],
                "net_name": pg_dict[dev["backing.network.name"]]
            }
        )

    # controller_keys_map
    controller_list = []
    controller_keys_map = {"SCSI": [], "IDE": [], "SATA":[]}
    for i in device_list:
        controller_type = ""
        if isinstance(i, vim.vm.device.VirtualLsiLogicSASController):
            controller_type = "VirtualLsiLogicSASController"
        elif isinstance(i, vim.vm.device.VirtualLsiLogicController):
            controller_type = "VirtualLsiLogicController"
        elif isinstance(i, vim.vm.device.ParaVirtualSCSIController):
            controller_type = "ParaVirtualSCSIController"
        elif isinstance(i, vim.vm.device.VirtualAHCIController):
            controller_type = "VirtualAHCIController"
        elif isinstance(i, vim.vm.device.VirtualBusLogicController):
            controller_type = "VirtualBusLogicController"

        # Create controller_keys used in calculating disk data and controller data
        if isinstance(i, vim.vm.device.VirtualSCSIController):
            controller_keys_map["SCSI"].append(i.key)
            controller_list.append(
                {
                    "controller_type": controller_type,
                    "key": i.key,
                    "bus_sharing": i.sharedBus
                }
            )
        elif isinstance(i, vim.vm.device.VirtualIDEController):
            controller_keys_map["IDE"].append(i.key)
        elif isinstance(i, vim.vm.device.VirtualSATAController):
            controller_keys_map["SATA"].append(i.key)
            controller_list.append(
                {
                    "controller_type": controller_type,
                    "key": i.key,
                    "bus_sharing": ""
                }
            )

    disk_list = []
    vm_disk_info = get_virtual_disk_info(device_list)
    for _, dev in vm_disk_info.items():
        controller_key = dev.get("controllerKey")
        disk_type = dev.get("type")
        adapter_type = ""
        for _k, _v in controller_keys_map.items():
            if controller_key in _v:
                adapter_type = _k
                break
        disk_list.append(
            {
                "disk_size_mb": dev.get("capacityInBytes")/(1024*1024) if dev.get("capacityInBytes") else -1,
                "disk_slot": dev.get("unitNumber"),
                "controller_key": dev.get("controllerKey"),
                "location": dev.get("backing.datastore.url", ""),
                "disk_type": "disk" if disk_type == "VirtualDisk" else "cdrom",
                "adapter_type": adapter_type,
                "key": dev.get("key"),
                "disk_mode": dev.get("backing.diskMode"),
            }
        )

        if disk_type == "VirtualDisk":
            disk_list[-1]["disk_name"] = dev.get("backing.fileName", "")
        else:
            disk_list[-1]["disk_name"] = ""
            disk_list[-1]["iso_path"] = dev.get("backing.fileName", "")
            disk_list[-1]["disk_mode"] = "persistent"

    platformData = {
        "instance_uuid": new_instance_id,
        "instance_name": vm.name,
        "mob_id": vm._GetMoId(),
        "host": vm_host_uuid,
        "cluster": vm.runtime.host.parent.name,
        "runtime.powerState": vm.runtime.powerState,
        "ipAddressList": handler.get_ip_list(vcenter_details['data']['datacenter'], new_instance_id),
        "datastore": [
            {
                "Name": vm.datastore[0].name,
                "URL": vm.datastore[0].summary.url,
                "FreeSpace": vm.datastore[0].summary.freeSpace
            }
        ],
        "nics": nic_list,
        "disks": disk_list,
        "controllers": controller_list,
        "folder": folderPath
    }
    return platformData


def update_create_spec_object(create_spec, platform_data, vcenter_details):

    create_spec.resources.account_uuid = vcenter_details["account_uuid"]
    create_spec.datastore = platform_data["datastore"]["URL"]
    create_spec.host = platform_data["host"]
    create_spec.template = ""
    create_spec.resources.template_nic_list = []
    create_spec.resources.template_disk_list = []
    create_spec.resources.template_controller_list = []

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


def update_substrate(old_instance_id, new_instance_id, vcenter_details):

    sub_ele = VcenterSubstrateElement.query(instance_id=old_instance_id, deleted=False)
    if not sub_ele:
        return
    
    sub_ele = sub_ele[0]
    current_platform_data = json.loads(sub_ele.platform_data)
    new_platform_data = get_vm_platform_data(vcenter_details, new_instance_id)
    current_platform_data.update(new_platform_data)

    # update substrate element, clear all the snapshot info 
    sub_ele.platform_data = json.dumps(new_platform_data)
    update_create_spec_object(sub_ele.spec, new_platform_data, vcenter_details)
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
    update_create_spec_object(substrate.spec, new_platform_data, vcenter_details)

    # update create action
    log.info("Updating 'create_Action' for substrate {}.".format(str(substrate.uuid)))
    for action in substrate.actions:
        if action.name == "action_create":
            for task in action.runbook.get_all_tasks():
                if task.type == "PROVISION_VCENTER":
                    update_create_spec_object(task.attrs)
                    task.save()
                    break
            break
    substrate.save()

    # Get the substrate config from substrate object
    log.info("Updating VM substrate config for substrate element {}". format(str(sub_ele.uuid)))
    sub_config = substrate.config
    update_create_spec_object(sub_config.spec, new_platform_data, vcenter_details)
    sub_config.save()

    # Updating intent spec
    application = model.AppProfileInstance.get_object(sub_ele.app_profile_instance_reference).application
    clone_bp = application.app_blueprint_config
    clone_bp_intent_spec_dict = json.loads(clone_bp.intent_spec)
    for substrate_cfg in clone_bp_intent_spec_dict.get("resources").get("substrate_definition_list"):
        if substrate_cfg["uuid"] == str(sub_config.uuid):
            create_spec = substrate_cfg["create_spec"]
            create_spec["datastore"] = new_platform_data["datastore"]["URL"]
            create_spec["host"] = new_platform_data["host"]
            create_spec["template"] = ""
            create_spec["resources"]["template_nic_list"] = ""
            create_spec["resources"]["template_disk_list"] = ""
            create_spec["resources"]["template_controller_list"] = ""
            create_spec["resources"]["nic_list"] = deepcopy(new_platform_data["nics"])
            create_spec["resources"]["disk_list"] = deepcopy(new_platform_data["disks"])
            create_spec["resources"]["controller_list"] = deepcopy(new_platform_data["controllers"])
            create_spec["resources"]["account_uuid"] = vcenter_details["account_uuid"]
    clone_bp.intent_spec = json.dumps(clone_bp_intent_spec_dict)
    clone_bp.save()

    

    # update patch config action




    




def main():
    try:

        init_contexts()

        # Get the account
        vcenter_details= get_vcenter_details(os.environ['DEST_ACCOUNT_NAME'])

        vm_uuid_map = get_vm_source_dest_uuid_map(dest_base_url, dest_pc_auth)
        # This will contain pc-vm-uuid(source) to pc-vm-uuid(destination)

        for _, dest_pc_vm_uuid in vm_uuid_map.items():
            vm_data = get_mh_vm(dest_base_url, dest_pc_auth, dest_pc_vm_uuid)
            newer_vcenter_vm_uuid = vm_data["status"]["resources"]["hypervisor_specific_id"]
            older_vcenter_vm_uuid = vm_data["metadata"].get("categories", {}).get(DR_KEY, "")
            if not older_vcenter_vm_uuid:
                continue

            # Get substrate element using older vcenter vm uuid
            update_substrate(older_vcenter_vm_uuid, newer_vcenter_vm_uuid, vcenter_details)

        
        
        
        
    











        Need map for older vcenter-uuid to newer vcenter-uuid

        update_substrates(vm_uuid_map)


    
    except Exception as e:
        log.info("Exception: %s" % e)
        raise

if __name__ == '__main__':
    main()

