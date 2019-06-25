# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@nutanix.com, lukasz@nutanix.com
# * version:    20190606
# task_name:    PeAddVmToPd
# description:  Adds the virtual machine provisioned by Calm to the specified
# protection domain.
# endregion

# region capture Calm variables
username = '@@{pe.username}@@'
username_secret = "@@{pe.secret}@@"
nutanix_cluster_ip = "@@{nutanix_cluster_ip}@@"
vm_uuid = "@@{vm_uuid}@@"
protection_domain_name = "@@{protection_domain_name}@@"
# endregion

# region Add VM to Protection Domain
api_server = nutanix_cluster_ip
api_server_port = "9440"
api_server_endpoint = "/PrismGateway/services/rest/v2.0/protection_domains/{}/protect_vms".format(protection_domain_name)
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
payload = {
  "uuids": [
    vm_uuid
  ]
}

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
