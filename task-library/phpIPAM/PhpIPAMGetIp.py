# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@nutanix.com, igor.zecevic@nutanix.com
# * version:    v1.0/20200129 - initial version
# task_name:    PhpIPAMGetIp
# description:  Given a phpIPAM server ip/fqdn, a phpIPAM app id, an 
#               authentication token and an ip address, returns information
#               about that ip address from ipam.  Assumes a single IP will
#               be returned.
# output vars:  phpipam_ip_id, phpipam_ip_subnet_id,phpipam_ip_hostname,
#               phpipam_ip_mac, phpipam_ip_owner
# endregion

# region capture Calm variables
api_server = "@@{phpipam_ip}@@"
phpipam_token = "@@{phpipam_token}@@"
phpipam_app_id = "@@{phpipam_app_id}@@"
ip = "@@{ip}@@"
# endregion

# region prepare api call
#! note that if your app security in php-ipam is set to 'none'
#! you will have to change the port to 80 and url to http.
api_server_port = "443"
api_server_endpoint = "/api/{}/addresses/search/{}/".format(phpipam_app_id,ip)
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
    print("phpipam_ip_id: {}".format(json.loads(resp.content)['data'][0]['id']))
    print("phpipam_ip_subnet_id: {}".format(json.loads(resp.content)['data'][0]['subnetId']))
    print("phpipam_ip_hostname: {}".format(json.loads(resp.content)['data'][0]['hostname']))
    print("phpipam_ip_mac: {}".format(json.loads(resp.content)['data'][0]['mac']))
    print("phpipam_ip_owner: {}".format(json.loads(resp.content)['data'][0]['owner']))
    exit(0)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
