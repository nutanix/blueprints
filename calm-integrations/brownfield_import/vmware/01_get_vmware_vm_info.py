import argparse
import atexit
import ssl
import sys
from pyVim import connect
from pyVmomi import vmodl,vim
import requests
import csv

def help_parser():
    """
    Builds a standard argument parser with arguments for talking to vCenter

    -s service_host_name_or_ip
    -o optional_port_number
    -u required_user
    -p optional_password

    """
    parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to vCenter or ESXi')

    parser.add_argument('-s', '--vcenterip',
                        required=True,
                        action='store',
                        help='vSphere service to connect to')

    parser.add_argument('-d', '--clustername',
                        required=True,
                        action='store',
                        help='cluster name in VCenter datacenter')

    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to VCenter')

    parser.add_argument('-p', '--password',
                        required=True,
                        action='store',
                        help='Password to use when connecting to VCenter')

    return parser

def parse_service_instance(clustername, service_instance):
    '''
    :param service_instance:
    :return:
    '''

    content = service_instance.RetrieveContent()
    object_view = content.viewManager.CreateContainerView(content.rootFolder, [], True)
    vm_info_list = []
    vm_info_list.append(["virtual_machine_name","virtual_machine_uuid","virtual_machine_ip","num_cpu",
        "num_vcpus","memory_size","guest_family","host_uuid","datastore","power_state"])

    for obj in object_view.view:
        if isinstance(obj, vim.ComputeResource):
            if isinstance(obj, vim.ClusterComputeResource) and obj.name == clustername :
                #instance_name,instance_id,address,num_sockets,num_vcpus_per_socket,memory_size_mib,guestFamily,host_uuid, datastore
                for h in obj.host:
                    nic = h.config.network.vnic[0].spec
                    esxi_config = h.summary.config
                    #host_ip = h.summary.config.name
                    #host_id = str(h).split(":")[1][:-1]
                    host_uuid = h.hardware.systemInfo.uuid

                    for vx in h.vm:
                        if vx.summary.config.template is False:
                            ## Check if guestFullName contains `Windows` to determine the guest os is windows
                            ## otherwise we assumed that it is linux.
                            os = "Windows" if "Windows" in vx.summary.config.guestFullName else "Linux"
                            power_state = "poweron" if vx.runtime.powerState == "poweredOn" else "poweroff"

                            ## We assume here that guest os datastore will always have url start as `ds:///vmfs/volumes`
                            datastore =  [ d.info.url for d in vx.datastore if d.info.url.startswith("ds:///vmfs/volumes")]
                            vm_info  = [vx.name, vx.config.instanceUuid, vx.summary.guest.ipAddress,
                                vx.config.hardware.numCPU, vx.config.hardware.numCoresPerSocket,
                                vx.summary.config.memorySizeMB, os, host_uuid, datastore[0], power_state]

                            vm_info_list.append(vm_info)
    object_view.Destroy()

    with open("{}.csv".format(clustername), 'w') as file:
        writer = csv.writer(file)
        writer.writerows(vm_info_list)

def makeConnect(parser):
    """
    :return:
    """
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE

        service_instance = connect.SmartConnect(
            host=parser.vcenterip,
            user=parser.user,
            pwd=parser.password,
            port=parser.port,
            sslContext=context
        )
        if not service_instance:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1

        atexit.register(connect.Disconnect, service_instance)

        parse_service_instance(parser.clustername, service_instance)

    except vmodl.MethodFault as e:
        return -1
    return 0

def main():
    parser = help_parser()
    parser = parser.parse_args()
    content = makeConnect(parser)

if __name__ == '__main__':
    main()