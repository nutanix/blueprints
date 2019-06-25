# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     andy.schmid@nutanix.com, stephane.bourdeaud@nutanix.com
# * version:    2019/06/25, v1
# task_name:    InfobloxReserveMacIp
# description:  Given a hostname, this script will get the next available IPv4
#               address in the specified network and then reserve the IP using
#               the VM mac address.
# endregion

# region capture Calm variables
# * Capture variables here. This makes sure Calm macros are not referenced
# * anywhere else in order to improve maintainability.
username = "@@{infoblox.username}@@"
username_secret = "@@{infoblox.secret}@@"
api_server = "@@{infoblox_ip}@@"
vm_name = "@@{vm_name}@@"
# grabbing the mac address from a VM called WinVM in the blueprint
vm_mac = "@@{WinVM.mac_address}@@"
# endregion

# region prepare variables
api_server_port = "443"
# ! You may have to change the endpoint based on your Infoblox version
api_server_endpoint = "/wapi/v2.7.1/"
base_url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
# endregion

# region login Infoblox
method = "GET"
print("Making a {} API call to {}".format(method, url))
resp = urlreq(
    base_url,
    verb=method,
    headers=headers,
    verify=False,
    auth="BASIC",
    user=username,
    passwd=username_secret
)

# deal with the result/response
if resp.ok:
    print("Login request was successful")
    # let's store the session cookies for future use
    cookie_jar = resp.cookies
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion

# region get the host record from Infoblox
url = "{}record:host?name~={}".format(base_url, vm_name)
method = "GET"
print("Making a {} API call to {}".format(method, url))
resp = urlreq(
    url,
    verb=method,
    headers=headers,
    verify=False,
    cookies=cookie_jar
)
# deal with the result/response
if resp.ok:
    print("Grabbed the hostname record from Infoblox")
    json_resp = json.loads(resp.content)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion

# region modify the host record to add MAC address and DHCP reservation
url = "{}{}".format(base_url, json.loads(response.content)[0]['ipv4addrs'][0]['_ref'])
method = "PUT"
print("Making a {} API call to {}".format(method, url))
payload = {
    'configure_for_dhcp': True,
    'mac':vm_mac
}
resp = urlreq(
    url,
    verb=method,
    params=json.dumps(payload),
    headers=headers,
    verify=False,
    cookies=cookie_jar
)
if resp.ok:
    print("Configured for DHCP with MAC reservation in Infoblox")
    json_resp = json.loads(resp.content)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion