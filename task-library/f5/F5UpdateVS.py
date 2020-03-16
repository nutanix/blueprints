# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/11032020 - initial version
# task_name:    F5UpdateVS
# description:  Update a virtual server with a pool as a memeber
# input vars:   pool_name, vs_name, f5_partition
# output vars:  n/a
# endregion

# region capture Calm variables
api_server = "@@{fortigate_endpoint}@@"
f5_login = "@@{fortigate.username}@@"
f5_password = "@@{fortigate.secret}@@"
api_server_port = 443
pool_name = "@@{calm_application_name}@@" + "-pool"
vs_name = "@@{calm_application_name}@@" + "-vs"
f5_partition = "@@{f5_partition}@@"

# endregion


def f5_update_vs(api_server, api_server_port, pool_name, vs_name, f5_partition, action="add"):
    
    # region prepare api call
    api_server_endpoint = "/mgmt/tm/ltm/virtual/" + vs_name
    url = "https://{}:{}{}".format(
        api_server,
        api_server_port,
        api_server_endpoint
    )
    headers = {
         'Content-Type': 'application/json'
    }
    method = "PATCH"
    # endregion
    
    # region make api call
    # make the API call and capture the results in the variable called "resp"
    if action == "add":
        update_payload = {
            "pool": "/" + f5_partition + "/" + pool_name,
        }
        print("Adding pool {} into virtual server {}".format(
            pool_name, vs_name))
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(url, verb=method, auth='BASIC', params=json.dumps(update_payload),
                      user=f5_login, passwd=f5_password, headers=headers, verify=False)
    else:
        print("Removing pool {} from virtual server {}".format(pool_name, vs_name))
        update_payload = {
            "pool": "",
        }
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(url, verb=method, auth='BASIC', params=json.dumps(update_payload),
                      user=f5_login, passwd=f5_password, headers=headers, verify=False)

    # deal with the result/response
    if resp.ok:
        print("Request was successful. Status code: {}".format(resp.status_code))
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)
    # endregion


f5_update_vs(api_server, api_server_port, pool_name, vs_name, f5_partition, "add")
