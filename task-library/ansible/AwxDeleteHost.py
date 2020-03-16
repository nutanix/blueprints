# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:     jose.gomez@nutanix.com
# * version:    20200214
# task_type:    Execute
# task_name:    AwxDeleteHost
# description:  Delete host from AWX inventory 
# endregion

# region capture Calm variables
# * Capture variables here. This makes sure Calm macros are not referenced
# * anywhere else in order to improve maintainability.
awx_username = '@@{awx.username}@@'
awx_password = '@@{awx.secret}@@'
awx_api = '@@{awx_ip}@@'
host_id = int('@@{awx_host_id}@@')
# endregion

# region functions
def make_api_call(url,method,username,username_secret):
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
            exit(0)

        else:
            print "Luis"
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(
                json.dumps(
                    json.loads(resp.content), 
                    indent=4)))
            exit(1)

def awx_delete_host(api,username,password,host_id):
    # region prepare api call
    # Form method, url and headers for the API call
    api_port = "80"
    api_endpoint = "/api/v2/hosts/"
    url = "http://{}:{}{}{}".format(
        api,
        api_port,
        api_endpoint,
        host_id
    )
    method = "DELETE"

    # endregion

    r = make_api_call(
        url,
        method,
        username,
        password
        )

    if r.ok:
        resp = json.loads(r.content)
        print 'Host with id {0} removed from inventory'.format(host_id)
        print "Here"
        exit(0)
    else:
        print 'Post request failed', r.content
        print "There"
        exit(1)
# endregion
        
awx_delete_host(awx_api,awx_username,awx_password,host_id)