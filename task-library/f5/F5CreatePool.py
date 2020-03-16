# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/10032020 - initial version
# task_name:    F5CreatePool
# description:  Create an empty pool
# input vars:   pool_name, f5_pool_description, f5_pool_monitor, f5_partition
# output vars:  n/a
# endregion

# region capture Calm variables
api_server = "@@{fortigate_endpoint}@@"
f5_login = "@@{fortigate.username}@@"
f5_password = "@@{fortigate.secret}@@"
api_server_port = 443
pool_name = "@@{calm_application_name}@@" + "-pool"
f5_pool_description = "@@{awx_application_name}@@" + " pool"
f5_pool_monitor = "@@{f5_pool_monitor}@@"
f5_partition = "@@{f5_partition}@@"
# endregion


def f5_create_pool(api_server, api_server_port, pool_name, f5_pool_description, f5_pool_monitor, f5_partition):
    
    # region prepare api call
    api_server_endpoint = "/mgmt/tm/ltm/pool/"
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
        "name": pool_name,
        "partition": f5_partition,
        "monitor": f5_pool_monitor
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
        print("Pool {} created".format(result['name']))
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(resp.content)))
        exit(1)
    # endregion
    

f5_create_pool(api_server, api_server_port, pool_name, f5_pool_description, f5_pool_monitor, f5_partition)
