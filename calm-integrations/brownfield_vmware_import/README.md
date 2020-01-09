# Calm brownfield import of VMware VM's

## Pre-requisites:
* Python 3.x
* Calm 2.9.x

## Steps:
* Create a file 'vms_list' with list of VMware vm's (VM names).
* Update pc_ip, auth(username, password), project_name & account_namei in brownfield_vmware_import.py.
* Update linux_template_uuid & windows_template_uuid (not required post 2.9.7.1 upgrade) in brownfield_vmware_import.py.
* Install python "requests" module.
* Execute the script `python brownfield_vmware_import.py`
