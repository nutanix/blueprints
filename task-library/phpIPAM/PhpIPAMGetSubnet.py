# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@nutanix.com
# * version:    v1.0/20200129 - initial version
# task_name:    PhpIPAMGetSubnet
# description:  Given a php-ipam server ip/fqdn, and a subnet id, return
#               information about that subnet (mask, gateway, used IPs, 
#               total IPs, free IPs). It assumes the gateway and nameservers
#               have been defined on the subnet.
# output vars:  phpipam_subnet_mask, phpipam_subnet_bitmask,  
#               phpipam_subnet_gateway, phpipam_subnet_total_ips,
#               phpipam_subnet_nameservers
# endregion

# region capture Calm variables
# * Capture variables here. This makes sure Calm macros are not referenced
# * anywhere else in order to improve maintainability.
api_server = "@@{phpipam_ip}@@"
phpipam_token = "@@{phpipam_token}@@"
phpipam_app_id = "@@{phpipam_app_id}@@"
phpipam_subnet_id = "@@{phpipam_subnet_id}@@"
# endregion

# region prepare api call
#! note that if your app security in php-ipam is set to 'none'
#! you will have to change the port to 80 and url to http.
api_server_port = "443"
api_server_endpoint = "/api/{}/subnets/{}/".format(phpipam_app_id,phpipam_subnet_id)
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "GET"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'token' : phpipam_token
}
# endregion

# region make api call
# make the API call and capture the results in the variable called "resp"
print("Making a {} API call to {}".format(method, url))
# ! Get rid of verify=False if you're using proper certificates
resp = urlreq(
    url,
    verb=method,
    headers=headers,
    verify=False
)

# deal with the result/response
if resp.ok:
    print("Request was successful. Status code: {}".format(resp.status_code))
    #print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    print("phpipam_subnet_mask: {}".format(json.loads(resp.content)['data']['calculation']['Subnet netmask']))
    print("phpipam_subnet_bitmask: {}".format(json.loads(resp.content)['data']['calculation']['Subnet bitmask']))
    print("phpipam_subnet_gateway: {}".format(json.loads(resp.content)['data']['gateway']['ip_addr']))
    print("phpipam_subnet_total_ips: {}".format(json.loads(resp.content)['data']['calculation']['Number of hosts']))
    print("phpipam_subnet_nameservers: {}".format(json.loads(resp.content)['data']['nameservers']['namesrv1']))
    exit(0)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
