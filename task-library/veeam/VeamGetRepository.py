# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       11/03/2020
# task_name:    VeeamGetRepository
# description:  Get Repository UID
#               The script retreives the repository uid
#               based on the provided repository's name
# input vars:   veeam_job_name, username, password
#               veeam_repo_name, api_server
# output vars:  veeam_repo_uid
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
veeam_repo_name = "@@{veeam_repo_name}@@"
api_server = "@@{veeam_endpoint}@@"
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
api_server_endpoint = "/api/repositories"
method = "GET"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-RestSvcSessionId': veeam_session_cookie}
# endregion

# region get repositories
# make the api call
print("STEP: Gettings repositories...")
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)

# pass the repo_uid so that it may be captured by Calm.
repo_uid = ""
resp_parse = json.loads(resp.content)
for repo in resp_parse['Refs']:
    if repo['Name'] == veeam_repo_name:
                repo_uid = repo['UID']
                
if repo_uid:
    print ("veeam_repo_uid={}".format(repo_uid))
else:
    print("Error: Repository "+veeam_repo_name+" is not present ..")
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