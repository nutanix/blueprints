# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       11/03/2020
# task_name:    VeeamGetJob
# description:  Get Veeam Backup Job
#               The script retreives a specific job based on a provided job's name
# input vars:   veeam_job_name
# output vars:  veeam_job_url
# endregion

# region capture Calm variables
username = "@@{veeam.username}@@"
password = "@@{veeam.secret}@@"
#veeam_job_name = "@@{calm_application_name}@@"  # getting the calm apps job
veeam_job_name = "@@{veeam_job_template_name}@@" # getting the backup template job on veeam
api_server = "@@{veeam_endpoint}@@"

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
        #if (r.content and ('/api/sessionMngr' not in url)):
        #    print('Response: {}'.format(json.dumps(json.loads(r.content), indent=2)))
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
method = "GET"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-RestSvcSessionId': veeam_session_cookie}
# endregion

# region get jobss
# make the api call
print("STEP: Gettings jobs...")
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)

# pass the cookie job_url so that it may be captured by Calm.
job_url = ""
resp_parse = json.loads(resp.content)
for job in resp_parse['Refs']:
    if job['Name'] == veeam_job_name:
        job_url = job['Href']
                
if job_url:
    print ("veeam_job_url={}".format(job_url.rsplit('/', 1)[1])) #get only the last occurence
else:
    print("Error: Backup Job "+veeam_job_name+" is not present ..")
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