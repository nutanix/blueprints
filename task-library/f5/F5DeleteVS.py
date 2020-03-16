# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/10032020 - initial version
# task_name:    F5DeleteVS
# description:  Delete a single virtual server
# input vars:   vs_name
# output vars:  n/a
# endregion

# region capture Calm variables
api_server = "@@{fortigate_endpoint}@@"
f5_login = "@@{fortigate.username}@@"
f5_password = "@@{fortigate.secret}@@"
api_server_port = 80
vs_name = "@@{calm_application_name}@@" + "-vs"
# endregion


def f5_delete_pool(api_server, api_server_port, pool_name):
    
    # region prepare api call
    api_server_endpoint = "/mgmt/tm/ltm/virtual/" + vs_name
    url = "http://{}:{}{}".format(
        api_server,
        api_server_port,
        api_server_endpoint
    )
    method = "DELETE"
    headers = {
         'Accept': '*/*'
    }
    # endregion

    # region make api call
    # make the API call and capture the results in the variable called "resp"
    print("Making a {} API call to {}".format(method, url))
    resp = urlreq(url, verb=method, user=f5_login, passwd=f5_password, headers=headers, verify=False)

    # deal with the result/response
    if resp.ok:
        print("Request was successful. Status code: {}".format(resp.status_code))
        print("Virtual server {} was deleted".format(vs_name))
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)
    # endregion
    

f5_delete_vs(api_server, api_server_port, vs_name)
