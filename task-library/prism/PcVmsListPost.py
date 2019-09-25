# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@nutanix.com, lukasz@nutanix.com
# * version:    20190925
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

# region functions
def make_prism_api_call_v3(url,method,username,username_secret,payload,length):
    """Makes a v3 API call to a Nutanix Prism instance.

    Args:
        url: The URL for the Prism REST API endpoint.
        method: The REST method to use.
        username: The Prism user name.
        username_secret: The Prism user name password.
        payload: The JSON payload to include in the call.
        length: The number of objects to return with each call response.
    
    Returns:
        An array of entities.
    """
    entities = []
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }
    while True:
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

        # deal with the result/response
        if resp.ok:
            json_resp = json.loads(resp.content)
            print("Processing results from {} to {} out of {}".format(
                json_resp['metadata']['offset'], 
                json_resp['metadata']['length']+json_resp['metadata']['offset'],
                json_resp['metadata']['total_matches']))
            for entity in json_resp['entities']:
                entities.append(entity)
            if json_resp['metadata']['length'] == length:
                payload = {
                    "kind": "vm",
                    "offset": json_resp['metadata']['length'] + json_resp['metadata']['offset'] + 1,
                    "length": length
                }
            else:
                return entities
                break
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print("Payload: {}".format(json.dumps(payload)))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(
                json.dumps(
                    json.loads(resp.content), 
                    indent=4)))
            exit(1)
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

# Compose the json payload
payload = {
    "kind": "vm",
    "offset": 0,
    "length": length
}
# endregion

# region make api call and process the results
entities = make_prism_api_call_v3(
    url,
    method,
    username,
    username_secret,
    payload,
    length)
print(json.dumps(entities))
# endregion
