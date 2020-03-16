# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       10/03/2020
# task_name:    VcRestGetCategory
# description:  Retreives a specific category id based on the category's name
#               The scripts list all categories and filter
# input vars:   vc_cookie, api_server, vc_category_name
# output vars:  vc_category_id
# endregion

# region capture Calm variables
vc_cookie = "@@{vc_api_session}@@" # retreived from VcRestLogin
api_server = "@@{vc_endpoint}@@"
vc_category_name = "@@{calm_application_name}@@"
# endregion

# region prepare api call
api_server_port = "443"
api_server_endpoint = "/rest/com/vmware/cis/tagging/category"
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

# region get category id
# get all categories
url = format(base_url)
print("Making a {} API call to {}".format(method, url))
all_categories = process_request(base_url, method, headers)

# get specific category
all_categories_parsed = json.loads(all_categories.content)
category_id = ""
for category in all_categories_parsed['value']:
    url = ""+base_url+"/id:"+category+""
    print("Making a {} API call to {}".format(method, url))
    category = process_request(url, method, headers)
    category_parse = json.loads(category.content)
    if category_parse['value']['name'] == vc_category_name:
        category_id = category_parse['value']['id']
        break
# endregion

# pass the specific founded category in vc_category_id so that it may be captured by Calm.
if not category_id:
    print("Error : category not present")
    exit (1)
elif category_id:
    print("vc_category_id={}".format(category_id))
    exit(0)
# endregion