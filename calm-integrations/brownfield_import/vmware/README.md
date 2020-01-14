# Calm brownfield import of VMware VM's

Calm Brownfield import scripts help customer to do bulk import of VMware Vm's.

- `01_get_vmware_vmn_info.py` Script takes VCenter host details and whitelisted vm's file as a input and create a metadata csv file with vm information esxi_vms_info_list.csv - (instance_name,instance_id,address,num_sockets,num_vcpus_per_socket,memory_size_mib,guestFamily,host_uuid,datastore_location)
- `02_brownfield_import.py` Script takes the above csv as input and import the vm's into CALM as brownfield apps.

## Pre-requisites:
* Calm 2.9.x
* VCenter

## Inputs for 01_get_vmware_vmn_info.py:
* --host - VCenter Host ip address
* --port - VCenter api port
* --user - VCenter Username
* --pass - Vcenter Password
* --dc - VCenter Datacenter
* --whitelist-vms - File path of whitelisted VCenter vm's to be imported

## Inputs for 02_brownfield_import.py:
* --pc - PC ip address
* --port - PC port
* --user - PC username
* --pass - PC password
* --project-name - PC project name
* --account-name - VCenter Account name
* --vm-info - File path of esxi_vms_info_list.csv

## Steps to Execute the script:
* Create a file with all the whitelisted vmware vm's.
* Execute below commands to generate whitelisted vm csv (esxi_vms_info_list.csv).
```shell
ssh user@<PC_IP>
sudo docker exec -it epsilon bash
cd /tmp
#copy paste contents of "01_get_vmware_vmn_info.py" to "01_get_vmware_vmn_info.py"
#copy paste contents of whitelisted vmware vm's to "whitelisted_vms"
activate
python 01_get_vmware_vmn_info.py --host <VCenter host ip> --port 443 --user <VCenter username> --pass <VCenter Password> --dc <VCenter Datacenter> --whitelist-vms <File path of whitelisted vm's>
```
* Copy the generated csv to any linux/windows vm with python 2.7.x installed (pip install requests too)
* Update linux_template_uuid & windows_template_uuid (not required post 2.9.7.1 upgrade) in 02_brownfield_import.py.
* Execute below commands to start import process.
```shell
python 02_brownfield_import.py --pc <PC ip address> --port <PC Port> --user <PC Username> --pass <PC Password> --project-name <CALM project name> --account-name <VMware project name in CALM> --vm-info /path/to/esxi_vms_info_list.csv
```
