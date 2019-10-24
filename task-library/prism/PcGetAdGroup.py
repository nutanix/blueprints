#region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     Bogdan-Nicolae.MITU@ext.eeas.europa.eu,
# *             stephane.bourdeaud@nutanix.com
# * version:    2019/09/17
# task_name:    PcGetAdGroup
# description:  Given an AD group, return information from the directory.
# output vars:  ad_group_name,ad_group_dn
# endregion

#region capture Calm variables
username = '@@{pc.username}@@'
username_secret = "@@{pc.secret}@@"
api_server = "@@{pc_ip}@@"
project_vlan_id = "@@{project_vlan_id}@@"
directory_uuid = "@@{directory_uuid}@@"
#endregion

#region define variables
ad_group_name = "NUT_EEAS_R_TLAB{}Admins".format(project_vlan_id)
#endregion

# region prepare api call
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/directory_services/{}/search".format(directory_uuid)
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
    "query":ad_group_name,
    "returned_attribute_list":[
        "memberOf",
        "member",
        "userPrincipalName",
        "distinguishedName"
    ],
    "searched_attribute_list":[
        "name",
        "userPrincipalName",
        "distinguishedName"
    ]
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
    if len(json_resp['search_result_list']) == 0:
        print("The Active Directory group {} does not exist.".format(ad_group_name))
        exit(1)
    else:
        print("The Active Directory group {} exists.".format(ad_group_name))
        ad_group_dn = json_resp['search_result_list'][0]['attribute_list'][0]['value_list'][0]
        print("ad_group_name={}".format(ad_group_name))
        print("ad_group_dn={}".format(ad_group_dn))
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