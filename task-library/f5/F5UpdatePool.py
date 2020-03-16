# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/11032020 - initial version
# task_name:    F5UpdatePool
# description:  Update a pool with a new member
# input vars:   pool_name, f5_pool_members,
#                   f5_vs_port, f5_member_ip, f5_partition
# output vars:  n/a
# endregion

# region capture Calm variables
api_server = "@@{fortigate_endpoint}@@"
f5_login = "@@{fortigate.username}@@"
f5_password = "@@{fortigate.secret}@@"
api_server_port = 443
pool_name = "@@{calm_application_name}@@" + "-pool"
f5_pool_members = "toto"
f5_vs_port = "@@{f5_vs_port}@@"
f5_member_ip = "@@{address}@@"
f5_partition = "@@{f5_partition}@@"

# endregion


def f5_update_pool(api_server, api_server_port, pool_name, f5_pool_members,
                   f5_vs_port, f5_member_ip, f5_partition, action="add"):
    
    # region prepare api call
    api_server_endpoint = "/mgmt/tm/ltm/pool/" + pool_name + "/members/"
    url = "https://{}:{}{}".format(
        api_server,
        api_server_port,
        api_server_endpoint
    )
    headers = {
         'Content-Type': 'application/json'
    }
    # endregion
    update_payload = {
        "name": "/" + f5_partition + "/" + f5_pool_members + ":" + f5_vs_port ,
    }
    print(json.dumps(update_payload))
    # region make api call
    # make the API call and capture the results in the variable called "resp"
    if action == "add":
        method = "POST"
        print("Adding a new member {} into pool {}".format(
            f5_pool_members, pool_name))
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(url, verb=method, auth='BASIC', params=json.dumps(update_payload),
                      user=f5_login, passwd=f5_password, headers=headers, verify=False)
    else:
        print("Removing member {} from pool {}".format(f5_pool_members,pool_name))
        method = "DELETE"
        url = url + f5_pool_members + ":" + f5_vs_port
        print("Making a {} API call to {}".format(method, url))
        resp = urlreq(url, verb=method, auth='BASIC',
                      user=f5_login, passwd=f5_password, headers=headers, verify=False)
 
    # deal with the result/response
    if resp.ok:
        print("Request was successful. Status code: {}".format(resp.status_code))
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(
            json.loads(resp.content), indent=4)))
        exit(1)
    # endregion


f5_update_pool(api_server, api_server_port, pool_name, f5_pool_members,
               f5_vs_port, f5_member_ip, f5_partition, "add")
