# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       11/03/2020
# task_name:    VeeamEditJob
# description:  Edit a Veeam Job
#               The script edits a Veeam Job using the 
#               the veeam_job_url found on VeeamGetJob
#               and attach a category_id found on 
#               VcRestGetCategory
# input vars:   username, password, veeam_start_url,
#               veeam_job_name, vc_category_name,
# #             vc_category_id, api_server
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
veeam_hierarchyroot_uid = "@@{veeam_hierarchyroot_uid}@@"
veeam_job_daily_schedule = "@@{veeam_job_daily_schedule}@@"
vc_category_id = "@@{calm_array_vc_category_id}@@"
vc_category_name = "@@{jira_parent_ticket}@@"
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
    if job['Name'] == veeam_job_name:
        job_url = job['Href']
                
if job_url:
    veeam_job_url=job_url.rsplit('/', 1)[1] #get only the last occurence
else:
    print("Error: Backup Job "+veeam_job_name+" is not present ..")
    exit(1)
# endregion

# region edit job
payload = {
    "ScheduleConfigured": True,
    "ScheduleEnabled": True,
    "JobScheduleOptions": { 
      "Standart": {
          "OptionsDaily": {
              "Kind": "Everyday",
              "Time": veeam_job_daily_schedule,
              "Enabled": True
          },
          "OptionsMonthly": {
              "Enabled": False
            }
        }
    },
    "JobInfo": {
      "BackupJobInfo": {
        "Includes": {
            "ObjectInJobs": [
              {
                "HierarchyObjRef": "urn:VMware:Category:"+veeam_hierarchyroot_uid+'.'+vc_category_id,
                    "Name": vc_category_name,
                    "DisplayName": vc_category_name,
                    "Type": "ObjectInJob"
                  }
              ]
          }
      }
  }
}

# make the api call
print("STEP: Edit job ...")
method = "PUT"
url = "{0}/{1}?action=edit".format(url, veeam_job_url)
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