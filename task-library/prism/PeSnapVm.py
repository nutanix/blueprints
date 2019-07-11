# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@nutanix.com
# * version:    2019/06/26, v1.0
# task_name:    PeSnapVm
# description:  Takes a snapshot of the virtual machine (AHV). Precede with
#               PcGetVmUuid.py to grab the virtual machine uuid and with
#               PcGetClusterIp.py to get the Prism Element cluster IP.
# endregion

# region capture Calm variables
# * Capture variables here. This makes sure Calm macros are not referenced
# * anywhere else in order to improve maintainability.
username = '@@{pe.username}@@'
username_secret = "@@{pe.secret}@@"
api_server = "@@{nutanix_cluster_ip}@@"
vm_uuid = "@@{vm_uuid}@@"
# endregion

# region prepare api call
api_server_port = "9440"
api_server_endpoint = "/PrismGateway/services/rest/v2.0/snapshots"
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "POST"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Compose the json payload
payload = {
    "snapshot_specs": [
    {
      "snapshot_name": "PeSnapVm",
      "vm_uuid": vm_uuid
    }
  ]
}
# endregion

# region make api call
# make the API call and capture the results in the variable called "resp"
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

# deal with the result/response
if resp.ok:
    print("Request was successful")
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(0)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
