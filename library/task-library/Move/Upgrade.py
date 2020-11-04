#Input Move details 
MOVE_VM_IP = ""
MOVE_UI_USERNAME = ""
MOVE_UI_PASSWORD = ""

def get_token(MOVE_UI_USERNAME, MOVE_UI_PASSWORD):
    HEADERS = {'Content-type': 'application/json','Accept': 'application/json'}
    PAYLOAD = {"Spec":{"Password": "%s" %(MOVE_UI_PASSWORD),"UserName": "%s" %(MOVE_UI_USERNAME)}}
    response = urlreq('https://%s/move/v2/users/login'%(MOVE_VM_IP), verb='POST', params=json.dumps(PAYLOAD), auth='BASIC', user=MOVE_UI_USERNAME, passwd=MOVE_UI_PASSWORD, headers=HEADERS, verify=False)
    json_response = response.json()
    token = json_response["Status"]["Token"]
    return token

token = get_token(MOVE_UI_USERNAME, MOVE_UI_PASSWORD)

def get_versions():
    HEADERS = {'Content-type': 'application/json','Accept': 'application/json', "Authorization": "%s" %(token)}
    response = urlreq('https://%s/move/v2/checkUpgrade' %(MOVE_VM_IP), verb='GET', headers=HEADERS, verify=False)
    json_response = response.json()
    LatestVersion = json_response["Status"]["LatestVersion"]
    CurrentVersion = json_response["Status"]["CurrentVersion"]
    return LatestVersion, CurrentVersion

def Upgrade_move():
    HEADERS = {'Content-type': 'application/json','Accept': 'application/json', "Authorization": "%s" %(token)}
    LatestVersion, CurrentVersion = get_versions()
    Payload = {"Spec":{"LatestVersion":"%s" %(LatestVersion),"OfflineUpgrade":False,"Version":"%s" %(CurrentVersion),"UploadedFilesInfo":None}}
    response = urlreq('https://%s/move/v2/upgrade'%(MOVE_VM_IP), verb='POST', params=json.dumps(Payload), headers=HEADERS, verify=False)
    return response

upgrade = Upgrade_move()
print(upgrade.content)