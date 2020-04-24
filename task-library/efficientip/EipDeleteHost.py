#region headers
# * authors:    igor.zecevic@nutanix.com
# * date:       30/03/2020
# task_name:    EIpDeleteHost
# description:  Delete an IP/Host on EfficientIp
# input vars:   vm_hostname, vm_ip, eip_dns_zone
# output vars:  
#endregion

#region capture Calm variables
username = "@@{eip.username}@@"
password = "@@{eip.secret}@@"
api_server = "@@{eip_endpoint}@@"
dns_zone = "@@{eip_dns_zone}@@"
vm_hostname = "@@{vm_name}@@"
vm_ip = "@@{vm_ip}@@"
# endregion

#region API call function
def process_request(url, method, headers, payload=None):
    if (payload is not None):
        payload = json.dumps(payload)
    r = urlreq(url, verb=method, auth='BASIC', user=username, passwd=password, params=payload, verify=False, headers=headers)
    if r.ok:
        print("Request was successful")
        print("Status code: {}".format(r.status_code))
        if (r.status_code == 204):
            print("Response: No Content here..")
            exit(1)
    else:
        print("Request failed")
        print('Status code: {}'.format(r.status_code))
        print("Headers: {}".format(headers))
        if (payload is not None):
            print("Payload: {}".format(json.dumps(payload)))
        if r.content:
            print('Response: {}'.format(json.dumps(json.loads(r.content), indent=4)))
        exit(1)
    return r
#endregion

#region main processing
# region prepare api call
api_server_port = "443"
api_server_endpoint = "/rest"
base_url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
# endregion

# region delete ip addresses
hostname_dns = vm_hostname+"."+dns_zone
# get ip
method = "GET"
url = "{0}/ip_address_list?WHERE={1}='{2}'&WHERE={3}='{4}'".format(base_url, "name", hostname_dns, "hostaddr", vm_ip)
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)
ip_id = json.loads(resp.content)[0]['ip_id']
# delete ip
method = "DELETE"
url = "{0}/ip_delete?{1}={2}".format(base_url, "ip_id", ip_id)
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)
# endregion
# endregion
exit(0)