# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:     jose.gomez@nutanix.com
# * version:    20211207
# task_type:    Execute
# task_name:    Commvault_Add_VM_to_Group
# description:  Add VM to Commvault VM Group
# endregion

#region capture Calm variables
USERNAME = "@@{CRED_CV.username}@@"
PASSWORD = "@@{CRED_CV.secret}@@"
SERVER_IP = "@@{SERVER_IP}@@"
TIMEOUT = 30 # In minutes

VSUBCLIENT = "@@{CV_VM_GROUP}@@" # profile variable (expands with user's choice)
#endregion

### DO NOT CHANGE AFTER THIS

VSUBCLIENT_NAME = VSUBCLIENT.split(' (')[0]
VSUBCLIENT_ID = int(VSUBCLIENT.split('=')[1][:-1])

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
    # print the content of the response (which should have the error message)
    print("Request failed", json.dumps(
        json.loads(resp.content),
        indent=4
    ))
    print("Headers: {}".format(HEADERS))
    print("Payload: {}".format(PAYLOAD))
    exit(1)
# endregion

#region make the api call
METHOD = "GET"
OPERATION = "v2/vsa/vmgroups/{}".format(VSUBCLIENT_ID)
URL = SEPARATOR.join([API_URL,OPERATION])

# print("Making a {} API call to {}".format(METHOD, URL))
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
    vmGroupEntity = json_resp["vmGroupInfo"][0]["vmGroupEntity"]
    content = json_resp["vmGroupInfo"][0]["content"]
else:
    # print the content of the response (which should have the error message)
    print("Request failed", json.dumps(
        json.loads(resp.content),
        indent=4
    ))
    print("Headers: {}".format(HEADERS))
    exit(1)
# endregion

#region make the api call
METHOD = "PUT"
OPERATION = "Subclient/{}/content".format(VSUBCLIENT_ID)
URL = SEPARATOR.join([API_URL,OPERATION])

add_vm = {
    "equalsOrNotEquals": True,
    "guestCredentialAssocId": 0,
    "displayName": "@@{name}@@",
    "allOrAnyChildren": True,
    "type": 9,
    "path": "",
    "name": "@@{id}@@"
}

content["children"].append(add_vm)

# print("Making a {} API call to {}".format(METHOD, URL))
resp = urlreq(
    URL,
    verb=METHOD,
    params=json.dumps(content),
    headers=HEADERS,
    verify=False
)
#endregion

#region process the results
if resp.ok:
    print("Virtual Machine @@{name}@@ with id @@{id}@@ added to backup group {}.".format(VSUBCLIENT_NAME))
else:
    # print the content of the response (which should have the error message)
    print("Request failed", json.dumps(
        json.loads(resp.content),
        indent=4
    ))
    print("Headers: {}".format(HEADERS))
    print("Payload: {}".format(content))
    exit(1)
# endregion

#region make the api call
METHOD = "POST"
OPERATION = "Subclient/Content/Preview"
URL = SEPARATOR.join([API_URL,OPERATION])

PAYLOAD = {
    "appId": {
        "subclientId": VSUBCLIENT_ID,
        "clientId": vmGroupEntity["clientId"],
        "instanceId": vmGroupEntity["instanceId"],
        "backupsetId": vmGroupEntity["backupsetId"],
        "apptypeId": vmGroupEntity["applicationId"]
    }
}


# print("Making a {} API call to {}".format(METHOD, URL))
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
    exit(0)
else:
    # print the content of the response (which should have the error message)
    print("Request failed", json.dumps(
        json.loads(resp.content),
        indent=4
    ))
    print("Headers: {}".format(HEADERS))
    print("Payload: {}".format(PAYLOAD))
    exit(1)
# endregion