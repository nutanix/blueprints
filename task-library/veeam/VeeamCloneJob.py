# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       11/03/2020
# task_name:    VeeamCloneJob
# description:  Clone a Veeam Job
#               The script clones a Veeam Job using the 
#               the veeam_job_url and veeam_repo_uid found
#               on the VeeamGetJob and VeeamGetRepository
# input vars:   veeam_session_cookie, veeam_job_url
#               veeam_job_name, veeam_repo_uid, api_server
# output vars:  none
# endregion

# region capture Calm variables
veeam_session_cookie = "@@{veeam_session_cookie}@@"
veeam_job_url = "@@{veeam_job_url}@@"
veeam_repo_uid = "@@{veeam_repo_uid}@@"
veeam_job_name = "@@{calm_application_name}@@"
api_server = "@@{veeam_endpoint}@@"
# endregion

# region prepare api call
api_server_port = "9398"
api_server_endpoint = "/api/jobs"
method = "POST"
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

# region login
payload = {
   "BackupJobCloneInfo": {
      "JobName": veeam_job_name,
      "FolderName": veeam_job_name,
      "RepositoryUid": veeam_repo_uid,
      "Description": "This job was created by CALM"
   }
}
url = "{0}/{1}?action=clone".format(base_url, veeam_job_url)
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)
# endregion

# pass the task_id so that it may be captured by Calm.
resp_parse = json.loads(resp.content)
task_id = resp_parse['TaskId']
print ("veeam_task_id={}".format(task_id))
exit(0)