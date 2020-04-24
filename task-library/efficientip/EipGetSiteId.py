#region headers
# * authors:    igor.zecevic@nutanix.com
# * date:       30/03/2020
# task_name:    EipGetSiteId
# description:  get site id
# input vars:   eip_site_name
# output vars:  eip_site_id
#endregion

#region capture Calm variables
username = "@@{eip.username}@@"
password = "@@{eip.secret}@@"
api_server = "@@{eip_endpoint}@@"
site_name = "@@{eip_site_name}@@"
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
        #if r.content:
        #    print('Response: {}'.format(json.dumps(json.loads(r.content), indent=4)))
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

#region main processing
# make the api call
url = "{0}/ip_site_list?WHERE={1}='{2}'".format(base_url, "site_name", site_name)
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers)

# parsing the response
sites = json.loads(resp.content)
for site in sites:
  if site['site_name'] == site_name:
       print("eip_site_id={}".format(site['site_id']))
#endregion