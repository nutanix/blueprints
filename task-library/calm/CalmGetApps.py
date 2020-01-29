# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:       stephane.bourdeaud@nutanix.com
# * version:      2020/01/22
# task_name:      CalmGetApp
# description:    This script gets the list of application instances from Calm.
# TODO: test
# endregion

# region capture Calm macros
pc_ip = '@@{pc_ip}@@'
username = '@@{pc_user.username}@@'
username_secret = '@@{pc_user.secret}@@'
# endregion

# region prepare variables
headers = {'content-type': 'application/json'}
# endregion

# region REST call: Get Apps
method = 'POST'
url = "https://{}:9440/api/nutanix/v3/apps/list".format(pc_ip)
payload = {
    "kind": "app",
    "length": 250
}
print("Making a {} API call to {}".format(method, url))
resp = urlreq(
    url,
    verb=method,
    params=json.dumps(payload),
    headers=headers,
    auth='BASIC',
    user=username,
    passwd=username_secret,
    verify=False
)

if resp.ok:
    json_resp = json.loads(resp.content)
    if json_resp['metadata']['total_matches'] > 0:
        print(json_resp)
    else:
        print("Could not find any apps.")
        exit(1)
    exit(0)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
