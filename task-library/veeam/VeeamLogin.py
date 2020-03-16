# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       11/03/2020
# task_name:    VeeamLogin
# description:  Login to the Veeam API
#               Retreives a X-RestSvcSessionId session
# input vars:   username, password, api_server
# output vars:  veeam_session_id, veeam_session_cookie
# endregion

# region capture Calm variables
username = "@@{veeam.username}@@"
password = "@@{veeam.secret}@@"
api_server = "@@{veeam_endpoint}@@"
# endregion

# region prepare api call
api_server_port = "9398"
api_server_endpoint = "/api/sessionMngr/?v=latest"
method = "POST"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
# endregion

# region API call function
def process_request(url, method, headers, payload=None):
    if (payload is not None):
        payload = json.dumps(payload)
    r = urlreq(url, verb=method, auth='BASIC', user=username, passwd=password, params=payload, verify=False, headers=headers)
    if r.ok:
        print("Request was successful")
        print("Status code: {}".format(r.status_code))
       # print('Response: {}'.format(json.dumps(json.loads(r.content), indent=2)))
    else:
        print("Request failed")
        print('Status code: {}'.format(r.status_code))
        print("Headers: {}".format(headers))
        print("Payload: {}".format(json.dumps(payload)))
        print('Response: {}'.format(json.dumps(json.loads(r.content), indent=4)))
        exit(1)
    return r
# endregion

# region login
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)
# endregion

# pass the session_cookie and session_id so that it may be captured by Calm.
resp_parse = json.loads(resp.content)
session_cookie = resp.headers.get('X-RestSvcSessionId')
session_id = resp_parse['SessionId']
print ("veeam_session_id={}".format(session_id))
print ("veeam_session_cookie={}".format(session_cookie))
exit(0)