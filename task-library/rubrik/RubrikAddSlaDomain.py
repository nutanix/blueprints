# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:       Geluykens, Andy <Andy.Geluykens@pfizer.com>
# * version:      2019/06/04
# task_name:      RubrikAddSlaDomain
# description:    This script adds an SLA domain to a VM in Rubrik.  Use
# RubrikGetSlaDomainId and RubrikGetVmId before this task.
# endregion

# region capture Calm macros
username = '@@{rubrik.username}@@'
username_secret = "@@{rubrik.secret}@@"
api_server = "@@{rubrik_ip}@@"
rubrik_vm_id = "@@{rubrik_vm_id}@@"
rubrik_sla_domain_id = "@@{rubrik_sla_domain_id}@@"
# endregion

# region prepare variables
api_server_port = "443"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
# endregion

# region add sla domain (API call)
api_server_endpoint = "/api/internal/nutanix/vm/{}".format(rubrik_vm_id)
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "PATCH"
payload = {
    "configuredSlaDomainId": rubrik_sla_domain_id
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
