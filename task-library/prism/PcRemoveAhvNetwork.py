#region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@nutanix.com
# * version:    2019/09/18
# task_name:    PcRemoveAhvNetwork
# description:  Given an AHV subnet UUID, delete that subnet from the AHV
#               cluster.
# endregion

#region capture Calm variables
username = '@@{pc.username}@@'
username_secret = "@@{pc.secret}@@"
api_server = "@@{pc_ip}@@"
ahv_network_uuid = "@@{ahv_network_uuid}@@"
# endregion

#region prepare api call
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/subnets/{}".format(ahv_network_uuid)
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
# endregion

#region make the api call
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

#region process results
if resp.ok:
    print("AHV network was successfully deleted.")
    json_resp = json.loads(resp.content)
    exit(0)
else:
    #api call failed
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
#endregion