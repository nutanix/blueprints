# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     andy.schmid@nutanix.com, stephane.bourdeaud@nutanix.com
# * version:    2019/06/12, v1
# task_name:    InfobloxCheckHostname
# description:  Given a hostname, this script will loop looking up the
#               hostname plus a 3 digit numerical increment until an
#               unregistered hostname is found.  It is meant to be used to
#               identify unique hostnames for VMs in a blueprint.
# endregion

# region capture Calm variables
# * Capture variables here. This makes sure Calm macros are not referenced
# * anywhere else in order to improve maintainability.
username = '@@{infoblox.username}@@'
username_secret = "@@{infoblox.secret}@@"
api_server = "@@{infoblox_ip}@@"
# * the variable below can be used to determine how the vm hostname will begin
vm_hostname_prefix = "@@{vm_hostname_prefix}@@"
# endregion

# region prepare variables
api_server_port = "443"
# ! You may have to change the endpoint based on your Infoblox version
api_server_endpoint = "/wapi/v2.7.1/"
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
# * variable id will be used to increment and make the vm hostname unique
id = 1
# * variable unique_id is used to transform the integer stored in id in a 3 digit string
unique_id = "%03d" % id
vm_hostname = "{}{}".format(vm_hostname_prefix, unique_id)
# endregion

# region login Infoblox
method = "GET"
print("Making a {} API call to {}".format(method, url))
resp = urlreq(
    create_rm_url,
    verb=method,
    headers=headers,
    verify=False,
    auth="BASIC",
    user=username,
    passwd=username_secret
)

# deal with the result/response
if resp.ok:
    print("Login request was successful")
    # let's store the session cookies for future use
    cookie_jar = resp.cookies
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion

# region loop on Infoblox get host until we find a name that is unique
while True:
    print("Checking if {} already exists in Infoblox...".format(vm_hostname))
    new_url = "{}record:host?name~={}".format(url, vm_hostname)
    method = "GET"
    print("Making a {} API call to {}".format(method, new_url))
    resp = urlreq(
        new_url,
        verb=method,
        headers=headers,
        verify=False,
        cookies=cookie_jar
    )

    if resp.ok:
        print("Lookup request was successful")
        json_resp = json.loads(resp.content)
        if json_resp == []:
            print("{} is not already registered in Infoblox.".format(vm_hostname))
            break
        print("{} already exists in Infoblox!".format(vm_hostname))
        # * increment the id by 1 in order to test the next hostname
        id = id + 1
        unique_id = "%03d" % id
        vm_hostname = "{}{}".format(vm_hostname_prefix, unique_id)
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print("Payload: {}".format(json.dumps(payload)))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)
# endregion

# pass the unique hostname in vm_hostname so that it may be captured by Calm.
print("vm_hostname={}".format(vm_hostname))

exit(0)
