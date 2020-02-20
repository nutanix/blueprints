# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@nutanix.com
# * version:    v1.0/20200129 - initial version
# task_name:    PhpIPAMGetSubnetId
# description:  Given a phpIPAM server ip/fqdn, app id, section id,
#               token and a vlan id, return the phpIPAM subnet object id 
#               belonging to that VLAN. Assumes only one subnet per vlan.
# output vars:  phpipam_subnet_id
# endregion

# region capture Calm variables
# * Capture variables here. This makes sure Calm macros are not referenced
# * anywhere else in order to improve maintainability.
api_server = "@@{phpipam_ip}@@"
phpipam_token = "@@{phpipam_token}@@"
phpipam_app_id = "@@{phpipam_app_id}@@"
vlan_id = "@@{vlan_id}@@"
phpipam_section_id = "@@{phpipam_section_id}@@"
# endregion

#region GET phpIPAM vlan object id based on vlan id number
# region prepare api call
#! note that if your app security in php-ipam is set to 'none'
#! you will have to change the port to 80 and url to http.
api_server_port = "443"
api_server_endpoint = "/api/{}/vlan/".format(phpipam_app_id)
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
    found = False
    for vlan in json.loads(resp.text)['data']:
        if vlan['number'] == vlan_id:
            print "Found phpIPAM vlan object {} with vlan number {}".format(vlan['vlanId'],vlan_id)
            phpipam_vlanId = vlan['vlanId']
            found = True
            break
        else:
            continue
    if found == False:
        print "Could not find any vlan with number {}".format(vlan_id)
        exit(1)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion

#endregion

#region GET subnets and match with phpIPAM vlan object id
# region prepare api call
#! note that if your app security in php-ipam is set to 'none'
#! you will have to change the port to 80 and url to http.
api_server_port = "443"
api_server_endpoint = "/api/{}/sections/{}/subnets".format(phpipam_app_id,phpipam_section_id)
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
    found = False
    for subnet in json.loads(resp.text)['data']:
        if subnet['vlanId'] == phpipam_vlanId:
            print "phpipam_subnet_id= {}".format(subnet['id'])
            found = True
            break
        else:
            continue
    if found == True:
        exit(0)
    else:
        print "Could not find a subnet for vlan object id {} with vlan number {}!".format(phpipam_vlanId,vlan_id)
        exit(1)
    exit(0)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
#endregion