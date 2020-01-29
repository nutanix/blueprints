# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# TODO Fill in this section with your information
# * author:     stephane.bourdeaud@nutanix.com, igor.zecevic@nutanix.com
# * version:    v1.0/20200129 - initial version
# task_name:    PhpIPAMGetFreeIp
# description:  Given a phpIPAM server ip/fqdn, a phpIPAM app id, a token
#               and a subnet id, return the first available IP address in 
#               that subnet. The current VM name and Calm user will be used
#               for ip registration with ipam.               
# outputvars:   phpipam_free_ip
# endregion

# region capture Calm variables
api_server = "@@{phpipam_ip}@@"
phpipam_token = "@@{phpipam_token}@@"
phpipam_app_id = "@@{phpipam_app_id}@@"
phpipam_subnet_id = "@@{phpipam_subnet_id}@@"
hostname = "@@{name}@@" #* this is a built-in Calm macro which returns the VM name
owner = "@@{calm_username}@@" #* this is a built-in Calm macro which returns the Calm user username
# endregion

# region prepare api call
api_server_port = "443"
api_server_endpoint = "/api/{}/addresses/first_free/{}".format(phpipam_app_id,phpipam_subnet_id)
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "POST"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'token' : phpipam_token
}

# Compose the json payload
payload = {
    "hostname": hostname, 
    "description": hostname,
    "owner": owner
}
# endregion

# region make api call
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
    print("Request was successful. Status code: {}".format(resp.status_code))
    print ("IP {} was registered for host {} with owner {}".format(json.loads(resp.content)['data'],hostname,owner))
    print('phpipam_free_ip= {}'.format(json.loads(resp.content)['data']))
    exit(0)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
