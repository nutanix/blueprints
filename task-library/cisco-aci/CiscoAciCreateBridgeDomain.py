# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     jose.gomez@nutanix.com, stephane.bourdeaud@nutanix.com
# * version:    2019/06/11 - v1
# task_name:    CiscoAciCreateBridgeDomain
# description:  Creates a Cisco ACI Bridge Domain object in the specified
#               VRF as well as a subnet, gateway and L3 out default route.
# endregion

# region capture Calm variables
username = "@@{aci_user.username}@@"
username_secret = "@@{aci_user.secret}@@"
api_server = "@@{aci_ip}@@"
aci_tenant_name = "@@{aci_tenant_name}@@"
aci_bd_name = "@@{aci_bd_name}@@"
aci_subnet = '@@{aci_subnet}@@'
aci_subnet_mask = '@@{aci_subnet_mask}@@'
aci_subnet_gw = '@@{aci_subnet_gw}@@'
aci_vrf_name = '@@{aci_vrf_name}@@'
aci_l3_out_name = '@@{aci_l3_out_name}@@'
# endregion

# region prepare variables
aci_bd_dn = "uni/tn-{}/BD-{}".format(aci_tenant_name, aci_bd_name)
aci_subnet_gw_ip = "{}/{}".format(aci_subnet_gw, aci_subnet_mask)
aci_subnet_rn = "subnet-[{}]".format(aci_subnet_gw_ip)
aci_subnet_dn = "{}/{}".format(aci_bd_dn, aci_subnet_rn)
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

# region POST new Bridge Domain
# prepare
api_server_endpoint = "/api/node/mo/{}.json".format(aci_bd_dn)
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "POST"

# Compose the json payload
payload = {
    "fvBD": {
        "attributes": {
            "OptimizeWanBandwidth": "no",
            "annotation": "",
            "arpFlood": "true",
            "descr": "",
            "dn": aci_bd_dn,
            "epClear": "no",
            "epMoveDetectMode": "",
            "status": "created,modified",
            "intersiteBumTrafficAllow": "no",
            "intersiteL2Stretch": "no",
            "ipLearning": "yes",
            "limitIpLearnToSubnets": "yes",
            "llAddr": "::",
            "mcastAllow": "no",
            "multiDstPktAct": "bd-flood",
            "name": aci_bd_name,
            "nameAlias": "",
            "ownerKey": "",
            "ownerTag": "",
            "type": "regular",
            "unicastRoute": "yes",
            "unkMacUcastAct": "proxy",
            "unkMcastAct": "flood",
            "vmac": "not-applicable"
        },
        "children": [
            {
                "fvSubnet": {
                    "attributes": {
                        "dn": aci_subnet_dn,
                        "ip": aci_subnet_gw_ip,
                        "preferred": "true",
                        "scope": "public",
                        "ctrl": "unspecified",
                        "rn": aci_subnet_rn,
                        "status": "created,modified"
                    },
                    "children": []
                }
            },
            {
                "fvRsCtx": {
                    "attributes": {
                        "tnFvCtxName": aci_vrf_name,
                        "status": "created,modified"
                    },
                    "children": []
                }
            },
            {
                "fvRsBDToOut": {
                    "attributes": {
                        "tnL3extOutName": aci_l3_out_name,
                        "status": "created,modified"
                    },
                    "children": []
                }
            }
        ]
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
    print("Request to add bridge domain {} in tenant {} was successful".format(
        aci_bd_name,
        aci_tenant_name
        )
    )
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
