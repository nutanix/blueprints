#region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@nutanix.com
# * version:    2019/09/17
# task_name:    CalmGetEnvUuid
# description:  Get existing project environments from Calm.
# output vars:  environment_uuid
# endregion

#region capture Calm variables
username = '@@{pc.username}@@'
username_secret = "@@{pc.secret}@@"
api_server = "@@{pc_ip}@@"
#endregion

#region define variables
environment_uuids = []
#endregion

# region prepare api call
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/environments/list"
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
  "kind": "environment",
  "offset": 0,
  "length": length
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
    for environment in json_resp['entities']:
        environment_uuids.append(environment['metadata']['uuid'])
    print("environment_uuid={}".format(environment_uuids[0]))
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