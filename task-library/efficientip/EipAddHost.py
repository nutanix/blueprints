#region headers
# * authors:    igor.zecevic@nutanix.com
# * date:       30/03/2020
# task_name:    EipAddHost
# description:  Create an IP/Host on EfficientIp
# input vars:   eip_site_id, eip_public_subnet_id, eip_dns_zone
#               vm_subnet_id, app_status, add_flag, ip_name_type, max_find
# output vars:  vm_hostname, vm_ip
#endregion

#region capture Calm variables
username = "@@{eip.username}@@"
password = "@@{eip.secret}@@"
api_server = "@@{eip_endpoint}@@"
site_id = "@@{eip_site_id}@@"
vm_subnet_id = "@@{vm_subnet_id}@@"
dns_zone = "@@{eip_dns_zone}@@"
app_status = "@@{app_status}@@"
host_index = int('@@{calm_array_index}@@')
add_flag = "new_only" # flag used to track new ip creation only
max_find = "1" # search for 1 available address
ip_name_type = "A" # create a DNS record
#endregion

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
    elif ((r.status_code == 400) and (json.loads(r.content)['errmsg']) == "Address already exists"):
        print('Response: {}'.format(json.dumps(json.loads(r.content), indent=4)))
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

# region find next free address function
def efficient_ip_find_free_address(subnet_id, max_find=max_find):
    api_server_port = "443"
    api_server_endpoint = "/rpc"
    method = "GET"
    base_url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    # make the api call
    url = "{0}/ip_find_free_address?{1}={2}&{3}={4}".format(base_url, "subnet_id", subnet_id, "max_find", max_find)
    print("Making a {} API call to {}".format(method, url))
    resp = process_request(url, method, headers)
    return resp
# endregion

# region add host function
def efficient_ip_add_host(host_ip, hostname_dns, site_id=site_id, add_flag=add_flag):
    api_server_port = "443"
    api_server_endpoint = "/rest"
    method = "POST"
    base_url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    # make the api call
    url = "{0}/ip_add?{1}={2}&{3}={4}&{5}={6}&{7}={8}&{9}={10}".format(base_url, "hostaddr", host_ip, "ip_name", hostname_dns, "ip_name_type", ip_name_type, "site_id", site_id, "add_flag", add_flag)
    print("Making a {} API call to {}".format(method, url))
    resp = process_request(url, method, headers)
    return resp
# endregion

# region main processing
# region prepare and reserve hostname
# sleep count based on the replica level
sleep_count = (host_index * 3)
print ("Sleep for: "+str(sleep_count)+" seconds")
sleep(sleep_count)
if (app_status == "provisioning"):
    # use the calm_array variable @@{eip_host_list}@@ if provisionning the apps
    hostname = @@{calm_array_eip_host_list}@@[host_index]
    hostname_dns = hostname+"."+dns_zone
    print("vm_hostname={}".format(hostname))
elif (app_status == "running"):
    # use the service variable @@{eip_host_list}@@[0] if ScalingOut/Up the apps
    hostname = @@{eip_host_list}@@[0]
    hostname_dns = hostname+"."+dns_zone
    print("vm_hostname={}".format(hostname))
# endregion

# region create host/ip
i = 0
while True:
    next_free_ip = efficient_ip_find_free_address(vm_subnet_id)
    host_ip = json.loads(next_free_ip.content)[0]['hostaddr']
    add_host = efficient_ip_add_host(host_ip, hostname_dns)
    # if the address already exists, loop to find a new one
    if ((add_host.status_code == 400) and (json.loads(add_host.content)['errmsg']) == "Address already exists"):
        sleep_count = (host_index * 2)
        print ("Sleep for: "+str(sleep_count)+" seconds")
        sleep(sleep_count)
        i = (i + 1)
        if (i > 10):
            print("Error: couldn't find any available address..")
            exit(1)
    elif (add_host.status_code == 201):
        print ("vm_ip={}".format(host_ip))
        break
# endregion
# endregion
exit(0)