#region headers
# * authors:     igor.zecevic@nutanix.com, stephane.bourdeaud@nutanix.com
# * version:    v1.1 - added login/logout logic (stephane)
# * date:       12/03/2020
# task_name:    VcRestTagAssociation
# description:  Attach or Detach a tag from/to one VM
# input vars:   vc_cookie, api_server, vc_tag_id, vc_tag_action, vm_id
# output vars:  none
#endregion

#region capture Calm variables
username = "@@{vc.username}@@"
password = "@@{vc.secret}@@"
api_server = "@@{vc_endpoint}@@"
vc_tag_id= '@@{vc_tag_id}@@' # retrieved from VcRestCreateTag
vc_tag_action = "attach" #attach / detach
vm_id = "@@{vc_vm_id}@@" #retreived from VcSoapGetObjects
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
api_server_endpoint = "/rest/com/vmware/cis/tagging/tag-association/id"
method = "POST"
base_url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Cookie': vc_cookie}
#endregion

#region tag association
object_id = {}
object_id['id'] = vm_id
object_id['type'] = "VirtualMachine"
payload = {
    "object_id" : object_id
    }

# make the api call
url = "{0}:{1}?~action={2}".format(base_url, vc_tag_id, vc_tag_action)
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
