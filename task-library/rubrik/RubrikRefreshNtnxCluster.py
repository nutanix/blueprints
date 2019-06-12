# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:       Geluykens, Andy <Andy.Geluykens@pfizer.com>
# * version:      2019/06/04
# task_name:      RubrikRefreshNtnxCluster
# description:    This script refreshes the data displayed in Rubrik for the
# specified Nutanix cluster (use RubrikGetClusterId to get the cluster id).
# Follow up with RubrikWaitUntilClusterRefresh.
# endregion

# region capture Calm macros
username = '@@{rubrik.username}@@'
username_secret = "@@{rubrik.secret}@@"
api_server = "@@{rubrik_ip}@@"
rubrik_ntnx_cluster_id = "@@{rubrik_ntnx_cluster_id}@@"
# endregion

# region prepare variables
api_server_port = "443"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
# endregion

# region POST API call to refresh the Nutanix cluster data in Rubrik
api_server_endpoint = "/api/internal/nutanix/cluster/{}/refresh".format(rubrik_ntnx_cluster_id)
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "POST"

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
    refresh_id = json_resp['id']
    print("rubrik_refresh_id={}".format(refresh_id))
    exit(0)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
