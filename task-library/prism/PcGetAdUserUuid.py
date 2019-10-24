# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     Bogdan-Nicolae.MITU@ext.eeas.europa.eu,
# *             stephane.bourdeaud@nutanix.com
# * version:    2019/10/18
# task_name:    PcGetAdUserUuid
# description:  Returns the Prism Central object uuid of the Calm user and its
#               directory service.
# output vars:  nutanix_calm_user_uuid, directory_uuid
# endregion

#region capture Calm variables
username = '@@{pc.username}@@'
username_secret = "@@{pc.secret}@@"
api_server = "@@{pc_ip}@@"
nutanix_calm_user_upn = "@@{calm_username}@@"
# endregion

# region prepare api call
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/users/list"
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
filter = "user_principal_name=={}".format(nutanix_calm_user_upn)
payload = {
    "kind":"user",
    "filter": filter,
    "length":length
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
    for directory_user in json_resp['entities']:
        nutanix_calm_user_uuid = directory_user['metadata']['uuid']
        directory_uuid = directory_user['spec']['resources']['directory_service_user']['directory_service_reference']['uuid']
        print("nutanix_calm_user_uuid={}".format(nutanix_calm_user_uuid))
        print("directory_uuid={}".format(directory_uuid))
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