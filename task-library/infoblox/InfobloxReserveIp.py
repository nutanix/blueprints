# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     andy.schmid@nutanix.com, stephane.bourdeaud@nutanix.com
# * version:    2019/06/12, v1
# task_name:    InfobloxReserveIp
# description:  Given a hostname, this script will get the next available IPv4
#               address in the specified network and then register the A and PTR
#               records in Infoblox.
# endregion

# region capture Calm variables
# * Capture variables here. This makes sure Calm macros are not referenced
# * anywhere else in order to improve maintainability.
username = '@@{infoblox.username}@@'
username_secret = "@@{infoblox.secret}@@"
api_server = "@@{infoblox_ip}@@"
hostname = "@@{calm_application_name}@@.@@{domain}@@"
network = "@@{network}@@"
name = "@@{calm_application_name}@@"
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

# region API call function
def process_request(url, method, user, password, headers, payload=None):
    if (payload is not None):
        payload = json.dumps(payload)
    r = urlreq(url, verb=method, auth="BASIC", user=user, passwd=password, params=payload, verify=False, headers=headers)
    return r
# endregion

# region get IP
reservation_payload = {}
reservation_payload['match_client'] = "RESERVED";
reservation_payload['name'] = hostname
reservation_payload['ipv4addr'] = "func:nextavailableip:{}".format(network)
payload = json.dumps(reservation_payload)

url = "{}fixedaddress".format(base_url)
method = "POST"
print("Making a {} API call to {}".format(method, url))

resp = process_request(url, method, username, username_secret, headers, reservation_payload)
ip = resp.json().replace(':', "/").split('/')[2]
print("INFOBLOX_IP={}".format(ip))
# endregion

# region create A Record
url = "{}record:a".format(base_url)
method = "POST"
print("Making a {} API call to {}".format(method, url))

dns_a_record_payload = {}
dns_a_record_payload['ipv4addr'] = ip;
dns_a_record_payload['name'] = hostname
dns_a_record_payload['view'] = 'default'

resp = process_request(url, method, username, username_secret, headers, dns_a_record_payload)
# endregion

# region create PTR record
url = "{}record:ptr".format(base_url)
method = "POST"
print("Making a {} API call to {}".format(method, url))

dns_ptr_payload = {}
dns_ptr_payload['ipv4addr'] = ip
dns_ptr_payload['name'] = name
dns_ptr_payload['ptrdname'] = hostname

resp = process_request(url, method, username, username_secret, headers, dns_ptr_payload)
# endregion
