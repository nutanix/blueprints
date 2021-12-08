import os, sys, json, re, uuid, time
import logging, argparse
import requests
logging.basicConfig(
        filename='brownfield_import.log',
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

headers = {'content-type': 'application/json', 'Accept': 'application/json'}

def help_parser():

    parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to vCenter or ESXi')
    parser.add_argument('--pc',
                        required=True,
                        action='store',
                        help='vSphere service to connect to')
    parser.add_argument('--port',
                        type=int,
                        default=9440,
                        action='store',
                        help='Port to connect on')
    parser.add_argument('--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to pc')
    parser.add_argument('--password',
                        required=True,
                        action='store',
                        help='Password to use when connecting to pc')
    parser.add_argument('--project',
                        required=True,
                        action='store',
                        help='CALM project name')
    parser.add_argument('--account',
                        required=True,
                        action='store',
                        help='CALM VMware account name')
    parser.add_argument('--vm-info',
                        required=False,
                        action='store',
                        help='File path of esxi vm metadata csv')
    parser.add_argument('-n', '--parallel',
                        type=int,
                        default=5,
                        action='store',
                        help='Number of parallel executions')
    return parser


BP_SPEC = {
    "api_version": "3.0",
    "metadata": {
      "kind": "blueprint",
      "categories": {
          "TemplateType": "Vm"
      },
      "project_reference": {
        "kind": "project",
        "uuid": ""
      },
      "uuid": "67ff4eaf-f7e3-4563-b1da-f42de3113402"
    },
    "spec": {
      "resources": {
        "substrate_definition_list": [
          {
            "variable_list": [],
            "type": "AHV_VM",
            "os_type": "Linux",
            "action_list": [],
            "create_spec": {
              "name": "vm-@@{calm_array_index}@@-@@{calm_time}@@",
              "resources": {
                "disk_list": [
                  {
                    "data_source_reference": {},
                    "device_properties": {
                      "device_type": "DISK",
                      "disk_address": {
                        "device_index": 0,
                        "adapter_type": "SCSI"
                      }
                    }
                  }
                ],
                "nic_list": [],
                "boot_config": {
                  "boot_device": {
                    "disk_address": {
                      "device_index": 0,
                      "adapter_type": "SCSI"
                    }
                  }
                },
                "account_uuid": ""
              },
              "categories": {}
            },
            "name": "VMSubstrate",
            "readiness_probe": {
              "disable_readiness_probe": True
            },
            "editables": {
              "create_spec": {
                "resources": {
                  "nic_list": {},
                  "serial_port_list": {}
                }
              }
            },
            "uuid": "61520e7a-67cc-e521-2853-fe249c92de18"
          }
        ],
        "client_attrs": {
        },
        "app_profile_list": [
          {
            "name": "AHV",
            "action_list": [],
            "variable_list": [],
            "deployment_create_list": [
              {
                "variable_list": [],
                "action_list": [],
                "min_replicas": "1",
                "name": "a7aadef7_deployment",
                "brownfield_instance_list": [
                  {
                  "instance_id": "",
                  "instance_name": "",
                  "address": [
                  ],
                  "platform_data": {}
                }
                ],
                "max_replicas": "1",
                "substrate_local_reference": {
                  "kind": "app_substrate",
                  "uuid": "61520e7a-67cc-e521-2853-fe249c92de18"
                },
                "type": "BROWNFIELD",
                "uuid": "48a70045-d71a-4486-0d03-e15a871372b5"
              }
            ],
            "uuid": "bc40ba37-6e84-49af-1ad3-280a5c3c1af4"
          }
        ],
        "type": "BROWNFIELD"
      },
      "name": ""
    }
}
### --------------------------------------------------------------------------------- ###
def whitelist_disk_objects(disk_list):
    updated_disk_list = []
    for disk in disk_list:
        if disk["device_properties"]["device_type"] == "CDROM":
            continue
        del disk["uuid"]
        del disk["disk_size_bytes"]
        del disk["storage_config"]
        updated_disk_list.append(disk)
    if "data_source_reference" not in updated_disk_list[0]:
        updated_disk_list[0]["data_source_reference"] = { "kind": "image", "uuid": "cce984f3-9160-409d-b966-9f30e556241d" } 

    return updated_disk_list

### --------------------------------------------------------------------------------- ###
def whitelist_nic_objects(nic_list):
    updated_nic_list = []
    for nic in nic_list:
        del nic["trunked_vlan_list"]
        del nic["is_connected"]
        del nic["uuid"]
        del nic["vlan_mode"]
        del nic["ip_endpoint_list"]
        updated_nic_list.append(nic)
    return updated_nic_list

### --------------------------------------------------------------------------------- ###
def create_open_file(file_name, file_operation):
    if not os.path.exists(file_name) and file_operation == "r":
        with open(file_name, 'w'): pass
    try:
        file = open(file_name, file_operation)
    except:
        logging.error("Failed to open file '{}' with operation '{}'.".format(file_name, file_operation))
        sys.exit(1)
    return file

### --------------------------------------------------------------------------------- ###
def get_vm_spec(vm_meta_info):
    vm_spec = {
        "instance_name": vm_meta_info["status"]["resources"]["instance_name"],
        "instance_id": vm_meta_info["status"]["resources"]["instance_id"],
        "address": vm_meta_info["status"]["resources"]["address"],
        "num_vcpus_per_socket" : vm_meta_info["status"]["resources"]["num_vcpus_per_socket"],
        "num_sockets" : vm_meta_info["status"]["resources"]["num_sockets"],
        "memory_size_mib" : vm_meta_info["status"]["resources"]["memory_size_mib"]
    }
    return vm_spec

### --------------------------------------------------------------------------------- ###
def get_brownfield_import_vms_list(base_url, auth, project_uuid, account_uuid, length):
    method = 'POST'
    url = base_url + "/blueprints/brownfield_import/vms/list"
    resp = None
    payload = {
        "length": length,
        "offset":0,
        "filter":"project_uuid=={};account_uuid=={}".format(project_uuid, account_uuid)
    }
    try:
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )
    except requests.exceptions.ConnectionError as e:
        logging.error("Failed to connect to PC: {}".format(e))
        sys.exit(1)
    finally:
        if resp.ok:
            json_resp = resp.json()
            if json_resp['metadata']['total_matches'] > 0:
                return resp.json()
            else:
                logging.error("No VM's available for import '{}'.".format(project_name))
                sys.exit(1)
        else:
            logging.error("Request failed")
            logging.error("Headers: {}".format(headers))
            logging.error('Status code: {}'.format(resp.status_code))
            logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(1)

### --------------------------------------------------------------------------------- ###
def get_project_uuid(base_url, auth, project_name):
    method = 'POST'
    url = base_url + "/projects/list"
    resp = None
    payload = {
        "length":100,
        "offset":0,
        "filter":"name=={0}".format(project_name)
    }
    try:
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )
    except requests.exceptions.ConnectionError as e:
        logging.error("Failed to connect to PC: {}".format(e))
        sys.exit(1)
    finally:
        if resp.ok:
            json_resp = resp.json()
            if json_resp['metadata']['total_matches'] > 0:
                project = json_resp['entities'][0]
                project_uuid = project["metadata"]["uuid"]
                return project_uuid
            else:
                logging.error("Could not find project '{}'.".format(project_name))
                sys.exit(1)
        else:
            logging.error("Request failed")
            logging.error("Headers: {}".format(headers))
            logging.error('Status code: {}'.format(resp.status_code))
            logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(1)

### --------------------------------------------------------------------------------- ###
def get_ahv_account_uuid(base_url, auth, account_name):
    method = 'POST'
    url = base_url + "/accounts/list"
    payload = {
        "length":100,
        "offset":0,
        "filter":"name=={0}".format(account_name)
    }
    try:
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )
    except requests.exceptions.ConnectionError as e:
        logging.error("Failed to connect to PC: {}".format(e))
        sys.exit(1)
    finally:
        if resp.ok:
            json_resp = resp.json()
            if json_resp['metadata']['total_matches'] > 0:
                account = json_resp['entities'][0]
                return account["status"]["resources"]["data"]["cluster_account_reference_list"][0]["uuid"], account["status"]["resources"]["data"]["server"]
            else:
                logging.error("Could not find account '{}'".format(account_name))
                sys.exit(1)
        else:
            logging.error("Request failed")
            logging.error("Headers: {}".format(headers))
            logging.error('Status code: {}'.format(resp.status_code))
            logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(1)

### --------------------------------------------------------------------------------- ###
def get_single_vm_app_status(base_url, auth, application_uuid):
    method = 'GET'
    url = base_url + "/apps/{}".format(application_uuid)
    status = ""
    while True:
        try:
            resp = requests.request(
                method,
                url,
                headers=headers,
                auth=(auth["username"], auth["password"]),
                verify=False
            )
        except requests.exceptions.ConnectionError as e:
            logging.error("Failed to connect to PC: {}".format(e))
            return ""
        finally:
            if resp.ok:
                json_resp = resp.json()
                status = json_resp["status"]["state"]
                return status
            else:
                logging.error("Request failed")
                logging.error("Headers: {}".format(headers))
                logging.error('Status code: {}'.format(resp.status_code))
                logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
                return ""


def ahv_brownfield_import(spec, vm_spec, project_uuid, account_uuid, account_pc_ip):
    application_uuid = ""

    ### --------------------------------------------------------------------------------- ###
    def change_uuids(bp, context):
        if isinstance(bp, dict):
            for key, val in bp.items():
                if key == 'uuid':
                    old_uuid = val
                    if old_uuid in context:
                        bp[key] = context[old_uuid]
                    else:
                        new_uuid = str(uuid.uuid4())
                        context[old_uuid] = new_uuid
                        bp[key] = new_uuid
                else:
                    change_uuids(val, context)
        elif isinstance(bp, list):
            for item in bp:
                if isinstance(item, str):
                    try:
                        uuid.UUID(hex=str(item), version=4)
                    except Exception:
                        change_uuids(item, context)
                        continue
                    old_uuid = item
                    if old_uuid in context:
                        new_uuid = context[old_uuid]
                        bp[bp.index(item)] = new_uuid
                    else:
                        new_uuid = str(uuid.uuid4())
                        context[old_uuid] = new_uuid
                        bp[bp.index(item)] = new_uuid
                else:
                    change_uuids(item, context)
        return bp

    ### --------------------------------------------------------------------------------- ###
    def get_vm(base_url, auth, vm_uuid):
        method = 'GET'
        url = base_url + "/vms/{}".format(vm_uuid)
        
        try:
            resp = requests.request(
                method,
                url,
                headers=headers,
                auth=(auth["username"], auth["password"]),
                verify=False
            )
        except requests.exceptions.ConnectionError as e:
            logging.error("ERROR: Failed to connect to PC: {}".format(e))
            return False, None
        finally:
            if resp.ok:
                return True, resp.json()
            else:
                logging.error("Request failed")
                logging.error("Headers: {}".format(headers))
                logging.error('Status code: {}'.format(resp.status_code))
                logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
                return False, None

    ### --------------------------------------------------------------------------------- ###
    def create_single_vm_bp(base_url, auth, payload):
        method = 'POST'
        url = base_url + "/blueprints"
        try:
            resp = requests.request(
                method,
                url,
                data=json.dumps(payload),
                headers=headers,
                auth=(auth["username"], auth["password"]),
                verify=False
            )
        except requests.exceptions.ConnectionError as e:
            logging.error("Failed to connect to PC: {}".format(e))
            return False, ""
        finally:
            if resp.ok:
                json_resp = resp.json()
                if json_resp["status"]["state"] != "ACTIVE":
                    logging.error("Blueprint state is not Active. It is : {}".format(json_resp["status"]["state"]))
                    return False, json_resp
                return True, json_resp
            else:
                logging.error("Request failed")
                logging.error("Headers: {}".format(headers))
                logging.error('Status code: {}'.format(resp.status_code))
                logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
                return False, ""

    ### --------------------------------------------------------------------------------- ###
    def launch_single_vm_bp(base_url, auth, blueprint_uuid, payload):
        method = 'POST'
        url = base_url + "/blueprints/{}/launch".format(blueprint_uuid)
        launch_request_uuid = ""
        try:
            resp = requests.request(
                method,
                url,
                data=json.dumps(payload),
                headers=headers,
                auth=(auth["username"], auth["password"]),
                verify=False
            )
        except requests.exceptions.ConnectionError as e:
            logging.error("ERROR: Failed to connect to PC: {}".format(e))
            return False, launch_request_uuid
        finally:
            if resp.ok:
                json_resp = resp.json()
                launch_request_uuid = json_resp["status"]["request_id"]
                return True, launch_request_uuid
            else:
                logging.error("Request failed")
                logging.error("Headers: {}".format(headers))
                logging.error('Status code: {}'.format(resp.status_code))
                logging.error('Response: {}'.format(resp.content))
                return False, launch_request_uuid

    ### --------------------------------------------------------------------------------- ###
    def get_single_vm_app_uuid(base_url, auth, launch_request_uuid):
        method = 'GET'
        url = base_url + "/blueprints/{}/pending_launches/{}".format(blueprint_uuid,launch_request_uuid)
        application_uuid = ""
        while True:
            try:
                resp = requests.request(
                    method,
                    url,
                    headers=headers,
                    auth=(auth["username"], auth["password"]),
                    verify=False
                )
            except requests.exceptions.ConnectionError as e:
                logging.error("ERROR: Failed to connect to PC: {}".format(e))
                return False, application_uuid
            finally:
                if resp.ok:
                    json_resp = resp.json()
                    if json_resp["status"]["state"] == "failure":
                        return False, application_uuid
                    if json_resp["status"]["state"] == "success":
                        application_uuid = json_resp["status"]["application_uuid"]
                        return True, application_uuid
                else:
                    logging.error("Request failed")
                    logging.error("Headers: {}".format(headers))
                    logging.error('Status code: {}'.format(resp.status_code))
                    logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
                    return False, application_uuid

    ### --------------------------------------------------------------------------------- ###

    ### Update uuids, project ref, account ref, bp name, vm-info etc.
    updated_spec = change_uuids(spec, {})
    accounts_pc_base_url = "https://{}:{}/api/nutanix/v3".format(account_pc_ip,str(pc_port))
    get_vm_status, vm_get_json = get_vm(accounts_pc_base_url, auth, vm_spec["instance_id"])
    if get_vm_status != True:
        return False, vm_get_json
    updated_spec["metadata"]["project_reference"]["uuid"] = project_uuid

    substrate = updated_spec["spec"]["resources"]["substrate_definition_list"][0]
    substrate["create_spec"]["name"] = vm_spec["instance_name"]
    substrate["create_spec"]["categories"] = vm_get_json["metadata"]["categories"]
    substrate["create_spec"]["resources"]["account_uuid"] = account_uuid
    substrate["create_spec"]["resources"]["num_vcpus_per_socket"] = vm_spec["num_vcpus_per_socket"]
    substrate["create_spec"]["resources"]["num_sockets"] = vm_spec["num_sockets"]
    substrate["create_spec"]["resources"]["memory_size_mib"] = vm_spec["memory_size_mib"]
    substrate["create_spec"]["resources"]["disk_list"] = whitelist_disk_objects(vm_get_json["status"]["resources"]["disk_list"])
    substrate["create_spec"]["resources"]["nic_list"] = whitelist_nic_objects(vm_get_json["status"]["resources"]["nic_list"])

    brownfield_instance = updated_spec["spec"]["resources"]["app_profile_list"][0]["deployment_create_list"][0]["brownfield_instance_list"][0]
    brownfield_instance["instance_name"] = vm_spec["instance_name"]
    brownfield_instance["instance_id"] = vm_spec["instance_id"]
    brownfield_instance["address"] = vm_spec["address"]
    brownfield_instance["platform_data"] = {}

    updated_spec["spec"]["resources"]["substrate_definition_list"][0] = substrate
    updated_spec["spec"]["resources"]["app_profile_list"][0]["deployment_create_list"][0]["brownfield_instance_list"][0] = brownfield_instance
    updated_spec["spec"]["name"] = vm_spec["instance_name"].replace(" ", "_")

    ### Create a single vm bp
    create_status, resp = create_single_vm_bp(base_url, auth, updated_spec)
    if create_status != True:
        return False, resp

    ### Update single vm bp spec to launch
    del resp["status"]
    blueprint_uuid = resp["metadata"]["uuid"]

    app_uuid = resp["spec"]["resources"]["app_profile_list"][0]["uuid"]
    resp["spec"]["application_name"] =  resp["spec"]["name"]
    resp["spec"]["app_profile_reference"] = {
        "kind": "app_profile",
        "uuid": app_uuid
    }

    del resp["spec"]["name"]

    ### Launch a single vm bp
    launch_request_status, launch_request_uuid = launch_single_vm_bp(base_url, auth, blueprint_uuid, resp)
    if launch_request_status != True:
        return False, launch_request_uuid
    app_uuid_status, application_uuid = get_single_vm_app_uuid(base_url, auth, launch_request_uuid)
    if app_uuid_status != True:
        return False, application_uuid
    return True, application_uuid

if __name__ == "__main__":
    parser = help_parser().parse_args()
    pc_ip = parser.pc
    pc_port = parser.port
    base_url = "https://{}:{}/api/nutanix/v3".format(pc_ip,str(pc_port))
    auth = { "username": parser.user, "password": parser.password}
    project_name = parser.project
    account_name = parser.account
    file_path = parser.vm_info
    parallel_process = parser.parallel
    whitelist_vms = "vm-"

    project_uuid = get_project_uuid(base_url, auth, project_name)
    account_uuid, accounts_pc_ip = get_ahv_account_uuid(base_url, auth, account_name)
    if project_uuid == "" or account_uuid == "" or accounts_pc_ip == "":
        logging.error("Failed to get project or account details.")
        sys.exit(1)
    logging.info("Project uuid: {}".format(project_uuid))
    logging.info("Account uuid: {}".format(account_uuid))
    logging.info("Account PCIP: {}".format(accounts_pc_ip))
    vm_import_list = get_brownfield_import_vms_list(base_url, auth, project_uuid, account_uuid, 5)
    total_matches = vm_import_list['metadata']['total_matches']
    logging.info("VM's to be imported are: {}".format(total_matches))

    count = 0
    while (count < total_matches):
        apps_ids = {}
        first_item = count
        last_item = first_item + parallel_process
        if total_matches < last_item:
            last_item = total_matches
        number_of_executions = last_item-first_item
        success_fail_apps = 0
        count += number_of_executions
        vm_input_list = get_brownfield_import_vms_list(base_url, auth, project_uuid, account_uuid, parallel_process)
 
        for vm_meta_info in vm_input_list["entities"]:
            vm_spec = get_vm_spec(vm_meta_info)
            if whitelist_vms in vm_spec["instance_name"].lower():
                logging.info("Importing VM: '{}' ({}) '{}'".format(vm_spec["instance_name"], vm_spec["address"][0], vm_spec["instance_id"]))
                launch_status, application_uuid = ahv_brownfield_import(BP_SPEC, vm_spec, project_uuid, account_uuid, accounts_pc_ip)
                if launch_status != True:
                    logging.error("Import failed: {}.".format(vm_spec["instance_name"]))
                    continue
                apps_ids[application_uuid] = { "name" : vm_spec["instance_name"], "state" : "provisioning", "ip" : vm_spec["address"][0]}
        if len(apps_ids) < number_of_executions:
            number_of_executions = len(apps_ids)
        while True:
            for apps_id in apps_ids.keys():
                if apps_ids[apps_id]["state"] == 'provisioning':
                    status = get_single_vm_app_status(base_url, auth, apps_id)
                    logging.info("Checking application '{}' ({}) status.".format(apps_ids[apps_id]["name"], apps_ids[apps_id]["ip"]))
                    if status == 'running':
                        apps_ids[apps_id]["state"] = 'success'
                        logging.info("Application '{}' ({}) import successful.".format(apps_ids[apps_id]["name"], apps_ids[apps_id]["ip"]))
                        success_fail_apps += 1
                    elif status == "failed":
                        apps_ids[apps_id]["state"] = 'failed'
                        logging.error("Application '{}' ({}) import failed.".format(apps_ids[apps_id]["name"], apps_ids[apps_id]["ip"]))
                        success_fail_apps += 1
                    elif status == "error":
                        apps_ids[apps_id]["state"] = 'error'
                        logging.error("Application '{}' ({}) import failed.".format(apps_ids[apps_id]["name"], apps_ids[apps_id]["ip"]))
                        success_fail_apps += 1
            if success_fail_apps == number_of_executions:
                logging.info("Completed ({}/{}) applications.".format(count, total_matches))
                break
            time.sleep(10)
    logging.info("Completed brownfield import.")