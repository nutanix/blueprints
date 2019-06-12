# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:       Geluykens, Andy <Andy.Geluykens@pfizer.com>
# * version:      2019/06/04
# task_name:      RubrikGetVmId
# description:    This script gets the specified VM object id from the Rubrik
# server.
# endregion

# region capture Calm macros
username = '@@{rubrik.username}@@'
username_secret = "@@{rubrik.secret}@@"
api_server = "@@{rubrik_ip}@@"
# endregion

# region prepare variables
api_server_port = "443"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
rubrik_vm_id = ""
# endregion

# region GET API call to retrieve the VM id
api_server_endpoint = "/api/internal/nutanix/vm?name=@@{name}@@"
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "GET"

print("Making a {} API call to {}".format(method, url))

resp = urlreq(
    url,
    verb=method,
    auth='BASIC',
    user=username,
    passwd=username_secret,
    params=json.dumps(payload),
    headers=headers,
    verify=False
)

if resp.ok:
    json_resp = json.loads(resp.content)
    vm_id = json_resp['data'][0]['id']
    print("rubrik_vm_id={}".format(vm_id))
    exit(0)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
