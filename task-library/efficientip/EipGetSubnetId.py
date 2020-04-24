#region headers
# * authors:    igor.zecevic@nutanix.com
# * date:       30/03/2020
# task_name:    EipGetSubnetId
# description:  get subnet id
# input vars:   eip_site_id, eip_public_subnet, eip_mgmt_subnet
#               is_terminal, eip_min_free_ip
# output vars:  eip_public_subnet_id, eip_mgmt_subnet_id
#endregion

#region capture Calm variables
username = "@@{eip.username}@@"
password = "@@{eip.secret}@@"
api_server = "@@{eip_endpoint}@@"
site_id = "@@{eip_site_id}@@"
public_subnet_name = "@@{eip_public_subnet}@@"
mgmt_subnet_name = "@@{eip_mgmt_subnet}@@"
f5_subnet_name = "@@{eip_f5_subnet}@@"
f5_enabled = "@@{f5_enabled}@@"
min_free_ip = "@@{eip_min_free_ip}@@"
host_index = int("@@{calm_array_index}@@")
is_terminal = "1"  #means the subnet cannot contains others subnets as children
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
    elif (r.status_code == 204):
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

# region len2mask function
def len2mask(len):
    mask = ''
    if not isinstance(len, int) or len < 0 or len > 32:
        print("error")
        return None
    for t in range(4):
        if len > 7:
            mask += '255.'
        else:
            dec = 255 - (2**(8 - len) - 1)
            mask += str(dec) + '.'
        len -= 8
        if len < 0:
            len = 0
    return mask[:-1]
# endregion

# region get base2 count from int
def get_base2_count(x):
    i = 1
    while x != 2:
        x = x/2
        i = (i + 1)
    return i
# endregion

#region main processing

# region get mgmt subnet id
if (mgmt_subnet_name):
    subnet_name = mgmt_subnet_name
    # making the api call
    url = "{0}/ip_block_subnet_list?WHERE={1}='{2}'&WHERE={3}='{4}'&WHERE={5}='{6}'&TAGS=network.gateway".format(base_url, "site_id", site_id, "is_terminal", is_terminal, "subnet_name", subnet_name)
    print("Making a {} API call to {}".format(method, url))
    resp = process_request(url, method, headers)
    # parsing the response
    subnets = json.loads(resp.content)
    for subnet in subnets:
        if ((subnet['subnet_ip_free_size'] != int(min_free_ip)) and (subnet['subnet_name'] == mgmt_subnet_name)):
            host_base= get_base2_count(int(subnet['subnet_size']))
            cidr_netmask = (32 - host_base)
            netmask = len2mask(cidr_netmask)
            print("vm_mgmt_subnet_id={}".format(subnet['subnet_id']))
            print("vm_mgmt_netmask={}".format(netmask))
            print("vm_mgmt_gateway={}".format(subnet['tag_network_gateway']))
# endregion

# region get public subnet id
if (public_subnet_name):
    subnet_name = public_subnet_name
    # making the api call
    url = "{0}/ip_block_subnet_list?WHERE={1}='{2}'&WHERE={3}='{4}'&WHERE={5}='{6}'&TAGS=network.gateway".format(base_url, "site_id", site_id, "is_terminal", is_terminal, "subnet_name", subnet_name)
    print("Making a {} API call to {}".format(method, url))
    resp = process_request(url, method, headers)
    # parsing the response
    subnets = json.loads(resp.content)
    for subnet in subnets:
        if ((subnet['subnet_ip_free_size'] != int(min_free_ip)) and (subnet['subnet_name'] == public_subnet_name)):
            host_base= get_base2_count(int(subnet['subnet_size']))
            cidr_netmask = (32 - host_base)
            netmask = len2mask(cidr_netmask)
            print("vm_public_subnet_id={}".format(subnet['subnet_id']))
            print("vm_public_netmask={}".format(netmask))
            print("vm_public_gateway={}".format(subnet['tag_network_gateway']))
# endregion

# region get f5 subnet id
if ((host_index == 0) and (f5_enabled == "yes")):
    subnet_name = f5_subnet_name
    # making the api call
    url = "{0}/ip_block_subnet_list?WHERE={1}='{2}'&WHERE={3}='{4}'&WHERE={5}='{6}'".format(base_url, "site_id", site_id, "is_terminal", is_terminal, "subnet_name", subnet_name)
    print("Making a {} API call to {}".format(method, url))
    resp = process_request(url, method, headers)
    # parsing the response
    subnets = json.loads(resp.content)
    for subnet in subnets:
        if ((subnet['subnet_ip_free_size'] != int(min_free_ip)) and (subnet['subnet_name'] == f5_subnet_name)):
            print("vm_f5_subnet_id={}".format(subnet['subnet_id']))
# endregion
# endregion
exit(0)