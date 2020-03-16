#script
#region headers
# * authors:     igor.zecevic@nutanix.com, stephane.bourdeaud@nutanix.com
# * version:    v1.1 - added login/logout logic (stephane)
# * date:       12/03/2020
# task_name:    VcRestDeleteTag
# description:  Deletes a tag
#               This script deletes a tag and his associated category
# input vars:   vc_cookie, api_server, vc_tag_id, vc_category_id
# output vars:  none
#endregion

#region dealing with Scaling In/Out the application
# # this script will be executed only on the first Service/Instance
# (ie: Service[0])
if "@@{calm_array_index}@@" != "0":
    print("This task is not required on this Instance ..")
    print("Skipping this task ..")
    exit(0)
#endregion

#region capture Calm variables
username = "@@{vc.username}@@"
password = "@@{vc.secret}@@"
api_server = "@@{vc_endpoint}@@"
vc_tag_id = "@@{vc_tag_id}@@" #retreived from VcRestCreateTag
vc_category_id = "@@{vc_category_id}@@" #retreived from VcRestCreateTag
#endregion

#region API call function
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
        if (r.content and ('/rest/com/vmware/cis/session' not in url)):
            print('Response: {}'.format(json.dumps(json.loads(r.content), indent=4)))
    elif ((r.status_code == 400) and (json.loads(r.content)['type'] == 'com.vmware.vapi.std.errors.already_exists')):
        print("Status code: {}".format(r.status_code))
        print("Object already exists: skipping")
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
#endregion

#region login
#region prepare api call
api_server_port = "443"
api_server_endpoint = "/rest/com/vmware/cis/session"
method = "POST"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
#endregion

#region login API call
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)
vc_cookie = resp.headers.get('Set-Cookie').split(";")[0]
#endregion
#endregion

#region main processing
#region prepare api call
api_server_port = "443"
api_server_endpoint = "/rest/com/vmware/cis/tagging"
method = "DELETE"
base_url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Cookie': vc_cookie}
payload = {}
#endregion

#region delete tag
url = '{0}/tag/id:{1}'.format(base_url,vc_tag_id)
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)
#endregion

#region delete category
url = '{0}/category/id:{1}'.format(base_url,vc_category_id)
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)
#endregion
#endregion

#region logout
#region prepare api call
api_server_port = "443"
api_server_endpoint = "/rest/com/vmware/cis/session"
method = "DELETE"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Cookie': vc_cookie}
#endregion

#region logout API call
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)
#endregion

#endregion

exit(0)
