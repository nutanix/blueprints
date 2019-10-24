# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@nutanix.com
# * version:    20191022
# task_name:    PeMountIso
# description:  Mounts the specified image in the vm.
# output:       task_uuid
# endregion

# region capture Calm variables
username = "@@{pe.username}@@"
username_secret = "@@{pe.secret}@@"
api_server = "@@{pe_ip}@@"
image_vm_disk_id = "@@{image_vm_disk_id}@@"
vm_uuid = "@@{platform.metadata.uuid}@@"
disk_list = @@{platform.spec.resources.disk_list}@@
# endregion

# region variables
for disk in disk_list:
    if disk['device_properties']['device_type'] == "CDROM":
        vm_cdrom_uuid = disk['uuid']
        vm_cdrom_device_index = disk['device_properties']['disk_address']['device_index']
        break
# endregion

# region prepare api call
# Form method, url and headers for the API call
api_server_port = "9440"
api_server_endpoint = "/PrismGateway/services/rest/v2.0/vms/{}/disks/update".format(vm_uuid)
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "PUT"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
# Compose the json payload
payload = {
    "vm_disks": [
        {
            "disk_address": {
                "vmdisk_uuid": vm_cdrom_uuid,
                "device_index": vm_cdrom_device_index,
                "device_bus": "ide"
            },
            "flash_mode_enabled": "false",
            "is_cdrom": "true",
            "is_empty": "false",
            "vm_disk_clone": {
                "disk_address": {
                    "vmdisk_uuid": image_vm_disk_id
                }
            }
        }
    ]
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
    params=json.dumps(payload),
    headers=headers,
    verify=False
)

# deal with the result/response
if resp.ok:
    json_resp = json.loads(resp.content)
    print "task_uuid = {}".format(json_resp['task_uuid'])
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
