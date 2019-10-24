#region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     MITU Bogdan Nicolae (EEAS-EXT) <Bogdan-Nicolae.MITU@ext.eeas.europa.eu>
# * version:    2019/09/17
# task_name:    CalmSetProjectBp
# description:  Publish existing CALM Blueprints on the new project created. 
#               Blueprints will be added into a list, which will be populated by
#               Nutanix Admins and stored on a CALM macro.
# endregion

#region capture Calm variables
username = "@@{pc.username}@@"
username_secret = "@@{pc.secret}@@"
api_server = "@@{pc_ip}@@"
project_name = "@@{project_name}@@"
project_uuid = "@@{project_uuid}@@"
# endregion

#region prepare api call (get marketplace items)
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/marketplace_items/list"
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
    "filter":"app_state==PUBLISHED",
    "length":length
}
# endregion
#region make the api call (get marketplace items)
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
#region process the results (get marketplace items)
if resp.ok:
    print ("Request status code {} on {}".format(resp.status_code,resp.request.url))
    json_resp = json.loads(resp.content)
    marketplace_items = json_resp['entities']
    #process each marketplace item
    for marketplace_item in marketplace_items:
        marketplace_item_uuid = marketplace_item['metadata']['uuid']
        #region prepare api call (get marketplace information)
        api_server_endpoint = "/api/nutanix/v3/calm_marketplace_items/{}".format(marketplace_item_uuid)
        url = "https://{}:{}{}".format(
            api_server,
            api_server_port,
            api_server_endpoint
        )
        method = "GET"
        #endregion
        #region make the api call (get marketplace information)
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
        #region process results (get marketplace information)
        if resp.ok:
            print ("Request status code {} on {}".format(resp.status_code,resp.request.url))
            json_resp = json.loads(resp.content)
            json_resp['metadata'].pop('owner_reference', None)
            json_resp.pop('status', None)
            json_resp['metadata'].pop('create_time', None)
            marketplace_item_project =  {
                "kind": "project",
                "name": project_name,
                "uuid": project_uuid
            }
            json_resp['spec']['resources']['project_reference_list'].append(marketplace_item_project)
            #region prepare the api call (publish marketplace item to project)
            payload = json_resp
            method = "PUT"
            #endregion
            #region make the api call (publish marketplace item to project)
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
            #region process results (publish marketplace item to project)
            if resp.ok:
                print ("Request status code {} on {}".format(resp.status_code,resp.request.url))
                print "Marketplace item with uuid {} is published.".format(marketplace_item_uuid)
            else:
                print ("Request failed with status code {}".format(resp.status_code))
                print ("Response content:")
                print(json.dumps(json.loads(resp.content),indent=4))
                print("Headers: {}".format(headers))
                print("Payload: {}".format(payload))
                exit(1)
            #endregion
        else:
            print ("Request failed with status code {}".format(resp.status_code))
            print ("Response content:")
            print(json.dumps(json.loads(resp.content),indent=4))
            print("Headers: {}".format(headers))
            print("Payload: {}".format(payload))
            exit(1)
        #endregion
else:
    print ("Request failed with status code {}".format(resp.status_code))
    print ("Response content:")
    print(json.dumps(json.loads(resp.content),indent=4))
    print("Headers: {}".format(headers))
    print("Payload: {}".format(payload))
    exit(1)
#endregion