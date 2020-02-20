# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@emeagso.lab
# * version:    2020/01/22
# task_name:    CalmRemoveApp
# description:  Given an app name, delete the Calm App. 
# endregion

#region capture Calm variables
api_server = "@@{pc_ip}@@"
username = "@@{pc.username}@@"
username_secret = "@@{pc.secret}@@"
app_name = "@@{target_app}@@"
#endregion

#region prepare api call (get apps)
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/apps/list"
length = 250
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
    "kind": "app", 
    "length":length, 
    "offset":0
}
# endregion

#region make the api call (get apps)
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

#region process the results (get apps)
if resp.ok:
    print ("Request status code {} on {}".format(resp.status_code,resp.request.url))
    json_resp = json.loads(resp.content)
    for app in json_resp['entities']:
        if app_name == app['metadata']['name']:
            print ("Deleting application {}".format(app['metadata']['name']))
            #region prepare api call (delete app)
            api_server_port = "9440"
            api_server_endpoint = "/api/nutanix/v3/apps/{}".format(app['metadata']['uuid'])
            url = "https://{}:{}{}".format(
                api_server,
                api_server_port,
                api_server_endpoint
            )
            method = "DELETE"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            #endregion
            #region make api call (delete app)
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
            #endregion
            #region process results (delete app)
            if resp.ok:
                print ("Request status code {} on {}".format(resp.status_code,resp.request.url))
                print ("Application {} is deleting.".format(app['metadata']['name']))
                app_state = app['status']['state']
                app_uuid = app['metadata']['uuid']
                while app_state != 'deleted':
                    sleep(15)
                    method = 'GET'
                    url = "https://{}:9440/api/nutanix/v3/apps/{}".format(
                        api_server,
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
                            print("App could not be deleted.")
                            print ("Response content:")
                            print(json.dumps(json.loads(resp.content),indent=4))
                            exit(1)
                        app_state = json_resp['status']['state']
                    else:
                        print ("Request failed with status code {}".format(resp.status_code))
                        print ("Response content:")
                        print(json.dumps(json.loads(resp.content),indent=4))
                        print("Headers: {}".format(headers))
                        exit(1)
            else:
                print ("Request failed with status code {}".format(resp.status_code))
                print ("Response content:")
                print(json.dumps(json.loads(resp.content),indent=4))
                print("Headers: {}".format(headers))
                exit(1)
            #endregion
else:
    print ("Request failed with status code {}".format(resp.status_code))
    print ("Response content:")
    print(json.dumps(json.loads(resp.content),indent=4))
    print("Headers: {}".format(headers))
    print("Payload: {}".format(payload))
    exit(1)
# endregion
