# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       11/03/2020
# task_name:    VeeamLogout
# description:  Logout from the Veeam API
#               veeam_session_cookie: retreived from VeeamLogin
#               vmware_session_id: retreived from VeeamLogin
#               none that the LogonSessionId can also be 
#               retreived using /api/logonSessions url
# input vars:   veeam_session_cookie, veeam_session_id, api_server
# output vars:  none
# endregion

# region capture Calm variables
veeam_session_cookie = "@@{veeam_session_cookie}@@"
veeam_session_id = "@@{veeam_session_id}@@"
api_server = "@@{veeam_endpoint}@@"
# endregion

# region prepare api call
api_server_port = "9398"
api_server_endpoint = "/api/logonSessions"
method = "DELETE"
base_url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-RestSvcSessionId': veeam_session_cookie}
# endregion

# region API call function
def process_request(url, method, headers, payload=None):
    if (payload is not None):
        payload = json.dumps(payload)
    r = urlreq(url, verb=method, params=payload, verify=False, headers=headers)
    if r.ok:
        print("Request was successful")
        print("Status code: {}".format(r.status_code))
    else:
        print("Request failed")
        print('Status code: {}'.format(r.status_code))
        print("Headers: {}".format(headers))
        print("Payload: {}".format(json.dumps(payload)))
        print('Response: {}'.format(json.dumps(json.loads(r.content), indent=4)))
        exit(1)
    return r
# endregion

# region Logout
url = "{0}/{1}".format(base_url, veeam_session_id)
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)
# endregion

exit(0)