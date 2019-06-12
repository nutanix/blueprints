# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:       Geluykens, Andy <Andy.Geluykens@pfizer.com>
# * version:      2019/06/04
# task_name:      RubrikGetClusterId
# description:    This script gets the specified Nutanix AHV cluster id from
# the Rubrik server.
# endregion

# region capture Calm macros
username = '@@{rubrik.username}@@'
username_secret = "@@{rubrik.secret}@@"
api_server = "@@{rubrik_ip}@@"
nutanix_cluster_name = "@@{nutanix_cluster_name}@@"
# endregion

# region prepare variables
api_server_port = "443"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
rubrik_ntnx_cluster_id = ""
# endregion

# region GET API call to retrieve the Nutanix AHV cluster id from Rubrik
api_server_endpoint = "/api/internal/nutanix/cluster"
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "GET"

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

if resp.ok:
    json_resp = json.loads(resp.content)
    for cluster in json_resp['data']:
        if cluster['name'] == nutanix_cluster_name:
            print("rubrik_ntnx_cluster_id={}".format(cluster['id']))
            exit(0)
    if rubrik_ntnx_cluster_id == "":
        print("Could not find a Nutanix cluster with name {} on Rubrik server {}".format(
            nutanix_cluster_name,
            api_server
            )
        )
        exit(1)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
