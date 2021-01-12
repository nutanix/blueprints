#Input Move details 
MOVE_VM_IP = ""
MOVE_UI_USERNAME = ""
MOVE_UI_PASSWORD = ""

#Input the type of environment, ex: Nutanix, AWS or VMware
ENV = "Nutanix"

#Input Nutanix provider details for Nutanix env type
NUTANIX_ENV_NAME = "NUTANIX_ENV"
NUTANIX_IPorFQDN = ""
NUTANIX_IPorFQDN_USERNAME = ""
NUTANIX_IPorFQDN_PASSWORD = ""

#Input AWS details for AWS env type
AWS_ENV_NAME = "AWS_ENV"
AWS_ACCESSKEY = ""
AWS_SECRETKEY = ""

#Input VMware details for VMware env type
VMWARE_ENV_NAME = "VMWARE_NAME"
VMWARE_IPorFQDN = ""
VMWARE_IPorFQDN_USERNAME = ""
VMWARE_IPorFQDN_PASSWORD = ""
  
def get_token(MOVE_UI_USERNAME, MOVE_UI_PASSWORD):
  HEADERS = {'Content-type': 'application/json','Accept': 'application/json'}
  PAYLOAD = {"Spec":{"Password": "%s" %(MOVE_UI_PASSWORD),"UserName": "%s" %(MOVE_UI_USERNAME)}}
  response = urlreq('https://%s/move/v2/users/login'%(MOVE_VM_IP), verb='POST', params=json.dumps(PAYLOAD), auth='BASIC', user=MOVE_UI_USERNAME, passwd=MOVE_UI_PASSWORD, headers=HEADERS, verify=False)
  json_response = response.json()
  token = json_response["Status"]["Token"]
  return token
   
def create_env(MOVE_UI_USERNAME, MOVE_UI_PASSWORD, PAYLOAD):
  token = get_token(MOVE_UI_USERNAME, MOVE_UI_PASSWORD)
  HEADERS = {'Content-type': 'application/json','Accept': 'application/json', "Authorization": "%s" %(token)}
  res = urlreq('https://%s/move/v2/providers'%(MOVE_VM_IP), verb='POST', params=json.dumps(PAYLOAD), headers=HEADERS, verify=False)
  return res

if ENV == "Nutanix":
  PAYLOAD = {"Spec":{"Name":"%s" %(NUTANIX_ENV_NAME),"AOSAccessInfo":{"IPorFQDN":"%s" %(NUTANIX_IPorFQDN),"Password":"%s" %(NUTANIX_IPorFQDN_PASSWORD),"Username":"%s" %(NUTANIX_IPorFQDN_USERNAME)},"Type":"AOS"}}
  create_nutanix_env = create_env(MOVE_UI_USERNAME, MOVE_UI_PASSWORD, PAYLOAD)
  print(create_nutanix_env.json())
elif ENV == "AWS":
  PAYLOAD = {"Spec":{"Name":"%s" %(AWS_ENV_NAME),"AWSAccessInfo":{"AccessKey":"%s" %(AWS_ACCESSKEY),"SecretKey":"%s" %(AWS_SECRETKEY)},"Type":"AWS"}}
  create_aws_env = create_env(MOVE_UI_USERNAME, MOVE_UI_PASSWORD, PAYLOAD)
  print(create_aws_env.json())
elif ENV == "VMware":
  PAYLOAD = {"Spec":{"Name":"%s" %(VMWARE_ENV_NAME),"ESXAccessInfo":{"IPorFQDN":"%s" %(VMWARE_IPorFQDN),"Password":"%s" %(VMWARE_IPorFQDN_PASSWORD),"Username":"%s" %(VMWARE_IPorFQDN_USERNAME)},"Type":"ESXI"}}
  create_vmware_env = create_env(MOVE_UI_USERNAME, MOVE_UI_PASSWORD, PAYLOAD)
  print(create_vmware_env.json())


