import sys, requests, json, re, uuid, time

pc_ip = '10.46.4.2'
auth = { "username": 'admin', "password": ''}
esxi_host_ip = "10.46.33.228"
project_name = "sample"
account_name = "vmware_regression"
parallel_process = 5
# Workaround: Any Linux and Windows template uuid #fixed in 2.9.7.1
linux_template_uuid = "50204284-5a62-9f9f-16c1-de61da074ee7"
windows_template_uuid = "5020b0fe-19fa-bbfe-0d94-844a9a4145d2"
base_url = "https://{}:9440/api/nutanix/v3".format(pc_ip)

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
            "type": "VMWARE_VM",
            "os_type": "Linux",
            "action_list": [],
            "create_spec": {
              "type": "PROVISION_VMWARE_VM",
              "name": "vm1",
              "datastore": "",
              "host": "",
              "resources": {
                "guest_customization": {
                  "customization_type": "GUEST_OS_LINUX"
                },
                "account_uuid": "",
                "num_vcpus_per_socket": 0,
                "num_sockets": 0,
                "memory_size_mib": 0,
                "nic_list": []
              }
            },
            "name": "VMSubstrate",
            "readiness_probe": {
              "disable_readiness_probe": True
            },
            "editables": {
              "create_spec": {
                "resources": {
                  "nic_list": {},
                  "controller_list": {},
                  "template_nic_list": {},
                  "template_controller_list": {},
                  "template_disk_list": {}
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
            "name": "VMware",
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

def get_single_vm_app_status(base_url, auth, application_uuid):
    method = 'GET'
    url = base_url + "/apps/{}".format(application_uuid)
    #print("Making a {} API call to {}".format(method, url))
    headers = {'content-type': 'application/json', 'Accept': 'application/json'}
    status = ""
    while True:
        resp = requests.request(
            method,
            url,
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )

        if resp.ok:
            json_resp = resp.json()
            status = json_resp["status"]["state"]
            return status
            #print("Received application status")
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(1)

### --------------------------------------------------------------------------------- ###

def esxi_brownfield_import(spec, vm_ip):
    vm_ip = vm_ip
    bp_name = "app-{}".format(vm_ip.replace(".", "-"))

    headers = {'content-type': 'application/json', 'Accept': 'application/json'}

    ### --------------------------------------------------------------------------------- ###
    def change_uuids(bp, context):
        """
        Helper function to change uuids
        Args:
            bp (dict): BP dict
            context (dict) : context to recursively change uuid references
        """
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
    def get_project_uuid(base_url, auth, project_name):
        method = 'POST'
        url = base_url + "/projects/list"
        payload = {
            "length":100,
            "offset":0,
            "filter":"name=={0}".format(project_name)
        }
        #print("Making a {} API call to {}".format(method, url))
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )

        if resp.ok:
            json_resp = resp.json()
            if json_resp['metadata']['total_matches'] > 0:
                project = json_resp['entities'][0]
                project_uuid = project["metadata"]["uuid"]
                return project_uuid
            else:
                print("Could not find project")
                sys.exit(1)
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(1)

    ### --------------------------------------------------------------------------------- ###

    ### --------------------------------------------------------------------------------- ###
    def get_vmware_account_uuid(base_url, auth, account_name):
        method = 'POST'
        url = base_url + "/accounts/list"
        payload = {
            "length":100,
            "offset":0,
            "filter":"name=={0};type==vmware".format(account_name)
        }
        #print("Making a {} API call to {}".format(method, url))
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )

        if resp.ok:
            json_resp = resp.json()
            if json_resp['metadata']['total_matches'] > 0:
                account = json_resp['entities'][0]
                return account["metadata"]["uuid"]
            else:
                print("Could not find account")
                exit(1)
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            exit(1)
    ### --------------------------------------------------------------------------------- ###

    ### --------------------------------------------------------------------------------- ###
    def get_hosts(base_url, auth, account_uuid):
        method = 'POST'
        url = base_url + "/vmware/v6/host/list"
        payload = {
            "length":100,
            "offset":0,
            "filter":"account_uuid=={0}".format(account_uuid)
        }
        #print("Making a {} API call to {}".format(method, url))
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )

        if resp.ok:
            json_resp = resp.json()
            host_dict = {}
            if len(json_resp['entities']) > 0:
                for host in json_resp['entities']:
                    ip = host['status']['resources']["name"]
                    host_dict[ip] = host['status']['resources']['summary']['hardware']['uuid']
                return host_dict
            else:
                print("No host found")
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(1)
    ### --------------------------------------------------------------------------------- ###

    ### --------------------------------------------------------------------------------- ###
    def get_host_datastore(base_url, auth, account_uuid, host_id):
        method = 'POST'
        url = base_url + "/vmware/v6/datastore/list"
        payload = {
            "length":100,
            "offset":0,
            "filter":"account_uuid=={0};host_id=={1}".format(account_uuid, host_id)
        }
        #print("Making a {} API call to {}".format(method, url))
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )

        if resp.ok:
            json_resp = resp.json()
            datastore_dict = {}
            if len(json_resp['entities']) > 0:
                for datastore in json_resp['entities']:
                    datastore_dict[datastore['status']['resources']['name']] = datastore['status']['resources']["summary"]["url"]
                return datastore_dict
            else:
                print("Could not find network for host {}.".format(host_id))
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(1)
    ### --------------------------------------------------------------------------------- ###

    ### --------------------------------------------------------------------------------- ###
    def get_brownfield_vms_list(base_url, auth, project_uuid, account_uuid, vm_ip):
        method = 'POST'
        url = base_url + "/blueprints/brownfield_import/vms/list"
        payload = {
            "length":100,
            "offset":0,
            "filter":"instance_name=={0};project_uuid=={1};account_uuid=={2}".format(vm_ip, project_uuid, account_uuid)
        }
        #print("Making a {} API call to {}".format(method, url))
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )
        ### It assumes that vm['status']['resources']['address'] will be list having only one ip.
        if resp.ok:
            json_resp = resp.json()
            brownfield_instance_list = []
            hardware_resources = {}
            datastore = ""
            if json_resp['metadata']['total_matches'] > 0:
                for vm in json_resp['entities']:
                    if vm["status"]["resources"]["instance_name"] == vm_ip:
                        vm_info = {
                            "instance_name": vm['status']['resources']['instance_name'],
                            "instance_id": vm['status']['resources']['instance_id'],
                            "address": vm['status']['resources']['address'],
                            "platform_data": {}
                        }
                        datastore = vm['status']['resources']['datastore']
                        hardware_resources = {
                            "num_sockets": vm['status']['resources']['config.hardware.numCPU'],
                            "num_vcpus_per_socket": vm['status']['resources']['config.hardware.numCoresPerSocket'],
                            "memory_size_mib" : vm['status']['resources']['summary.config.memorySizeMB'],
                            "guest": vm['status']['resources']['guest.guestFamily']
                        }
                        brownfield_instance_list.append(vm_info)

                if brownfield_instance_list:
                    return brownfield_instance_list, hardware_resources, datastore
                else:
                    print("Could not find brownfield vms.")
                    return brownfield_instance_list, hardware_resources, datastore
            else:
                print("Could not find brownfield vms.")
                return brownfield_instance_list, hardware_resources, datastore
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(1)
    ### --------------------------------------------------------------------------------- ###

    ### --------------------------------------------------------------------------------- ###
    def create_single_vm_bp(base_url, auth, payload):
        method = 'POST'
        url = base_url + "/blueprints"
        #print("Making a {} API call to {}".format(method, url))
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )

        if resp.ok:
            json_resp = resp.json()
            if json_resp["status"]["state"] != "ACTIVE":
                print("Blueprint state is not Active. It is : {}".format(json_resp["status"]["state"]))
                print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
                sys.exit(1)
            return json_resp
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(1)
    ### --------------------------------------------------------------------------------- ###

    ### --------------------------------------------------------------------------------- ###
    def launch_single_vm_bp(base_url, auth, blueprint_uuid, payload):
        method = 'POST'
        url = base_url + "/blueprints/{}/launch".format(blueprint_uuid)
        #print("Making a {} API call to {}".format(method, url))
        launch_request_uuid = ""
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )

        if resp.ok:
            json_resp = resp.json()
            launch_request_uuid = json_resp["status"]["request_id"]
            return launch_request_uuid
            print("Single VM Blueprint launched successfully")
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(1)

        method = GET
        url = base_url + "/blueprints/{}/pending_launches/{}".format(blueprint_uuid,launch_request_uuid)
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )
    ### --------------------------------------------------------------------------------- ###

    def get_single_vm_app_uuid(base_url, auth, launch_request_uuid):
        method = 'GET'
        url = base_url + "/blueprints/{}/pending_launches/{}".format(blueprint_uuid,launch_request_uuid)
        #print("Making a {} API call to {}".format(method, url))
        application_uuid = ""
        while True:
            resp = requests.request(
                method,
                url,
                headers=headers,
                auth=(auth["username"], auth["password"]),
                verify=False
            )

            if resp.ok:
                json_resp = resp.json()
                if json_resp["status"]["state"] == "failure":
                    return application_uuid
                if json_resp["status"]["state"] == "success":
                    application_uuid = json_resp["status"]["application_uuid"]
                    return application_uuid
                #print("Received application uuid")
            else:
                print("Request failed")
                print("Headers: {}".format(headers))
                print('Status code: {}'.format(resp.status_code))
                print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
                sys.exit(1)

    ### --------------------------------------------------------------------------------- ###
    ### Get project and account uuid
    project_uuid = get_project_uuid(base_url, auth, project_name)
    account_uuid = get_vmware_account_uuid(base_url, auth, account_name)
    application_uuid = ""

    ### Get host dict
    host_dict = get_hosts(base_url, auth, account_uuid)
    if esxi_host_ip not in host_dict.keys():
        print("Esxi Host '{}' not found.".format(esxi_host_ip))
        sys.exit(1)
    host_uuid = host_dict[esxi_host_ip]
    datastore_dict = get_host_datastore(base_url, auth, account_uuid, host_uuid)

    ### Get brownfield vms dict
    brownfield_instance_list, hardware_resources, datastore = get_brownfield_vms_list(base_url, auth, project_uuid, account_uuid, vm_ip)
    if len(brownfield_instance_list) == 0:
        return ""
    vm_name = brownfield_instance_list[0]["instance_name"]  #[0:25]

    datastore_location = ""
    for ds in datastore_dict:
        a = re.match(r".*({}).*".format(datastore_dict[ds]), datastore)
        if a != None:
            datastore_location = a.group(1)

    ### Update uuids, project ref, account ref, bp name, vm-info etc.
    updated_spec = change_uuids(spec, {})
    updated_spec["metadata"]["project_reference"]["uuid"] = project_uuid
    substrate = updated_spec["spec"]["resources"]["substrate_definition_list"][0]
    if hardware_resources["guest"] == "linuxGuest":
        template_uuid = linux_template_uuid
    else:
        template_uuid = windows_template_uuid
    substrate["create_spec"]["name"] = vm_name
    substrate["create_spec"]["host"] = host_uuid
    substrate["create_spec"]["template"] = template_uuid
    substrate["create_spec"]["datastore"] = datastore_location
    substrate["create_spec"]["resources"]["account_uuid"] = account_uuid
    substrate["create_spec"]["resources"]["num_vcpus_per_socket"] = hardware_resources["num_vcpus_per_socket"]
    substrate["create_spec"]["resources"]["num_sockets"] = hardware_resources["num_sockets"]
    substrate["create_spec"]["resources"]["memory_size_mib"] = hardware_resources["memory_size_mib"]

    updated_spec["spec"]["resources"]["substrate_definition_list"][0] = substrate
    updated_spec["spec"]["name"] = vm_name
    brownfield_instance_list[0]["instance_name"] = vm_name
    updated_spec["spec"]["resources"]["app_profile_list"][0]["deployment_create_list"][0]["brownfield_instance_list"] = brownfield_instance_list

    ### Create a single vm bp
    resp = create_single_vm_bp(base_url, auth, updated_spec)

    ### Update single vm bp spec
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
    launch_request_uuid = launch_single_vm_bp(base_url, auth, blueprint_uuid, resp)
    application_uuid = get_single_vm_app_uuid(base_url, auth, launch_request_uuid)
    return application_uuid

vms_ip = []
try:
    vm_names = open("vms_list", "r")
except IOError:
    print("ERROR: 'vms_list' File not found.")
    sys.exit(1)
finally:
    vms_ip = vm_names.read().splitlines()

total_matches = len(vms_ip)
count = 0

while (count < total_matches):
    apps_ids = {}
    first_item = count
    last_item = first_item + parallel_process
    if total_matches < last_item:
        last_item = total_matches
    number_of_executions = last_item-first_item
    success_fail_apps = 0
    for vm_ip in vms_ip[first_item:last_item]:
        print("Importing VM: {}".format(vm_ip))
        application_uuid = esxi_brownfield_import(BP_SPEC, vm_ip)
        if application_uuid == "":
            print("ERROR: Failed to import vm: {}".format(vm_ip))
            continue
        apps_ids[application_uuid] = "provisioning"
    count += parallel_process
    
    if len(apps_ids) < number_of_executions:
        number_of_executions = len(apps_ids)
    while True:
        for apps_id in apps_ids.keys():
            print("INFO: Checking application: {}".format(apps_id))
            if apps_ids[apps_id] == 'provisioning':
                status = get_single_vm_app_status(base_url, auth, apps_id)
                if status == 'running':
                    apps_ids[apps_id] = 'success'
                    print("INFO: Import success: {}.".format(apps_id))
                    success_fail_apps += 1
                elif status == 'provisioning':
                    print("INFO: Import in-progress: {}.".format(apps_id))
                else:
                    apps_ids[apps_id] = 'failed'
                    print("ERROR: Import failed {}.".format(apps_id))
                    success_fail_apps += 1
        if success_fail_apps == number_of_executions:
            break
        time.sleep(5)
