# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     MITU Bogdan Nicolae (EEAS-EXT) <Bogdan-Nicolae.MITU@ext.eeas.europa.eu>
# *             stephane.bourdeaud@emeagso.lab
# * version:    2019/09/18
# task_name:    CalmSetProjectOwner
# description:  Given a Calm project UUID, updates the owner reference section 
#               in the metadata.
# endregion

#region capture Calm variables
username = "@@{pc.username}@@"
username_secret = "@@{pc.secret}@@"
api_server = "@@{pc_ip}@@"
nutanix_calm_user_uuid = "@@{nutanix_calm_user_uuid}@@"
nutanix_calm_user_upn = "@@{calm_username}@@"
project_uuid = "@@{project_uuid}@@"
#endregion

#region prepare api call (get project)
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/projects_internal/{}".format(project_uuid)
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "GET"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
#endregion

#region make the api call (get project)
print("Making a {} API call to {}".format(method, url))
resp = urlreq(
    url,
    verb=method,
    auth='BASIC',
    user=username,
    passwd=username_secret,
    headers=headers,
    verify=False
)
# endregion

#region process the results (get project)
if resp.ok:
   print("Successfully retrieved project details for project with uuid {}".format(project_uuid))
   project_json = json.loads(resp.content)
else:
    #api call failed
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion

#region prepare api call (update project with acp)
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/projects_internal/{}".format(project_uuid)
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "PUT"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Compose the json payload
#removing stuff we don't need for the update
project_json.pop('status', None)
project_json['metadata'].pop('create_time', None)
#updating values
project_json['metadata']['owner_reference']['uuid'] = nutanix_calm_user_uuid
project_json['metadata']['owner_reference']['name'] = nutanix_calm_user_upn
for acp in project_json['spec']['access_control_policy_list']:
    acp["operation"] = "ADD"
payload = project_json
#endregion

#region make the api call (update project with acp)
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

#region process the results (update project with acp)
if resp.ok:
    print("Successfully updated the project owner reference to {}".format(nutanix_calm_user_upn))
    exit(0)
else:
    #api call failed
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
#endregion