# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       10/03/2020
# task_name:    VcRestGetTag
# description:  Retreives a specific tag id based on the tag's name
#               The scripts list all tags and filter
# input vars:   vc_cookie, api_server, vc_tag_name
# output vars:  vc_tag_id, vc_tag_name
# endregion

# region capture Calm variables
vc_cookie = "@@{vc_api_session}@@" # retreived from VcRestLogin
api_server = "@@{vc_endpoint}@@"
vc_tag_name = "@@{calm_application_name}@@"
# endregion

# region prepare api call
api_server_port = "443"
api_server_endpoint = "/rest/com/vmware/cis/tagging/tag"
method = "GET"
base_url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Cookie': vc_cookie}
# endregion

# region API call function
def process_request(url, method, headers, payload=None):
    if (payload is not None):
        payload = json.dumps(payload)
    r = urlreq(url, verb=method, params=payload, verify=False, headers=headers)
    if r.ok:
        print("Request was successful")
        print("Status code: {}".format(r.status_code))
        print('Response: {}'.format(json.dumps(json.loads(r.content), indent=4)))
    else:
        print("Request failed")
        print('Status code: {}'.format(r.status_code))
        print("Headers: {}".format(headers))
        print("Payload: {}".format(json.dumps(payload)))
        print('Response: {}'.format(json.dumps(json.loads(r.content), indent=4)))
        exit(1)
    return r
# endregion

# region get tag id
# get all tags
url = format(base_url)
print("Making a {} API call to {}".format(method, url))
all_tags = process_request(base_url, method, headers)

# get specific tag
all_tags_parsed = json.loads(all_tags.content)
tag_id = ""
for tag in all_tags_parsed['value']:
    url = ""+base_url+"/id:"+tag+""
    print("Making a {} API call to {}".format(method, url))
    tag = process_request(url, method, headers)
    tag_parse = json.loads(tag.content)
    if tag_parse['value']['name'] == vc_tag_name:
        tag_id = tag_parse['value']['id']
        break
# endregion

# pass the specific founded tag in vc_tag_id and vc_tag_name so that it may be captured by Calm.
if not tag_id:
    print("Error : tag not present")
    exit (1)
elif tag_id:
    print("vc_tag_id={}".format(tag_id))
    exit(0)
# endregion