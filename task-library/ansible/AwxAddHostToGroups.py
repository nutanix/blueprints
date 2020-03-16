# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:     jose.gomez@nutanix.com
# * version:    20200214
# task_type:    Execute
# task_name:    AwxAddHostToGroups
# description:  Add host to AWX inventory 
# endregion

# region capture Calm variables
# * Capture variables here. This makes sure Calm macros are not referenced
# * anywhere else in order to improve maintainability.
awx_username = '@@{awx.username}@@'
awx_password = '@@{awx.secret}@@'
awx_api = '@@{awx_ip}@@'
awx_inventory_id = int('@@{awx_inventory_id}@@')
awx_host_id = int('@@{awx_host_id}@@')
awx_ansible_groups = list("@@{awx_ansible_groups}@@".split(","))
# endregion

# region functions
def make_api_call(url,method,username,username_secret,payload=None):
    """Makes an API call to an external API.

    Args:
        url: The URL for the external REST API endpoint.
        method: The REST method to use.
        username: The API user name.
        username_secret: The API user name password.
        payload: The JSON payload to include in the call.
    
    Returns:
        The API response.
    """
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }
    while True:
        print("Making a {} API call to {}".format(method, url))
        if payload:
            resp = urlreq(
                url,
                verb=method,
                auth='BASIC',
                user=username,
                passwd=username_secret,
                params=json.dumps(payload),
                headers=headers,
                verify=False
            )
        else:
            resp = urlreq(
                url,
                verb=method,
                auth='BASIC',
                user=username,
                passwd=username_secret,
                headers=headers,
                verify=False
            )

        # deal with the result/response
        if resp.ok:     
            return resp

        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print("Payload: {}".format(json.dumps(payload)))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(
                json.dumps(
                    json.loads(resp.content), 
                    indent=4)))
            exit(1)

def awx_add_host_to_groups(api,username,password,inventory_id,host_id,host_groups = [], *args):
    # region prepare api call
    # Form method, url and headers for the API call
    api_port = "80"

    for group in host_groups:
        api_endpoint = "/api/v2/inventories/"
        api_action = "/groups"
        api_query = "?name="

        url = "http://{}:{}{}{}{}{}{}".format(
            api,
            api_port,
            api_endpoint,
            inventory_id,
            api_action,
            api_query,
            group
        )
        
        method = "GET"

        r = make_api_call(
            url,
            method,
            username,
            password
        )
        
        if len(json.loads(r.content)['results']) > 0:
            group_id = json.loads(r.content)['results'][0]['id']
            payload = {
                'id': host_id
            }
        else:
            print "Group {0} does no exist".format(group)
            break

        api_endpoint = "/api/v2/groups/"
        api_action = "/hosts/"

        method = "POST"

        url = "http://{}:{}{}{}{}".format(
            api,
            api_port,
            api_endpoint,
            group_id,
            api_action,            
        )

        r = make_api_call(
            url,
            method,
            username,
            password,
            payload
        )

        if r.ok:
            print "Host added to group {0}".format(group)
        else:
            print 'Post request failed', r.content
            exit(1)
# endregion
        
awx_add_host_to_groups(awx_api,awx_username,awx_password,awx_inventory_id,awx_host_id,awx_ansible_groups)