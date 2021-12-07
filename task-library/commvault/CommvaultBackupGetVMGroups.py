#region capture Calm variables
USERNAME = "@@{USERNAME}@@"
PASSWORD = "@@{PASSWORD}@@"
SERVER_IP = "@@{SERVER_IP}@@"
CLIENT_NAME = "@@{CLIENT_NAME}@@"
TIMEOUT = 30 # In minutes
#endregion

### DO NOT CHANGE AFTER THIS

# region prepare api call
API_URL = "https://{}/webconsole/api".format(SERVER_IP)

SEPARATOR = "/"

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Compose the json payload
PAYLOAD = {
  "password": PASSWORD,
  "username": USERNAME,
  "timeout" : TIMEOUT
}
# endregion

#region make the api call
METHOD = "POST"
OPERATION = "Login"
URL = SEPARATOR.join([API_URL,OPERATION])

resp = urlreq(
    URL,
    verb=METHOD,
    params=json.dumps(PAYLOAD),
    headers=HEADERS,
    verify=False
)
#endregion

#region process the results
if resp.ok:
    json_resp = json.loads(resp.content)
    HEADERS["Authtoken"] = json_resp["token"]
else:
    exit(1)
# endregion

#region make the api call
METHOD = "GET"
OPERATION = "v2/vsa/vmgroups?clientName={}".format(CLIENT_NAME)
URL = SEPARATOR.join([API_URL,OPERATION])

resp = urlreq(
    URL,
    verb=METHOD,
    headers=HEADERS,
    verify=False
)
#endregion

#region process the results
if resp.ok:
    json_resp = json.loads(resp.content)
    vm_groups = json_resp["vmGroupInfo"]
else:
    exit(1)
# endregion

vm_groups_list = []

for group in vm_groups:
    if group["vmGroupEntity"]["subclientName"] != "default":
        group_details = group["vmGroupEntity"]
        id = group_details["subclientId"]
        name = group_details["subclientName"]
        group_tuple = ("{} (id={})".format(name,id))
        vm_groups_list.append(group_tuple)

print(",".join(map(str,vm_groups_list)))