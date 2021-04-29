#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import atexit
import ssl
import sys
import json

from pyVim import connect
from pyVmomi import vmodl,vim

from calm.common.flags import gflags

from calm.lib.model.store.db_session import flush_session
import calm.lib.model as model

from helper import change_project_vmware, init_contexts, log

if (
    'DEST_PROJECT_NAME' not in os.environ or
    'DEST_ACCOUNT_UUID' not in os.environ
    ):
    raise Exception("Please export 'DEST_PROJECT_NAME' & 'DEST_ACCOUNT_UUID'.")

if (
    'DEST_VC_IP' not in os.environ or
    'DEST_VC_USER' not in os.environ or
    'DEST_VC_PASS' not in os.environ or
    'DEST_VC_CLUSTER' not in os.environ
    ):
    raise Exception("Please export 'DEST_VC_IP', 'DEST_VC_CLUSTER', 'DEST_VC_USER' &  'DEST_VC_PASS'.")

DEST_VC_IP = os.environ['DEST_VC_IP']
DEST_PROJECT = os.environ['DEST_PROJECT_NAME']
DEST_VC_USER = os.environ['DEST_VC_USER']
DEST_VC_PASS = os.environ['DEST_VC_PASS']
DEST_VC_CLUSTER = os.environ['DEST_VC_CLUSTER']
DEST_ACCOUNT_UUID = os.environ['DEST_ACCOUNT_UUID']
#DEST_VC_CLUSTER = "Trunks4-Cluster"
#DEST_ACCOUNT_UUID = "aad91c45-ed5e-fa76-042a-4619a562d92e"

def ConnectVCenter():
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
        service_instance = connect.SmartConnect(
            host = DEST_VC_IP,
            user = DEST_VC_USER,
            pwd = DEST_VC_PASS,
            port=443,
            sslContext=context
        )
        if not service_instance:
            raise Exception("Could not connect to the specified host using specified "
                  "username and password")
        atexit.register(connect.Disconnect, service_instance)
        return service_instance
    except vmodl.MethodFault as e:
        log.info("Exception: %s" % e)
        raise
    

def update_substrate_info(vm, host_uuid):

    instance_id = vm.config.instanceUuid
    vm_name = vm.name
    datastore = [d.info.url for d in vm.datastore if d.info.url.startswith("ds:///vmfs/volumes")][0]

    NSE = model.SubstrateElement.query(instance_id=instance_id)
    if NSE:
        NSE = NSE[0]
        if NSE.spec.resources.account_uuid != DEST_ACCOUNT_UUID:
            log.info("Updating VM substrate for '{}' with instance_id '{}'.".format(vm_name, instance_id))
            NSE.spec.resources.account_uuid = DEST_ACCOUNT_UUID
            NSE.spec.datastore = datastore
            NSE.spec.host = host_uuid
            #NSE.platform_data = json.dumps(vm)
            #for i in range(len(NSE.spec.resources.nic_list)):
                #NSE.spec.resources.nic_list[i].net_name = "this should be net_name"
                #NSE.spec.resources.nic_list[i].nic_type = "this should be nic_type"
            for i in range(len(NSE.spec.resources.disk_list)):
                if NSE.spec.resources.disk_list[i].disk_type == "disk":
                    NSE.spec.resources.disk_list[i].location = datastore
            NSE.save()
            NS = NSE.replica_group
            NS.spec.resources.account_uuid = DEST_ACCOUNT_UUID
            NS.spec.datastore = datastore
            NS.spec.host = host_uuid
            #for i in range(len(NS.spec.resources.nic_list)):
                #NS.spec.resources.nic_list[i].net_name = "this should be net_name"
                #NS.spec.resources.nic_list[i].nic_type = "this should be nic_type"
            NS.save()
            NSC = NS.config
            NSC.spec.resources.account_uuid = DEST_ACCOUNT_UUID
            NSC.spec.datastore = datastore
            NSC.spec.host = host_uuid
            #for i in range(len(NSC.spec.resources.nic_list)):
                #NSC.spec.resources.nic_list[i].net_name = "this should be net_name"
                #NSC.spec.resources.nic_list[i].nic_type = "this should be nic_type"
            NSC.save()

def update_substrates():

    service_instance = ConnectVCenter()

    content = service_instance.RetrieveContent()
    object_view = content.viewManager.CreateContainerView(content.rootFolder, [], True)

    for obj in object_view.view:
        if isinstance(obj, vim.ComputeResource):
            if isinstance(obj, vim.ClusterComputeResource) and obj.name == DEST_VC_CLUSTER:
                for h in obj.host:
                    for vm in h.vm:
                        host_uuid = h.hardware.systemInfo.uuid
                        update_substrate_info(vm, host_uuid)
    flush_session()

def update_app_project():
    app_names = set()
    service_instance = ConnectVCenter()

    content = service_instance.RetrieveContent()
    object_view = content.viewManager.CreateContainerView(content.rootFolder, [], True)

    for obj in object_view.view:
        if isinstance(obj, vim.ComputeResource):
            if isinstance(obj, vim.ClusterComputeResource) and obj.name == DEST_VC_CLUSTER:
                for h in obj.host:
                    for vm in h.vm:
                        instance_id = vm.config.instanceUuid
                        NSE = model.SubstrateElement.query(instance_id=instance_id)
                        if NSE:
                            NSE = NSE[0]
                            app_name = model.AppProfileInstance.get_object(NSE.app_profile_instance_reference).application.name
                            app_names.add(app_name)

    for app_name in app_names:
        change_project_vmware(app_name, DEST_PROJECT)

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