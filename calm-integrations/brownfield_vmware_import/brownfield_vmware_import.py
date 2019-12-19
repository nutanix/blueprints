
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

def esxi_single_vm_run(spec):

    pc_ip = '@@{pc_ip}@@'
    auth = { "username": '@@{pc_cred.username}@@', "password": '@@{pc_cred.secret}@@'}
    base_url = "https://{}:9440/api/nutanix/v3".format(pc_ip)

    vm_ip = "@@{vm_ip}@@"
    host_ip = "@@{host_ip}@@"
    bp_name = "app-{}".format(vm_ip.replace(".", "-"))
    project_name = "@@{project_name}@@"
    account_name = "@@{account_name}@@"

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
            for key, val in bp.iteritems():
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
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(
            url,
            verb=method,
            params=json.dumps(payload),
            headers=headers,
            auth='BASIC',
            user=auth["username"],
            passwd=auth["password"],
            verify=False
        )

        if resp.ok:
            json_resp = json.loads(resp.content)
            if json_resp['metadata']['total_matches'] > 0:
                project = json_resp['entities'][0]
                return project["metadata"]["uuid"]
            else:
                print("Could not find project")
                exit(1)
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            exit(1)
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
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(
            url,
            verb=method,
            params=json.dumps(payload),
            headers=headers,
            auth='BASIC',
            user=auth["username"],
            passwd=auth["password"],
            verify=False
        )

        if resp.ok:
            json_resp = json.loads(resp.content)
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
    def get_hosts(base_url, auth, account_uuid):
        method = 'POST'
        url = base_url + "/vmware/v6/host/list"
        payload = {
            "length":100,
            "offset":0,
            "filter":"account_uuid=={0}".format(account_uuid)
        }
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(
            url,
            verb=method,
            params=json.dumps(payload),
            headers=headers,
            auth='BASIC',
            user=auth["username"],
            passwd=auth["password"],
            verify=False
        )

        if resp.ok:
            json_resp = json.loads(resp.content)
            host_dict = {}
            if len(json_resp['entities']) > 0:
                for host in json_resp['entities']:
                    ip = host['status']['resources']["name"]
                    host_dict[ip] = host['status']['resources']['summary']['hardware']['uuid']
                    #id = host['status']['resources']['summary']['hardware']['uuid']
                    #host_dict[id] = host['status']['resources']["name"]
                return host_dict
            else:
                print("No host found")
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            exit(1)
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
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(
            url,
            verb=method,
            params=json.dumps(payload),
            headers=headers,
            auth='BASIC',
            user=auth["username"],
            passwd=auth["password"],
            verify=False
        )

        if resp.ok:
            json_resp = json.loads(resp.content)
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
            exit(1)
    ### --------------------------------------------------------------------------------- ###

    ### --------------------------------------------------------------------------------- ###
    def get_brownfield_vms_list(base_url, auth, project_uuid, account_uuid, vm_ip):
        method = 'POST'
        url = base_url + "/blueprints/brownfield_import/vms/list"
        payload = {
            "length":100,
            "offset":0,
            "filter":"guest.ipAddress=={0};project_uuid=={1};account_uuid=={2}".format(vm_ip, project_uuid, account_uuid)
        }
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(
            url,
            verb=method,
            params=json.dumps(payload),
            headers=headers,
            auth='BASIC',
            user=auth["username"],
            passwd=auth["password"],
            verify=False
        )
        ### It assumes that vm['status']['resources']['address'] will be list having only one ip.
        if resp.ok:
            json_resp = json.loads(resp.content)
            brownfield_instance_list = []
            vm_host = ""
            datastore = ""
            if json_resp['metadata']['total_matches'] > 0:
                for vm in json_resp['entities']:
                    print("IP: ", vm['status']['resources']['guest.ipAddress'])
                    if len(set(vm['status']['resources']['guest.ipAddress']) & set([vm_ip])) > 0:
                        vm_info = {
                            "instance_name": vm['status']['resources']['instance_name'],
                            "instance_id": vm['status']['resources']['instance_id'],
                            "address": vm['status']['resources']['address'],
                            "platform_data": {}
                        }
                        datastore = vm['status']['resources']['datastore']
                        hardware_resources = {
                            "numCPU": vm['status']['resources']['config.hardware.numCPU'],
                            "numCoresPerSocket": vm['status']['resources']['config.hardware.numCoresPerSocket'],
                            "memorySizeMB" : vm['status']['resources']['summary.config.memorySizeMB']
                        }
                        brownfield_instance_list.append(vm_info)

                if brownfield_instance_list:
                    return brownfield_instance_list, hardware_resources, datastore
                else:
                    print("Could not find brownfield vms.")
                    exit(1)
            else:
                print("Could not find brownfield vms.")
                exit(1)
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            exit(1)
    ### --------------------------------------------------------------------------------- ###

    ### --------------------------------------------------------------------------------- ###
    def create_single_vm_bp(base_url, auth, payload):
        method = 'POST'
        url = base_url + "/blueprints"
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(
            url,
            verb=method,
            params=json.dumps(payload),
            headers=headers,
            auth='BASIC',
            user=auth["username"],
            passwd=auth["password"],
            verify=False
        )

        if resp.ok:
            json_resp = json.loads(resp.content)
            if json_resp["status"]["state"] != "ACTIVE":
                print("Blueprint state is not Active. It is : {}".format(json_resp["status"]["state"]))
                print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
                exit(1)
            return json_resp
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            exit(1)
    ### --------------------------------------------------------------------------------- ###

    ### --------------------------------------------------------------------------------- ###
    def launch_single_vm_bp(base_url, auth, blueprint_uuid, payload):
        method = 'POST'
        url = base_url + "/blueprints/{}/launch".format(blueprint_uuid)
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(
            url,
            verb=method,
            params=json.dumps(payload),
            headers=headers,
            auth='BASIC',
            user=auth["username"],
            passwd=auth["password"],
            verify=False
        )

        if resp.ok:
            json_resp = json.loads(resp.content)
            print("Single VM Blueprint launched successfully")
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            exit(1)
    ### --------------------------------------------------------------------------------- ###

    ### Get project and account uuid
    project_uuid = get_project_uuid(base_url, auth, project_name)
    account_uuid = get_vmware_account_uuid(base_url, auth, account_name)

    ### Get host dict
    host_dict = get_hosts(base_url, auth, account_uuid)
    host_uuid = host_dict[host_ip]
    
    datastore_dict = get_host_datastore(base_url, auth, account_uuid, host_uuid)

    ### Get brownfield vms dict
    brownfield_instance_list, hardware_resources, datastore = get_brownfield_vms_list(base_url, auth, project_uuid, account_uuid, vm_ip)
    vm_name = brownfield_instance_list[0]["instance_name"][0:25]

    datastore_location = ""
    for ds in datastore_dict:
        a = re.match(r".*({}).*".format(datastore_dict[ds]), datastore)
        if a != None:
            datastore_location = a.group(1)

    ### Update uuids, project ref, account ref, bp name, vm-info etc.
    updated_spec = change_uuids(spec, {})
    updated_spec["metadata"]["project_reference"]["uuid"] = project_uuid
    substrate = updated_spec["spec"]["resources"]["substrate_definition_list"][0]

    substrate["create_spec"]["name"] = vm_name
    substrate["create_spec"]["host"] = host_uuid
    substrate["create_spec"]["datastore"] = datastore_location
    substrate["create_spec"]["resources"]["account_uuid"] = account_uuid
    substrate["create_spec"]["resources"]["num_vcpus_per_socket"] = hardware_resources["numCoresPerSocket"]
    substrate["create_spec"]["resources"]["num_sockets"] = hardware_resources["numCPU"]
    substrate["create_spec"]["resources"]["memory_size_mib"] = hardware_resources["memorySizeMB"]

    updated_spec["spec"]["resources"]["substrate_definition_list"][0] = substrate
    updated_spec["spec"]["name"] = bp_name
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
    launch_single_vm_bp(base_url, auth, blueprint_uuid, resp)


esxi_single_vm_run(BP_SPEC)