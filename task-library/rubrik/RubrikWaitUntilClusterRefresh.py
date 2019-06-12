# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:       Geluykens, Andy <Andy.Geluykens@pfizer.com>
# * version:      2019/06/04
# task_name:      RubrikWaitUntilClusterRefresh
# description:    This script refreshes the data displayed in Rubrik for the
# specified Nutanix cluster. Invoke this task asfter RubrikRefreshNtnxCluster
# which will provide the refresh id.
# endregion

# region capture Calm macros
username = '@@{rubrik.username}@@'
username_secret = "@@{rubrik.secret}@@"
api_server = "@@{rubrik_ip}@@"
rubrik_refresh_id = "@@{rubrik_refresh_id}@@"
# endregion

# region prepare variables
api_server_port = "443"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
# endregion

# region GET API call to check the status of the refresh task
api_server_endpoint = "/api/internal/nutanix/cluster/request/{}".format(rubrik_refresh_id)
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "GET"

print("Making a {} API call to {}".format(method, url))

while True:
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
        refresh_status = json_resp['status']
        if json_resp['status'] == "SUCCEEDED":
            print("Refresh task status is {}".format(json_resp['status']))
            exit(0)
            break
        if json_resp['status'] == "FAILED":
            print("Refresh task status is {}".format(json_resp['status']))
            exit(1)
            break
        print("Refresh task status is {}".format(json_resp['status']))
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print("Payload: {}".format(json.dumps(payload)))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)
        break
    sleep(5)
# endregion
