# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     Bogdan-Nicolae.MITU@ext.eeas.europa.eu,
# *             stephane.bourdeaud@nutanix.com
# * version:    2019/09/18
# task_name:    CalmGetUserProjects
# description:  Counts how many projects a user owns.
#               Returns an error if the count is too high.
# endregion

#region capture Calm variables
username = '@@{pc.username}@@'
username_secret = "@@{pc.secret}@@"
api_server = "@@{pc_ip}@@"
nutanix_calm_user_uuid = "@@{nutanix_calm_user_uuid}@@"
nutanix_calm_user_name = "@@{calm_username}@@"
# endregion

#region define variables
max_project_count = 3
user_project_count = 0
#endregion

# region prepare api call
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

# Compose the json payload
payload = {
    "kind":"project",
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

#region process the results
if resp.ok:
    json_resp = json.loads(resp.content)
    print("Processing results from {} to {}".format(json_resp['metadata']['offset'], json_resp['metadata']['length']))
    for project in json_resp['entities']:
        if project['metadata'].get("owner_reference"):
            #print("Comparing {} with {}".format(nutanix_calm_user_uuid,project['metadata']['owner_reference']['uuid']))
            if nutanix_calm_user_uuid == project['metadata']['owner_reference']['uuid']:
                user_project_count = user_project_count + 1
        else:
            print("Project {} has no owner".format(project['status']['name']))
    while json_resp['metadata']['length'] is length:
        payload = {
            "kind": "project",
            "length":length,
            "offset": json_resp['metadata']['length'] + json_resp['metadata']['offset'] + 1
        }
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
        if resp.ok:
            json_resp = json.loads(resp.content)
            print("Processing results from {} to {}".format(json_resp['metadata']['offset'], json_resp['metadata']['offset'] + json_resp['metadata']['length']))
            for project in json_resp['entities']:
                if project['metadata'].get("owner_reference"):
                    #print("Comparing {} with {}".format(nutanix_calm_user_uuid,project['metadata']['owner_reference']['uuid']))
                    if nutanix_calm_user_uuid == project['metadata']['owner_reference']['uuid']:
                        user_project_count = user_project_count + 1
                else:
                    print("Project {} has no owner".format(project['status']['name']))
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print("Payload: {}".format(json.dumps(payload)))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            exit(1)
    if user_project_count >= max_project_count:
        print("User {0} already owns {1} projects which is greater than the maximum allowed ({2})".format(nutanix_calm_user_name,user_project_count,max_project_count))
        exit(1)
    else:
        print("User {0} owns {1} projects which is lower than the maximum allowed ({2})".format(nutanix_calm_user_name,user_project_count,max_project_count))
        exit(0)
else:
    # print the content of the response (which should have the error message)
    print("Request failed", json.dumps(
        json.loads(resp.content),
        indent=4
    ))
    print("Headers: {}".format(headers))
    print("Payload: {}".format(payload))
    exit(1)
# endregion