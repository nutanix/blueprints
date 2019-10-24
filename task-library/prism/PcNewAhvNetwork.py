#region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     MITU Bogdan Nicolae (EEAS-EXT) <Bogdan-Nicolae.MITU@ext.eeas.europa.eu>
# * version:    2019/09/17
# task_name:    PcNewAhvNetwork
# description:  Given a vlan id, create an ipam managed network in AHV.
# output vars:  ahv_network_uuid, ahv_network_name
# endregion

#region capture Calm variables
username = '@@{pc.username}@@'
username_secret = "@@{pc.secret}@@"
api_server = "@@{pc_ip}@@"
project_vlan_id = "@@{project_vlan_id}@@"
nutanix_cluster_uuid = "@@{nutanix_cluster_uuid}@@"
# endregion

#region define variables
dns_server = "8.8.8.8"
ahv_network_name = "belbru-nut-vlan{}test".format(project_vlan_id)
ahv_network_address = "10.55.{}.0".format(project_vlan_id)
ahv_network_prefix = "24"
ahv_network_gw = "10.55.{}.1".format(project_vlan_id)
ahv_network_pool_range = "10.55.{0}.2 10.55.{0}.253".format(project_vlan_id)
#endregion

#region prepare api call
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v0.8/networks?proxyClusterUuid={}".format(nutanix_cluster_uuid)
length = 100
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
    "name":ahv_network_name,
    "vlanId":project_vlan_id,
    "ipConfig":{"dhcpOptions":{"domainNameServers":dns_server},
    "networkAddress":ahv_network_address,
    "prefixLength":ahv_network_prefix,
    "defaultGateway":ahv_network_gw,
    "pool":[{"range":ahv_network_pool_range}]}
}
# endregion

#region make the api call
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
#endregion

#region process results
if resp.ok:
    print("AHV network was successfully created.")
    json_resp = json.loads(resp.content)
    print("ahv_network_uuid={}".format(json_resp['networkUuid']))
    print("ahv_network_name={}".format(ahv_network_name))
    exit(0)
else:
    #api call failed
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
#endregion