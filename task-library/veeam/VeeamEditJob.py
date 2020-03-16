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
# input vars:   veeam_session_cookie, veeam_start_url,
#               veeam_job_name, vc_category_name,
# #             vc_category_id, api_server
# output vars:  none
# endregion

# region capture Calm variables
veeam_session_cookie = "@@{veeam_session_cookie}@@"
veeam_job_url = "@@{veeam_job_url}@@"
veeam_hierarchyroot_uid = "@@{veeam_hierarchyroot_uid}@@"
veeam_job_daily_schedule = "@@{veeam_job_daily_schedule}@@"
vc_category_id = "@@{vc_category_id}@@"
vc_category_name = "@@{calm_application_name}@@"
api_server = "@@{veeam_endpoint}@@"
# endregion

# region prepare api call
api_server_port = "9398"
api_server_endpoint = "/api/jobs"
method = "PUT"
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
        print('Response: {}'.format(json.dumps(json.loads(r.content), indent=2)))
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
url = "{0}/{1}?action=edit".format(base_url, veeam_job_url)
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)
# endregion

# pass the task_id so that it may be captured by Calm.
resp_parse = json.loads(resp.content)
task_id = resp_parse['TaskId']
print ("veeam_task_id={}".format(task_id))
exit(0)