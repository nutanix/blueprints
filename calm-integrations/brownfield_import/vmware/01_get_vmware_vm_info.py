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

    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='vSphere service to connect to')

    parser.add_argument('-d', '--datacenter',
                        required=True,
                        action='store',
                        help='Datacenter to connect  to')

    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=True,
                        action='store',
                        help='Password to use when connecting to host')

    return parser

def parse_service_instance(datacenter, service_instance):
    '''
    :param service_instance:
    :return:
    '''

    content = service_instance.RetrieveContent()
    object_view = content.viewManager.CreateContainerView(content.rootFolder, [], True)
    vm_info_list = []

    for obj in object_view.view:
        if isinstance(obj, vim.ComputeResource):
            if isinstance(obj, vim.ClusterComputeResource) and obj.name == datacenter :

                #print('VcenterCluster: {}'.format(obj.name))
                #instance_name,instance_id,address,num_sockets,num_vcpus_per_socket,memory_size_mib,guestFamily,host_ip, host_id, host_uuid, datastore
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

                            ## We assume here that guest os datastore will always have url start as `ds:///vmfs/volumes`
                            datastore =  [ d.info.url for d in vx.datastore if d.info.url.startswith("ds:///vmfs/volumes")]
                            vm_info  = [vx.name, vx.config.instanceUuid, vx.summary.guest.ipAddress,
                                vx.config.hardware.numCPU, vx.config.hardware.numCoresPerSocket,
                                vx.summary.config.memorySizeMB, os, host_uuid, datastore[0]]

                            vm_info_list.append(vm_info)
    object_view.Destroy()


    with open('esxi_vms_info_list.csv', 'w') as file:
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
            host=parser.host,
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

        # ## Do the actual parsing of data ## #
        parse_service_instance(parser.datacenter, service_instance)

    except vmodl.MethodFault as e:
        return -1
    return 0

def main():
    parser = help_parser()
    parser = parser.parse_args()
    content = makeConnect(parser)

if __name__ == '__main__':
    main()