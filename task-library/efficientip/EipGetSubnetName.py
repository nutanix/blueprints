#region headers
# * authors:    igor.zecevic@nutanix.com
# * date:       30/03/2020
# task_name:    EipGetSubnets
# description:  Get available networks attached to a site on EfficientIP
# input vars:   eip_site_name, eip_min_free_ip
# output vars:  subnet_lists
#endregion

# this script is used to retreive a list of available subnets on EIP
# this list is provided during at the application launch using dynaminy variable
# all print are commented

#region capture Calm variables
username = "@@{eip_username}@@"
password = "@@{eip_password}@@"
api_server = "@@{eip_endpoint}@@"
site_name = "@@{eip_site_name}@@"
min_free_ip = "@@{eip_min_free_ip}@@"
is_terminal = "1"  #means that the subnet cannot contains others subnets as children
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
    if not r.ok:
        print("Request failed")
        exit(1)
    return r
#endregion

#region main processing
# make the api call
url = "{0}/ip_block_subnet_list?WHERE={1}='{2}'&WHERE={3}='{4}'".format(base_url, "is_terminal", is_terminal, "parent_site_name", site_name)
#print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)

# parsing the response
subnets_list = []
subnets = json.loads(resp.content)
for subnet in subnets:
  if subnet['subnet_ip_free_size'] != int(min_free_ip):
      subnets_list.append(format(subnet['subnet_name']))

# return array use for dynamic variable input           
print(", ".join(subnets_list))
#endregion