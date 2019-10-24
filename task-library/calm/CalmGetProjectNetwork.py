#region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@nutanix.com
# * version:    2019/09/20
# task_name:    CalmGetNetworkProject
# description:  Given a project UUID, returns the first AHV network assigned to 
#               that project. 
# output vars:  ahv_subnet
# endregion

#region capture Calm variables
project_name = "@@{calm_project_name}@@"
api_server = "@@{pc_ip}@@"
username = "@@{pc.username}@@"
username_secret = "@@{pc.secret}@@"
#endregion

#region prepare api call (get projects)
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/projects/list"
length = 100
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "POST"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
payload = {
    "kind": "project", 
    "length":length, 
    "offset":0
}
# endregion

#region make the api call
print("Making a {} API call to {}".format(method, url))
resp = urlreq(
    url,
    verb=method,
    auth='BASIC',
    user=username,
    passwd=username_secret,
    params=json.dumps(payload),
    headers=headers,
    verify=False
)
# endregion


#region process the results
if resp.ok:
    print ("Request status code {} on {}".format(resp.status_code,resp.request.url))
    json_resp = json.loads(resp.content)
    for project in json_resp['entities']:
        if project_name == project['status']['name']:
            ahv_subnet = project['spec']['resources']['subnet_reference_list'][0]['name']
            print ("ahv_subnet={}".format(ahv_subnet))
    exit(0)
else:
    #api call failed
    print("Request failed: {}".format(resp.status_code))
    #print("Headers: {}".format(headers))
    #print('Status code: {}'.format(resp.status_code))
    #print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion