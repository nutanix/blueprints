# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       11/03/2020
# task_name:    VeeamGetTask
# description:  Get status of a task
#               The script gets the task status
#               based on the task_id found
#               on the VeeamStartJob script
# input vars:   veeam_session_cookie, veeam_task_id, api_server
# output vars:  task_id
# endregion

# region capture Calm variables
veeam_session_cookie = "@@{veeam_session_cookie}@@"
veeam_task_id = "@@{veeam_task_id}@@"
api_server = "@@{veeam_endpoint}@@"
# endregion

# region prepare api call
api_server_port = "9398"
api_server_endpoint = "/api/tasks"
method = "GET"
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
url = "{0}/{1}".format(base_url, veeam_task_id)
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)
# endregion

# pass the task_id so that it may be captured by Calm.
resp_parse=json.loads(resp.content)
print resp_parse['TaskId']
print resp_parse['State']
print resp_parse['Result']['Success']
exit(0)