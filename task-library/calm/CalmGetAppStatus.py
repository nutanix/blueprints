# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:       stephane.bourdeaud@nutanix.com
# * version:      2019/06/06
# task_name:      CalmGetAppStatus
# description:    This script loops on the status of an application instance
# until it is running or in an error state.
# endregion

# region capture Calm macros
pc_ip = '@@{pc_ip}@@'
username = '@@{pc_user.username}@@'
username_secret = '@@{pc_user.secret}@@'
app_name = "@@{app_name}@@"
# endregion

# region prepare variables
headers = {'content-type': 'application/json'}
# endregion

# region REST call: Get application instance status
method = 'POST'
url = "https://{}:9440/api/nutanix/v3/apps/list".format(
    pc_ip
)

payload = {
  "kind": "app"
}

print("Making a {} API call to {}".format(method, url))

resp = urlreq(
    url,
    verb=method,
    headers=headers,
    auth="BASIC",
    user=username,
    passwd=username_secret,
    params=json.dumps(payload),
    verify=False
)

if resp.ok:
    json_resp = json.loads(resp.content)
    for app in json_resp['entities']:
        if app['status']['name'] == app_name:
            app_uuid = app['status']['uuid']
            print("Status:", app['status']['state'])
            if app['status']['state'] == 'running':
                exit(0)
            app_state = app['status']['state']
            while app_state != 'running':
                sleep(15)
                method = 'GET'
                url = "https://{}:9440/api/nutanix/v3/apps/{}".format(
                    pc_ip,
                    app_uuid
                )
                print("Making a {} API call to {}".format(method, url))
                resp = urlreq(
                    url,
                    verb=method,
                    headers=headers,
                    auth="BASIC",
                    user=username,
                    passwd=username_secret,
                    verify=False
                )
                if resp.ok:
                    json_resp = json.loads(resp.content)
                    print("Status:", json_resp['status']['state'])
                    if json_resp['status']['state'] is "error":
                        exit(1)
                    app_state = json_resp['status']['state']
                else:
                    print("Request failed")
                    print("Headers: {}".format(headers))
                    print("Payload: {}".format(json.dumps(payload)))
                    print('Status code: {}'.format(resp.status_code))
                    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
                    exit(1)
            exit(0)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)

# endregion
