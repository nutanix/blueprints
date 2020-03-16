# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       11/03/2020
# task_name:    VeeamGetRepository
# description:  Get Repository UID
#               The script retreives the repository uid
#               based on the provided repository's name
# input vars:   veeam_session_cookie, veeam_job_name,
#               veeam_repo_name, api_server
# output vars:  veeam_repo_uid
# endregion

# region capture Calm variables
veeam_session_cookie = "@@{veeam_session_cookie}@@"
veeam_repo_name = "@@{veeam_repo_name}@@"
api_server = "@@{veeam_endpoint}@@"
# endregion

# region prepare api call
api_server_port = "9398"
api_server_endpoint = "/api/repositories"
method = "GET"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
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

# region login
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)
# endregion

# pass the repo_uid so that it may be captured by Calm.
repo_uid = ""
resp_parse = json.loads(resp.content)
for repo in resp_parse['Refs']:
    if repo['Name'] == veeam_repo_name:
                repo_uid = repo['UID']
                
if repo_uid:
    print ("veeam_repo_uid={}".format(repo_uid))
    exit(0)
else:
    print("Error: Repository "+veeam_repo_name+" doesn't is not present ..")
    exit(1)