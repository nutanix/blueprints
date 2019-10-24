# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@nutanix.com
# * version:    20191022
# task_name:    PeGetImageUuid
# description:  Gets the uuid of the specified image from Prism Element.
# output:       image_uuid, image_vm_disk_id
# endregion

# region capture Calm variables
username = "@@{pe.username}@@"
username_secret = "@@{pe.secret}@@"
api_server = "@@{pe_ip}@@"
image_name = "@@{image_name}@@"
# endregion

# region prepare api call
# Form method, url and headers for the API call
api_server_port = "9440"
api_server_endpoint = "/PrismGateway/services/rest/v2.0/images/"
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "GET"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
# endregion

# region make api call
# make the API call and capture the results in the variable called "resp"
print("Making a {} API call to {}".format(method, url))
# ! Get rid of verify=False if you're using proper certificates
resp = urlreq(
    url,
    verb=method,
    auth='BASIC',
    user=username,
    passwd=username_secret,
    headers=headers,
    verify=False
)

# deal with the result/response
if resp.ok:
    json_resp = json.loads(resp.content)
    for image in json_resp['entities']:
        if image['name'] == image_name:
            print "image_uuid = {}".format(image['uuid'])
            print "image_vm_disk_id = {}".format(image['vm_disk_id'])
            exit(0)
    print("Image not found!")
    exit(1)
else:
    # print the content of the response (which should have the error message)
    print("Request failed", json.dumps(
        json.loads(resp.content),
        indent=4
    ))
    print("Headers: {}".format(headers))
    exit(1)
# endregion
