
BP_SPEC = {
    "api_version": "3.0",
    "metadata": {
      "kind": "blueprint",
      "categories": {
          "TemplateType": "Vm"
      },
      "project_reference": {
        "kind": "project",
        "uuid": "f0f8a738-ca91-49b3-8dd6-1e79bcd98fb7"
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
                "account_uuid": "763f3491-99b0-49ac-af3e-2588a6c61a41",
                "num_vcpus_per_socket": 1,
                "num_sockets": 2,
                "memory_size_mib": 2048,
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
                    "instance_id": "50133a6d-f952-30b9-b760-842e7c70a198",
                    "instance_name": "vm-0-190618-024859",
                    "address": [
                      "10.46.140.178"
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
      "name": "singlebrownfieldVmware"
    }
}

def esxi_single_vm_run(spec):

    pc_ip = '@@{pc_ip}@@'
    auth = { "username": '@@{pc_cred.username}@@', "password": '@@{pc_cred.secret}@@'}
    base_url = "https://{}:9440/api/nutanix/v3".format(pc_ip)

    vcenter_ip = "@@{vCenter_IP}@@"
    vcenter_auth = { "username": '@@{vcenter_cred.username}@@', "password": '@@{vcenter_cred.secret}@@'}
    vcenter_url = "https://{}/rest".format(vcenter_ip)

    vm_ip = "@@{vm_ip}@@"
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

    ### --------------------------------------------------------------------------------- ###
    def get_vmware_sid(vcenter_url, vcenter_auth):
        method = 'POST'
        url = vcenter_url + "/com/vmware/cis/session"
        payload = {}
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(
            url,
            verb=method,
            params=json.dumps(payload),
            headers=headers,
            auth='BASIC',
            user=vcenter_auth["username"],
            passwd=vcenter_auth["password"],
            verify=False
        )

        if resp.ok:
            resp_out = json.loads(resp.content)
            return resp.json()['value']

        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            exit(1)
    ### --------------------------------------------------------------------------------- ### 

    ### --------------------------------------------------------------------------------- ###
    def get_vmware_vm_id(vcenter_url, vcenter_auth, sid, vm_name):
        method = 'GET'
        url = vcenter_url + '/vcenter/vm?filter.names.1=' + vm_name
        payload = {}
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(
            url,
            verb=method,
            params=json.dumps(payload),
            headers={'vmware-api-session-id':sid},
            auth='BASIC',
            user=vcenter_auth["username"],
            passwd=vcenter_auth["password"],
            verify=False
        )

        if resp.ok:
            resp_out = json.loads(resp.content)
            return resp_out['value'][0]["vm"]

        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            exit(1)
    ### --------------------------------------------------------------------------------- ###

    ### --------------------------------------------------------------------------------- ###
    def get_vmware_vm_info(vcenter_url, vcenter_auth, sid, vm_id):
        method = 'GET'
        url = vcenter_url + '/vcenter/vm/'+vm_id
        payload = {}
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(
            url,
            verb=method,
            params=json.dumps(payload),
            headers={'vmware-api-session-id':sid},
            auth='BASIC',
            user=vcenter_auth["username"],
            passwd=vcenter_auth["password"],
            verify=False
        )

        if resp.ok:
            resp_out = json.loads(resp.content)
            return resp_out["value"]

        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            exit(1)
    ### --------------------------------------------------------------------------------- ###

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

    ### --------------------------------------------------------------------------------- ###
    def get_host_networks(base_url, auth, account_uuid, host_id):
        method = 'POST'
        url = base_url + "/vmware/v6/network/list"
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
            net_dict = {}
            if len(json_resp['entities']) > 0:
                for net in json_resp['entities']:
                    net_dict[net['status']['resources']['name']] = net['status']['resources']["id"]
                return net_dict
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
                    id = host['status']['resources']['summary']['hardware']['uuid']
                    host_dict[id] = host['status']['resources']["name"]
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
                        vm_host = vm['status']['resources']['host']
                        datastore = vm['status']['resources']['datastore']
                        brownfield_instance_list.append(vm_info)

                if brownfield_instance_list:
                    return brownfield_instance_list, vm_host, datastore
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

    ### Build network dict
    network = {}
    for host in host_dict.keys():
        net_dict = get_host_networks(base_url, auth, account_uuid, host)
        for key, val in net_dict.items():
            network[key] = val


    ### Get brownfield vms dict
    brownfield_instance_list, vm_host, datastore = get_brownfield_vms_list(base_url, auth, project_uuid, account_uuid, vm_ip)
    vm_name = brownfield_instance_list[0]["instance_name"][0:25]

    ### Build required vm info from vcenter
    sid = get_vmware_sid(vcenter_url, vcenter_auth)
    vm_id = get_vmware_vm_id(vcenter_url, vcenter_auth, sid, brownfield_instance_list[0]["instance_name"])
    vm = get_vmware_vm_info(vcenter_url, vcenter_auth, sid, vm_id)
    vm_info = {
        "vm_name": vm_name,
        "num_vcpus_per_socket": vm["cpu"]["cores_per_socket"] ,
        "num_sockets": vm["cpu"]["count"],
        "memory_size_mib": vm["memory"]["size_MiB"]
    }
    vm_info["nic_list"] = []
    for nic in vm["nics"]:
        key = nic["key"]
        val = nic["value"]
        vm_info["nic_list"].append({
            "net_name": network[val["backing"]["network_name"]],
            "nic_type": val["type"].lower()
        })

    ### Update uuids, project ref, account ref, bp name, vm-info etc.
    updated_spec = change_uuids(spec, {})
    updated_spec["metadata"]["project_reference"]["uuid"] = project_uuid
    substrate = updated_spec["spec"]["resources"]["substrate_definition_list"][0]

    substrate["create_spec"]["name"] = vm_name
    substrate["create_spec"]["host"] = vm_host["uuid"]
    substrate["create_spec"]["datastore"] = datastore["0"]["url"]
    substrate["create_spec"]["resources"]["account_uuid"] = account_uuid
    substrate["create_spec"]["resources"]["num_vcpus_per_socket"] = vm_info["num_vcpus_per_socket"]
    substrate["create_spec"]["resources"]["num_sockets"] = vm_info["num_sockets"]
    substrate["create_spec"]["resources"]["memory_size_mib"] = vm_info["memory_size_mib"]
    substrate["create_spec"]["resources"]["nic_list"] = vm_info["nic_list"]

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