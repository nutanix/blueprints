#region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     MITU Bogdan Nicolae (EEAS-EXT) <Bogdan-Nicolae.MITU@ext.eeas.europa.eu>
# *             stephane.bourdeaud@emeagso.lab
# * version:    2019/09/17
# task_name:    CalmGetRolesUuid
# description:  Gets the UUID for the "Project Admin", "Developer" and 
#               "Consumer" roles.
# output vars:  project_admin_role_uuid, developer_role_uuid, consumer_role_uuid
# endregion

#region capture Calm variables
username = '@@{pc.username}@@'
username_secret = "@@{pc.secret}@@"
api_server = "@@{pc_ip}@@"
# endregion

#region define variables
project_admin_role_uuid = ""
developer_role_uuid = ""
consumer_role_uuid = ""
#endregion

# region prepare api call
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/roles/list"
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

# Compose the json payload
payload = {
    "kind": "role", 
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
#endregion

#region process results
if resp.ok:
    print("Request was successful; processing results...")
    json_resp = json.loads(resp.content)
    #process each valid vlan range
    for role in json_resp['entities']:
        if role['status']['name'] == "Project Admin":
            project_admin_role_uuid = role['metadata']['uuid']
        if role['status']['name'] == "Developer":
            developer_role_uuid = role['metadata']['uuid']
        if role['status']['name'] == "Consumer":
            consumer_role_uuid = role['metadata']['uuid']
    print("project_admin_role_uuid={}".format(project_admin_role_uuid))
    print("developer_role_uuid={}".format(developer_role_uuid))
    print("consumer_role_uuid={}".format(consumer_role_uuid))
else:
    #api call failed
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
#endregion