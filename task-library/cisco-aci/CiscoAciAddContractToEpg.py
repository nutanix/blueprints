# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     jose.gomez@nutanix.com, stephane.bourdeaud@nutanix.com
# * version:    2019/06/11 - v1
# task_name:    CiscoAciAddContractToEpg
# description:  Adds a Cisco ACI contract to an EPG object in the specified
#               tenant and application profile.
# endregion

# region capture Calm variables
username = "@@{aci_user.username}@@"
username_secret = "@@{aci_user.secret}@@"
api_server = "@@{aci_ip}@@"
aci_tenant_name = "@@{aci_tenant_name}@@"
aci_ap_name = "@@{aci_ap_name}@@"
aci_epg_name = "@@{aci_epg_name}@@"
aci_default_contract = "@@{aci_default_contract}@@"
# endregion

# region prepare variables
aci_epg_dn = "uni/tn-{}/ap-{}/epg-{}".format(
    aci_tenant_name,
    aci_ap_name,
    aci_epg_name
)
# endregion

# region generic prepare api call
api_server_port = "443"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
# endregion

# region login
# prepare
api_server_endpoint = "/api/aaaLogin.json"
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "POST"

# Compose the json payload
payload = {
    "aaaUser": {
        "attributes": {
            "name": username,
            "pwd": username_secret
        }
    }
}

# make the API call and capture the results in the variable called "resp"
print("Making a {} API call to {}".format(method, url))
# ! Get rid of verify=False if you're using proper certificates
resp = urlreq(
    url,
    verb=method,
    params=json.dumps(payload),
    headers=headers,
    verify=False
)

# deal with the result/response
if resp.ok:
    print("Login request was successful")
    json_resp = json.loads(resp.content)
    aci_token = json_resp['imdata'][0]['aaaLogin']['attributes']['token']
    headers = {'content-type': 'application/json', 'Cookie': 'APIC-Cookie=' + aci_token}
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion

# region POST to edit EPG (endpoint group)
# prepare
api_server_endpoint = "/api/node/mo/{}.json".format(aci_epg_dn)
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "POST"

# Compose the json payload
payload = {
    "fvRsProv": {
        "attributes": {
            "tnVzBrCPName": aci_default_contract,
            "status": "created,modified"
        },
        "children": []
    }
}

# make the API call and capture the results in the variable called "resp"
print("Making a {} API call to {}".format(method, url))
# ! Get rid of verify=False if you're using proper certificates
resp = urlreq(
    url,
    verb=method,
    params=json.dumps(payload),
    headers=headers,
    verify=False
)

# deal with the result/response
if resp.ok:
    print("Request to add contract {} to EPG {} in tenant {} under application profile {} was successful".format(
        aci_default_contract,
        aci_epg_name,
        aci_tenant_name,
        aci_ap_name
    ))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion

# region logout
# prepare
api_server_endpoint = "/api/aaaLogout.json"
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "POST"

# Compose the json payload
payload = {
    "aaaUser": {
        "attributes": {
            "name": username,
            "pwd": username_secret
        }
    }
}

# make the API call and capture the results in the variable called "resp"
print("Making a {} API call to {}".format(method, url))
# ! Get rid of verify=False if you're using proper certificates
resp = urlreq(
    url,
    verb=method,
    params=json.dumps(payload),
    headers=headers,
    verify=False
)

# deal with the result/response
if resp.ok:
    print("Logout request was successful")
    exit(0)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
