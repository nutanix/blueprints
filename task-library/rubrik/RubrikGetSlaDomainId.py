# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:       Geluykens, Andy <Andy.Geluykens@pfizer.com>
# * version:      2019/06/05
# task_name:      RubrikGetSlaDomainId
# description:    This script gets the id of the specified Rubrik SLA domain.
# endregion

# region capture Calm macros
username = '@@{rubrik.username}@@'
username_secret = "@@{rubrik.secret}@@"
api_server = "@@{rubrik_ip}@@"
sla_domain = "@@{sla_domain}@@"
# endregion

# region Get Rubrik SLA domain ID
api_server_port = "443"
api_server_endpoint = "/api/v1/sla_domain?name={}".format(sla_domain)
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "GET"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

print("Making a {} API call to {}".format(method, url))

resp = urlreq(
    url,
    verb=method,
    auth='BASIC',
    user=username,
    passwd=username_secret,
    headers=headers,
    verify=False
)

if resp.ok:
    json_resp = json.loads(resp.content)
    sla_domain_id = json_resp['data'][0]['id']
    print("rubrik_sla_domain_id={}".format(sla_domain_id))
    exit(0)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
