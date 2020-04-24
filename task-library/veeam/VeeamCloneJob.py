# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       11/03/2020
# task_name:    VeeamCloneJob
# description:  Clone a Veeam Job
#               The script clones an exisiting Veeam Job
# input vars:   veaam_job_name, veeam_job_template_name, veeam_repo_uuid
# output vars:  none
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
veeam_job_name = "@@{calm_application_name}@@"  # getting the calm apps job
veeam_job_template_name = "@@{veeam_job_template_name}@@" # getting the template job on veeam
veeam_repo_uid = "@@{veeam_repo_uid}@@"
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
api_server_endpoint = "/api/jobs"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-RestSvcSessionId': veeam_session_cookie}
# endregion

# region get job
# make the api call
print("STEP: Gettings jobs...")
method = "GET"
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)

# get the job_url
job_url = ""
resp_parse = json.loads(resp.content)
for job in resp_parse['Refs']:
    if job['Name'] == veeam_job_template_name:
        job_url = job['Href']
                
if job_url:
    veeam_job_url=job_url.rsplit('/', 1)[1] #get only the last occurence
else:
    print("Error: Backup Job "+veeam_job_template_name+" is not present ..")
    exit(1)
# endregion

# region clone job
payload = {
   "BackupJobCloneInfo": {
      "JobName": veeam_job_name,
      "FolderName": veeam_job_name,
      "RepositoryUid": veeam_repo_uid,
      "Description": "This job was created by CALM"
   }
}

# make the api call
print("STEP: Clone job ...")
method = "POST"
url = "{0}/{1}?action=clone".format(url, veeam_job_url)
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)
# endregion

# pass the task_id so that it may be captured by Calm.
resp_parse = json.loads(resp.content)
task_id = resp_parse['TaskId']
print ("veeam_task_id={}".format(task_id))
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