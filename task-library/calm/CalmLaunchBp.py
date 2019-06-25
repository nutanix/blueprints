# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:       igor.zecevic@nutanix.com, stephane.bourdeaud@nutanix.com
# * version:      2019/06/06
# task_name:      CalmLaunchBp
# description:    This script launches the specified Calm blueprint with the
# specified application profile. You will need to edit the variable_list section
# of the json payload in the "REST call: Launch Blueprint" region with
# your list of variables in your application profile and also edit the region
# "customize application profile variables" to define values and uuids for your
# variables.
# endregion

# region capture Calm macros
pc_ip = '@@{pc_ip}@@'
username = '@@{pc_user.username}@@'
username_secret = '@@{pc_user.secret}@@'
blueprint_uuid = "@@{blueprint_uuid}@@"
blueprint_app_name = "@@{blueprint_app_name}@@"
blueprint_app_profile_uuid = '@@{blueprint_app_profile_uuid}@@'
variables_json = '@@{variables_json}@@'
# endregion

# region prepare variables
headers = {'content-type': 'application/json'}
# endregion

# region customize application profile variables
# TODO customize this section to match your bleuprint variables
# TODO then customize also the payload below
dns1 = "10.10.10.10"
for variable in json.loads(variables_json):
    if variable['name'] == "dns1":
        dns1_uuid = variable['uuid']
# endregion

# region REST call: Launch Blueprint
method = 'POST'
url = "https://{}:9440/api/nutanix/v3/blueprints/{}/launch".format(
    pc_ip,
    blueprint_uuid
)
print("Making a {} API call to {}".format(method, url))
payload = {
    "api_version": "3.0",
    "metadata": {
        "uuid": ""+blueprint_uuid+"",
        "kind": "blueprint"
    },
    "spec": {
        "application_name": ""+blueprint_app_name+"",
        "app_profile_reference": {
            "kind": "app_profile",
            "uuid": ""+blueprint_app_profile_uuid+""
        },
        "resources": {
            "app_profile_list": [
                {
                    "name": "Default",
                    "uuid": ""+blueprint_app_profile_uuid+"",
                    "variable_list": [
                        {
                            "name": "dns1",
                            "value": dns1,
                            "uuid": dns1_uuid
                        }
                    ]
                }
            ]
        }
    }
}
resp = urlreq(
    url,
    verb=method,
    params=json.dumps(payload),
    headers=headers,
    auth="BASIC",
    user=username,
    passwd=username_secret,
    verify=False
)

if resp.ok:
    json_resp = json.loads(resp.content)
    print("Blueprint {} was launched successfully as application instance {}".format(blueprint_uuid,blueprint_app_name))
    print("launch_request_id= {}".format(json_resp['status']['request_id']))
    exit(0)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)

# endregion
