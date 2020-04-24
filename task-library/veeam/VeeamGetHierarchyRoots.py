# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       11/03/2020
# task_name:    VeeamGetHierarchyRoots
# description:  Get the hierarchyRoot UID
#               The script retreives the hierarchyRoots UID
# input vars:   vc_server, api_server, username, password
# output vars:  veeam_hierarchyroot_uid
# endregion

# region dealing with Scaling In/Out the application
# # this script will be executed only on the first Service/Instance
# (ie: Service[0])
if "@@{calm_array_index}@@" != "0":
    print("This task is not required on this Instance ..")
    print("Skipping this task ..")
    exit(0)
# endregion

# region capture Calm variables
username = "@@{veeam.username}@@"
password = "@@{veeam.secret}@@"
api_server = "@@{veeam_endpoint}@@"
vc_server = "@@{vc_endpoint}@@"
# endregion

# region API call function
def process_request(url, method, headers, payload=None):
    if (payload is not None):
        payload = json.dumps(payload)
    if "Cookie" not in headers:
        r = urlreq(url, verb=method, auth='BASIC', user=username, passwd=password, params=payload, verify=False, headers=headers)
    else:
        r = urlreq(url, verb=method, params=payload, verify=False, headers=headers)
    if r.ok:
        print("Request was successful")
        print("Status code: {}".format(r.status_code))
    else:
        print("Request failed")
        print('Status code: {}'.format(r.status_code))
        print("Headers: {}".format(headers))
        if (payload is not None):
            print("Payload: {}".format(json.dumps(payload)))
        if r.content:
            print('Response: {}'.format(json.dumps(json.loads(r.content), indent=4)))
        exit(1)
    return r
# endregion

# region login
api_server_port = "9398"
api_server_endpoint = "/api/sessionMngr/?v=latest"
method = "POST"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

# making the call 
print("STEP: Logging in to Veeam...")
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)

# pass the session_cookie and session_id
resp_parse = json.loads(resp.content)
veeam_session_cookie = resp.headers.get('X-RestSvcSessionId')
veeam_session_id = resp_parse['SessionId']
# endregion

# region main processing
# region prepare api call
api_server_port = "9398"
api_server_endpoint = "/api/hierarchyRoots"
method = "GET"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-RestSvcSessionId': veeam_session_cookie}
# endregion

# region get hierarchyroot (managed vcenter server)
# make the api call
print("STEP: Gettings hiearchyroots...")
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)

# pass the repo_uid so that it may be captured by Calm.
obj_uid = ""
resp_parse = json.loads(resp.content)
for obj in resp_parse['Refs']:
    if obj['Name'] == vc_server:
                obj_uid = obj['UID']               
if obj_uid:
    print ("veeam_hierarchyroot_uid={}".format(obj_uid.rsplit(':', 1)[1]))
else:
    print("Error: Managed Server "+vc_server+" is not present ..")
    exit(1)
# endregion
# endregion

# region logout
api_server_port = "9398"
api_server_endpoint = "/api/logonSessions"
method = "DELETE"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-RestSvcSessionId': veeam_session_cookie}

# making the call 
print("STEP: Logging out of Veeam...")
url = "{0}/{1}".format(url, veeam_session_id)
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)
# endregion

exit(0)