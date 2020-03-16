# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       11/03/2020
# task_name:    VeeamGetJob
# description:  Get Job's url
#               The script retreives a specific job
#               url based on the provided job's name
# input vars:   veeam_session_cookie, veeam_job_name, api_server
# output vars:  veeam_job_url
# endregion

# region capture Calm variables
veeam_session_cookie = "@@{veeam_session_cookie}@@"
#veeam_job_name = "@@{calm_application_name}@@"  # getting the calm apps job
veeam_job_name = "@@{veeam_job_template_name}@@" # getting the template job on veeam
api_server = "@@{veeam_endpoint}@@"

# endregion

# region prepare api call
api_server_port = "9398"
api_server_endpoint = "/api/jobs"
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

# pass the cookie job_url so that it may be captured by Calm.
job_url = ""
resp_parse = json.loads(resp.content)
for job in resp_parse['Refs']:
    if job['Name'] == veeam_job_name:
        job_url = job['Href']
                
if job_url:
    print ("veeam_job_url={}".format(job_url.rsplit('/', 1)[1])) #get only the last occurence
    exit(0)
else:
    print("Error: Backup Job "+veeam_job_name+" doesn't is not present ..")
    exit(1)