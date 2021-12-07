# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:     jose.gomez@nutanix.com
# * version:    20211207
# task_type:    Execute
# task_name:    Commvault_Run_Subclient_Backup
# description:  Runs a backup job for the Commvault VM Group selected during launch
# endregion

#region capture Calm variables
USERNAME = "@@{CRED_CV.username}@@"
PASSWORD = "@@{CRED_CV.secret}@@"
SERVER_IP = "@@{SERVER_IP}@@"
TIMEOUT = 30 # In minutes

VSUBCLIENT = "@@{CV_VM_GROUP}@@" # profile variable (expands with user's choice)
#endregion

### DO NOT CHANGE AFTER THIS

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
METHOD = "POST"
OPERATION = "Subclient/{}/action/backup".format(VSUBCLIENT_ID)
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
    job_id = json_resp["jobIds"][0]
    print("Initial backup in process. Follow the progress https://{}/adminconsole/#/jobs/{}".format(SERVER_IP,job_id))
    exit(0)
else:
    # print the content of the response (which should have the error message)
    print("Request failed", json.dumps(
        json.loads(resp.content),
        indent=4
    ))
    print("Headers: {}".format(HEADERS))
    exit(1)
# endregion