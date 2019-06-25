# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:       igor.zecevic@nutanix.com
# * version:      2019/06/05
# task_name:      CalmGetAppProfileVars
# description:    This script gets all the Application Profiles variable of the
# specified blueprint.
# endregion

# region capture Calm macros
pc_ip = "@@{pc_ip}@@"
username = "@@{pc_user.username}@@"
username_secret = "@@{pc_user.secret}@@"
blueprint_uuid = "@@{blueprint_uuid}@@"
application_profile_name = "@@{application_profile_name}@@"
# endregion

# region prepare variables
headers = {'content-type': 'application/json'}
blueprint_app_profile_uuid = ""
# endregion

# region REST call: Get Blueprint
method = 'GET'
url = "https://{}:9440/api/nutanix/v3/blueprints/{}".format(
    pc_ip,
    blueprint_uuid
)
print("Making a {} API call to {}".format(method, url))
resp = urlreq(
    url,
    verb=method,
    headers=headers,
    auth="BASIC",
    user=username,
    passwd=username_secret,
    verify=False
)

if resp.ok:
    json_resp = json.loads(resp.text)
    blueprint_name = json_resp['status']['name']
    for app_profile in json_resp['spec']['resources']['app_profile_list']:
        if app_profile['name'] == application_profile_name:
            blueprint_app_profile_uuid = app_profile['uuid']
            blueprint_app_profile_variables = app_profile['variable_list']

            print("blueprint_app_profile_uuid= {}".format(blueprint_app_profile_uuid))
            print("blueprint_app_profile_variables= {}".format(json.dumps(blueprint_app_profile_variables)))
            exit(0)
        if blueprint_app_profile_uuid == "":
            print("Could not find application profile with name {} in blueprint {}".format(application_profile_name,blueprint_name))
            exit(1)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
