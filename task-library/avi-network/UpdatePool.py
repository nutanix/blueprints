#script
# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    30092019
# task_name:    UpdatePool
# description:  this task is used to update a pool and add an additional server(s)
# endregion

# setting up variables and header
controller_url = "@@{CONTROLLER_URL}@@"
h_referer = "@@{REFERER}@@"
h_api_version = "@@{API_VERSION}@@"
h_encoding = "@@{ENCODING}@@"
h_content = "@@{CONTENT}@@"
r_csrftoken = "@@{CSRF_TOKEN}@@"
r_sessionid = "@@{SESSION_ID}@@"
pool_port = "@@{POOL_PORT}@@"
vs_name = "@@{VS_NAME}@@" # Virtual service name to be updated
operation = "add" # operation to be done on the pool, could be: add, replace or delete

headers = {
    'cookie': "sessionid=" + r_sessionid +"; csrftoken=" + r_csrftoken,
    'X-Avi-Version': h_api_version,
    'Accept-Encoding': h_encoding,
    'Content-type': h_content,
    'X-CSRFToken': r_csrftoken,
    'Referer': h_referer
    }
    
my_servers = ["@@{Node1.address}@@"] #"@@{calm_array_address}@@"
print "my_servers = {}".format(my_servers)
# endregion

def update_pool(pool_url, operation, headers, servers, port):
    """ This function update a pool by adding/removing or replacing an additional server(s) 
        Args:
         controller_url: http://avi_controller_ip
         operation: what we are doing inside the pool
         headers_post: header with the sessionid and csrftoken
         servers: array containing the list of servers
         port: port number
        Returns:
         N/A
    
    """
    update_pool_payload = {}
    update_pool_payload[operation] = {}
    update_pool_payload[operation]['servers'] = []


    for server in servers:
        update_pool_payload[operation]['servers'].append({'ip':{"addr": server,"type": "V4"},'port':port})
    
    response = urlreq(pool_url, verb='PATCH', params=json.dumps(update_pool_payload), headers=headers, verify=False)
    # deal with the result/response
    if response.ok:
        print("Request was successful")
        pool = response.json()
        print('POOL_UUID={}'.format(pool['uuid']))        

    else:
        print("Request failed")
        print("Headers: {}".format(headers_patch))
        print("Payload: {}".format(update_pool_payload))
        print('Status code: {}'.format(response.status_code))
        print('Response: {}'.format(response.text))
        exit(1)
    
    # endregion


if "@@{AVI_INTEGRATION}@@" == "yes" and "@@{VS_NAME}@@" != "":
    # get the pool uuid by virtual service name
    vs_url = controller_url + "/api/virtualservice?name=" + vs_name
    response = urlreq(vs_url, verb='GET', headers=headers, verify=False)
    vs_exist = response.json()
	# if no pool inside the virtual service
    if vs_exist['count'] == 0:
        print("No Virtual Service with the name {} exist on the Avi Controller {}".format(
              vs_name, controller_url))
        exit(1)
    else:
        pool_url = vs_exist['results'][0]['pool_ref']
        print("Updating pool {}".format(pool_url))
        # should add a check to delete the VS if there is no more pool member
        update_pool(pool_url, operation, headers, my_servers, pool_port)
