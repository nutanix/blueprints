#region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     Bogdan-Nicolae.MITU@ext.eeas.europa.eu,
# *             stephane.bourdeaud@nutanix.com
# * version:    2019/09/17
# task_name:    PcGetAdGroupUuid
# description:  Given an AD group, return information from the directory.
# output vars:  ad_group_uuid
# endregion

#region capture Calm variables
username = '@@{pc.username}@@'
username_secret = "@@{pc.secret}@@"
api_server = "@@{pc_ip}@@"
project_vlan_id = "@@{project_vlan_id}@@"
directory_uuid = "@@{directory_uuid}@@"
ad_group_dn = "@@{ad_group_dn}@@"
ad_group_name = "@@{ad_group_name}@@"
nutanix_calm_user_upn = "@@{calm_username}@@"
#endregion

#region define variables
ad_group_uuid = ""
#endregion

# region prepare api call
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/user_groups/list"
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
    "kind":"user_group",
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
    #look at each group and determine if it matches our AD group for this project
    for directory_group in json_resp['entities']:
        print("Comparing {0} with {1}".format(ad_group_dn.lower(),directory_group['status']['resources']['directory_service_user_group']['distinguished_name']))
        if ad_group_dn.lower() == directory_group['status']['resources']['directory_service_user_group']['distinguished_name']:
            ad_group_uuid = directory_group['metadata']['uuid']
            print("ad_group_uuid={}".format(ad_group_uuid))
            exit(0)
    #adding processing if there is more than 1 page of results returned
    while json_resp['metadata']['length'] is length:
        payload = {
            "kind": "user",
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
            for directory_group in json_resp['entities']:
                print("Comparing {0} with {1}".format(ad_group_dn,directory_group['status']['resources']['directory_service_user_group']['distinguished_name']))
                if ad_group_dn == directory_group['status']['resources']['directory_service_user_group']['distinguished_name']:
                    ad_group_uuid = directory_group['metadata']['uuid']
                    print("ad_group_uuid={}".format(ad_group_uuid))
                    exit(0)
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print("Payload: {}".format(json.dumps(payload)))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            exit(1)
    if ad_group_uuid == "":
        print("Group {} does not have a UUID in Prism Central. Creating UUID...".format(ad_group_name))
        #region create idempotence identifier
        # region prepare api call
        api_server_port = "9440"
        api_server_endpoint = "/api/nutanix/v3/idempotence_identifiers"
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
            "count": 1,
            "client_identifier": nutanix_calm_user_upn,
            "valid_duration_in_minutes": 2
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
            json_resp = json.loads(resp.content)
            nutanix_calm_idempotence_identifier = json_resp['uuid_list'][0]
        else:
            # print the content of the response (which should have the error message)
            print("Request to create idempotence identifier failed", json.dumps(
                json.loads(resp.content),
                indent=4
            ))
            print("Headers: {}".format(headers))
            print("Payload: {}".format(payload))
            exit(1)
        #endregion
        #endregion

        #region create AD group UUID
        # region prepare api call
        api_server_port = "9440"
        api_server_endpoint = "/api/nutanix/v3/idempotence_identifiers/salted"
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
            "name_list":[ad_group_name]
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
            json_resp = json.loads(resp.content)
            print("Successfully created UUID for AD group {}".format(ad_group_name))
            print(json_resp)
            ad_group_uuid = json_resp['name_uuid_list'][0][ad_group_name]
            print("ad_group_uuid={}".format(ad_group_uuid))
        else:
            # print the content of the response (which should have the error message)
            print("Request to create UUID failed", json.dumps(
                json.loads(resp.content),
                indent=4
            ))
            print("Headers: {}".format(headers))
            print("Payload: {}".format(payload))
            exit(1)
        #endregion
        #endregion
    else:
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