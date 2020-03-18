#script
# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    14082019
# task_name:    CreatePool
# description:  this task is used to create a pool that include all the servers deployed through Calm
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

headers_post = {
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

def create_pool(controller_url,headers_post,cloud_uuid, name, description, vrf_uuid, servers, port):
    """ This function create a pool and return it's uuid to be used later 
        Args:
         controller_url: http://avi_controller_ip
         headers_post: header with the sessionid and csrftoken
         cloud_uuid: the cloud uuid that will host the pool
		 name: pool name
		 description: pool description
		 servers: array containing the list of server to be included
		 port: port number
		Returns:
		 POOL_UUID: uuid of the created pool
    
    """
    pool_url = controller_url + "/api/pool"
    create_pool_payload = {}
    create_pool_payload['cloud_ref'] = cloud_uuid
    create_pool_payload['vrf_ref'] = vrf_uuid
    create_pool_payload['description'] = description
    create_pool_payload['name'] = name
    create_pool_payload['servers'] = []

    for server in servers:
        create_pool_payload['servers'].append({'ip':{"addr": server,"type": "V4"},'port':port})
    
    response = urlreq(pool_url, verb='POST', params=json.dumps(create_pool_payload), headers=headers_post, verify=False)
    # deal with the result/response
    if response.ok:
        print("Request was successful")
        pool = response.json()
        print('POOL_UUID={}'.format(pool['uuid']))        

    else:
        print("Request failed")
        print("Headers: {}".format(headers_post))
        print("Payload: {}".format(create_pool_payload))
        print('Status code: {}'.format(response.status_code))
        print('Response: {}'.format(response.text))
        exit(1)
    
    # endregion

if "@@{AVI_INTEGRATION}@@" == "yes":
    create_pool(controller_url,headers_post,"@@{CLOUD_UUID}@@","Pool_@@{calm_application_name}@@",
                "@@{calm_application_name}@@ servers pool", "@@{VRF_UUID}@@", my_servers,pool_port)
