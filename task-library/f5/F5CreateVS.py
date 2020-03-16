# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/10032020 - initial version
# task_name:    F5CreateVS
# description:  Create a virtual server
# input vars:   vs_name, vs_ip, f5_vs_description,
#               f5_vs_port, f5_vs_protocol, f5_partition
# output vars:  n/a
# endregion

# region capture Calm variables
api_server = "@@{fortigate_endpoint}@@"
f5_login = "@@{fortigate.username}@@"
f5_password = "@@{fortigate.secret}@@"
api_server_port = 443
vs_name = "@@{calm_application_name}@@" + "-vs"
vs_ip = "1.1.1.10"
f5_vs_description = "@@{awx_application_name}@@" + " vip"
f5_vs_port = "@@{f5_vs_port}@@"
f5_vs_protocol = "@@{f5_vs_protocol}@@"
f5_partition = "@@{f5_partition}@@"
# endregion


def f5_create_vs(api_server, api_server_port, vs_name, vs_ip, f5_vs_description,
                 f5_vs_port, f5_vs_protocol, f5_partition):
    
    # region prepare api call
    api_server_endpoint = "/mgmt/tm/ltm/virtual/"
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
        "name": vs_name,
        "partition": f5_partition,
        "description": f5_vs_description,
        "destination": f5_partition + "/" + vs_ip + ":" + f5_vs_port,
        "enabled": True,
        "ipProtocol": f5_vs_protocol,
        "mask": "255.255.255.255",
        "source": "0.0.0.0/0",
        "sourcePort": "preserve"
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
        print("Virtual Server {} created".format(result['name']))
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)
    # endregion
    

f5_create_vs(api_server, api_server_port, vs_name, vs_ip, f5_vs_description,
             f5_vs_port, f5_vs_protocol, f5_partition)
