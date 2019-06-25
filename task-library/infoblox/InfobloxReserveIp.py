# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     andy.schmid@nutanix.com, stephane.bourdeaud@nutanix.com
# * version:    2019/06/12, v1
# task_name:    InfobloxReserveIp
# description:  Given a hostname, this script will get the next available IPv4
#               address in the specified network and then register the A and PTR
#               records in Infoblox.
# endregion

base_url = "@@{infoblox_url}@@"
user = "@@{infoblox.username}@@"
password = "@@{infoblox.secret}@@"
hostname = "@@{calm_application_name}@@.@@{domain}@@"


def process_request(url, method, user, password, headers, payload=None):
	if (payload != None):
		payload = json.dumps(payload)
	r = urlreq(url, verb=method, auth="BASIC", user=user, passwd=password, params=payload, verify=False, headers=headers)
	return r

headers = {'Accept': 'application/json', 'Content-Type': 'application/json; charset=UTF-8'}

### Get IP
reservation_payload = {}
reservation_payload['match_client'] = "RESERVED";
reservation_payload['name'] = hostname
reservation_payload['ipv4addr'] = "func:nextavailableip:@@{network}@@"
payload = json.dumps(reservation_payload)
print "Payload: " + payload

url = base_url + "fixedaddress";
r = process_request(url, 'POST', user, password, headers, reservation_payload)
ip = r.json().replace(':',"/").split('/')[2]
print "INFOBLOX_IP=", ip


#Create A Record
url = base_url + "record:a";
dns_a_record_payload = {}
dns_a_record_payload['ipv4addr'] = ip;
dns_a_record_payload['name'] = hostname
dns_a_record_payload['view'] = 'default'

r = process_request(url, 'POST', user, password, headers, dns_a_record_payload)

#Create PTR Record
url = base_url + "record:ptr"
dns_ptr_payload = {}
dns_ptr_payload['ipv4addr'] = ip
dns_ptr_payload['name'] = "@@{calm_application_name}@@"
dns_ptr_payload['ptrdname'] = hostname

r = process_request(url, 'POST', user, password, headers, dns_ptr_payload)
