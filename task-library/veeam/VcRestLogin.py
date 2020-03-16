# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       10/03/2020
# task_name:    VcRestLogin
# description:  Authenticate to the vCenter Rest API
#               Retreives a cookie session
# input vars:   username, password, api_server
# output vars:  vc_api_session
# endregion

# region capture Calm variables
username = "@@{vc.username}@@"
password = "@@{vc.secret}@@"
api_server = "@@{vc_endpoint}@@"
# endregion

# region prepare api call
api_server_port = "443"
api_server_endpoint = "/rest/com/vmware/cis/session"
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
        print('Response: {}'.format(json.dumps(json.loads(r.content), indent=4)))
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

# pass the cookie in vc_soap_session so that it may be captured by Calm.
cookie = resp.headers.get('Set-Cookie').split(";")[0]
print ("vc_api_session={}".format(cookie))
exit(0)