# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@nutanix.com, lukasz@nutanix.com
# * version:    20190606
# task_name:    PcVmsListPost
# description:  Gets the list of VMs from Prism Central.
# endregion

# region capture Calm variables
# * Capture variables here. This makes sure Calm macros are not referenced
# * anywhere else in order to improve maintainability.
username = '@@{pc.username}@@'
username_secret = "@@{pc.secret}@@"
api_server = "@@{pc_ip}@@"
# endregion

# region prepare api call
# Form method, url and headers for the API call
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/vms/list"
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "POST"
length = 50
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Compose the json payload
payload = {
    "kind": "vm",
    "offset": 0,
    "length": length
}
# endregion

# region make api call
# make the API call and capture the results in the variable called "resp"
# because the response could have multiple pages (by default, only 20 results
# are returned by the API, unless you specify a length in the json payload), we
# will loop until there are no more results
while True:
    print("Making a {} API call to {}".format(method, url))
    # ! Get rid of verify=False if you're using proper certificates
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

    # deal with the result/response
    if resp.ok:
        json_resp = json.loads(resp.content)
        print("Processing results from {} to {} out of {}".format(json_resp['metadata']['offset'], json_resp['metadata']['length']+json_resp['metadata']['offset'], json_resp['metadata']['total_matches']))
        #* add your own processing here
        #print("Offset is: {}, Length is: {}".format(json_resp['metadata']['offset'],json_resp['metadata']['length']))
        #print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        if json_resp['metadata']['length'] == length:
            payload = {
                "kind": "vm",
                "offset": json_resp['metadata']['length'] + json_resp['metadata']['offset'] + 1,
                "length": length
            }
        else:
            break
    else:
        # print the content of the response (which should have the error message)
        print("Request failed")
        print("Headers: {}".format(headers))
        print("Payload: {}".format(json.dumps(payload)))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)
# endregion
