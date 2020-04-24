# region headers
# * authors:    igor.zecevic@nutanix.com
# * date:       30/03/2020
# task_name:    EipReserveHost
# description:  Check DNS and Reserve an Hostname
#               check if hostname is not exising on the DNS
#               if exists, increment the suffix number
# input vars:   eip_site_id, app_prefix, source_app, app_status
#               eip_dns_zone, instance_count, rr_type, f5_enabled
# output vars:  eip_host_list
#endregion

#region capture Calm variables
username = "@@{eip.username}@@"
password = "@@{eip.secret}@@"
api_server = "@@{eip_endpoint}@@"
dns_zone = "@@{eip_dns_zone}@@"
app_prefix = "@@{app_prefix}@@"
app_source = "@@{source_app}@@"
app_status = "@@{app_status}@@"
host_index = int("@@{calm_array_index}@@")
number_instance = int("@@{instance_count}@@")
f5_enabled = "@@{f5_enabled}@@"
rr_type = "A"
#endregion

# region prepare api call
api_server_port = "443"
api_server_endpoint = "/rest"
method = "GET"
base_url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
# endregion

#region API call function
def process_request(url, method, headers, payload=None):
    if (payload is not None):
        payload = json.dumps(payload)
    r = urlreq(url, verb=method, auth='BASIC', user=username, passwd=password, params=payload, verify=False, headers=headers)
    if r.ok:
        print("Request was successful")
        print("Status code: {}".format(r.status_code))
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

# region check dns hostname
def eip_dns_check(hostname_dns, rr_type):
    api_server_port = "443"
    api_server_endpoint = "/rest"
    method = "GET"
    base_url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    # make the api call
    url = "{0}/dns_rr_list?WHERE={1}='{2}'&WHERE={3}='{4}'".format(base_url, "rr_type", rr_type, "rr_full_name", hostname_dns)
    print("Making a {} API call to {}".format(method, url))
    resp = process_request(url, method, headers)
    return resp
# endregion

#region main processing
i = 1
host_list = []
if ((host_index > 0) and (app_status == "provisioning")):
    print("This task is not required on this Instance ..")
    print("Skipping this task ..")
    exit(0)
elif ((app_status == "provisioning") and (host_index == 0)):
    for instance in range(0,number_instance):
        loop_break = 0
        while True:
            #checking if hostname exists on DNS
            hostname = app_prefix+"-"+app_source+"-0"+str(i)
            hostname_dns = hostname+"."+dns_zone
            check_dns = eip_dns_check(hostname_dns, rr_type)
            if (check_dns.status_code == 204) or (check_dns.status_code == 200 and json.loads(check_dns.content)[0]['delayed_delete_time'] == "1"):
                host_list.append(format(hostname))
                loop_break = 1
                i = i +1
                break
            elif (check_dns.status_code == 200 and json.loads(check_dns.content)[0]['delayed_delete_time'] == "0" and json.loads(check_dns.content)[0]['delayed_create_time'] == "0"):
                print ("DNS already exists.. looping")
                i = i + 1
        if ((loop_break == 1) and (instance == number_instance)):
            break
elif ((host_index > 0) and (app_status == "running")):
    while True:
            #checking if hostname exists on DNS
            hostname = app_prefix+"-"+app_source+"-0"+str(i)
            hostname_dns = hostname+"."+dns_zone
            check_dns = eip_dns_check(hostname_dns, rr_type)
            if (check_dns.status_code == 204) or (check_dns.status_code == 200 and json.loads(check_dns.content)[0]['delayed_delete_time'] == "1"):
                host_list.append(format(hostname))
                loop_break = 1
                i = i +1
                break
            elif (check_dns.status_code == 200 and json.loads(check_dns.content)[0]['delayed_delete_time'] == "0" and json.loads(check_dns.content)[0]['delayed_create_time'] == "0"):
                print ("DNS already exists.. looping")
                i = i + 1

# reserving hostname for the F5 virtual server
if ((host_index == 0) and (app_status == "provisioning") and (f5_enabled == "yes")):
    i = 1
    while True:
        #checking if hostname exists on DNS
        hostname = app_prefix+"-"+app_source+"-VS-0"+str(i)
        hostname_dns = hostname+"."+dns_zone
        check_dns = eip_dns_check(hostname_dns, rr_type)
        if (check_dns.status_code == 204) or (check_dns.status_code == 200 and json.loads(check_dns.content)[0]['delayed_delete_time'] == "1"):
            host_f5 = hostname
            print("eip_host_f5={}".format(host_f5))
            loop_break = 1
            i = i +1
            break
        elif (check_dns.status_code == 200 and json.loads(check_dns.content)[0]['delayed_delete_time'] == "0" and json.loads(check_dns.content)[0]['delayed_create_time'] == "0"):
            print ("DNS already exists.. looping")
            i = i + 1
# endregion
print("eip_host_list={}".format(host_list))
# endregion
exit(0)
