# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/10032020 - initial version
# task_name:    F5CreateNode
# description:  Create a node or nodes to be used inside a pool
# input vars:   vm_name, vm_ip, f5_node_description, f5_partition
# output vars:  n/a
# endregion

# region capture Calm variables
api_server = "@@{fortigate_endpoint}@@"
f5_login = "@@{fortigate.username}@@"
f5_password = "@@{fortigate.secret}@@"
api_server_port = 443
vm_name = "toto"
vm_ip = "@@{address}@@"
f5_node_description = "@@{awx_application_name}@@" + " node"
f5_partition = "@@{f5_partition}@@"
# endregion


def f5_create_node(api_server, api_server_port, vm_name, vm_ip, f5_node_description, f5_partition):
    
    # region prepare api call
    api_server_endpoint = "/mgmt/tm/ltm/node/"
    url = "https://{}:{}{}".format(
        api_server,
        api_server_port,
        api_server_endpoint
    )
    method = "POST"
    headers = {
         'Content-Type': 'application/json'
    }
    # endregion
    create_payload = {
        "name": vm_name,
        "partition": f5_partition,
        "address": vm_ip,
        "connectionLimit": 0,
        "description": f5_node_description,
        "dynamicRatio": 1,
        "ephemeral": "false",
        "fqdn": {
            "addressFamily": "ipv4",
            "autopopulate": "disabled",
            "downInterval": 5,
            "interval": "3600"
        }
    }
    print(json.dumps(create_payload))

    # region make api call
    # make the API call and capture the results in the variable called "resp"
    print("Making a {} API call to {}".format(method, url))
    resp = urlreq(url, verb=method, auth='BASIC', params=json.dumps(create_payload),
                  user=f5_login, passwd=f5_password, headers=headers, verify=False)

    # deal with the result/response
    if resp.ok:
        print("Request was successful. Status code: {}".format(resp.status_code))
        result = json.loads(resp.content)
        print("node {} created".format(result['name']))
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(resp.content)))
        exit(1)
    # endregion
    

f5_create_node(api_server, api_server_port, vm_name, vm_ip, f5_node_description, f5_partition)
