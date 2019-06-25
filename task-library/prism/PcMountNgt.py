# region headers
# escript-template v20190523 / stephane.bourdeaud@nutanix.com
# * author:       stephane.bourdeaud@nutanix.com
# * version:      2019/06/04
# task_name:      PcMountNgt
# description:    This script mounts the Nutanix Guest Tools on the AHV
#                 virtual machine provisioned by Calm.
# endregion

# region capture Calm macros
pc_user = "@@{pc.username}@@"
pc_password = "@@{pc.secret}@@"
vm_uuid = "@@{platform.metadata.uuid}@@"
cluster_uuid = "@@{platform.status.cluster_reference.uuid}@@"
pc_ip = "@@{pc_ip}@@"
# endregion

# region prepare variables
cluster_uuid_url = "https://{}:9440/api/nutanix/v3/clusters/{}".format(
    pc_ip,
    cluster_uuid
)
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
}
# endregion


# region functions
def process_request(url, method, user, password, headers, payload=None):
    if payload is not None:
        payload = json.dumps(payload)
    r = urlreq(
            url,
            verb=method,
            auth="BASIC",
            user=user,
            passwd=password,
            params=payload,
            verify=False,
            headers=headers
        )
    return r
# endregion

print("Mounting NGT...")

# region get the AHV cluster IP address
method = 'GET'
url = cluster_uuid_url
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, pc_user, pc_password, headers)
result = json.loads(resp.content)

if resp.ok:
    # print the content of the response
    print(json.dumps(
        json.loads(resp.content),
        indent=4
    ))
    cluster_ip = result["status"]["resources"]["network"]["external_ip"]
    print("The AHV cluster IP address is {}".format(cluster_ip))
else:
    # print the content of the response (which should have the error message)
    print("Request failed", json.dumps(
        json.loads(resp.content),
        indent=4
    ))
    print("Headers: {}".format(headers))
    exit(1)
# endregion

# region mount the NGT image (to regenerate the certificates)
method = 'POST'
url = "https://{}:9440/PrismGateway/services/rest/v1/vms/{}/guest_tools/mount".format(
    cluster_ip,
    vm_uuid
)
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, pc_user, pc_password, headers)
result = json.loads(resp.content)

if resp.ok:
    # print the content of the response
    print(json.dumps(
        json.loads(resp.content),
        indent=4
    ))
    print("NGT mounted")
    exit(0)
else:
    # print the content of the response (which should have the error message)
    print("Request failed", json.dumps(
        json.loads(resp.content),
        indent=4
    ))
    print("Headers: {}".format(headers))
    exit(1)
# endregion
