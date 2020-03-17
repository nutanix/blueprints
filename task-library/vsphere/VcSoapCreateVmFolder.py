#region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       10/03/2020
# task_name:    VcSoapCreateVmFolder
# description:  Create a vCenter vm folder based on the calm application name
#               ie: creates the folder at the vm root level (/datacenter/vm/)
# input vars:   vc_cookie, vm_folder_root_id, vm_folder_name, api_server
# output vars:  vc_vm_folder_id
#endregion

#region dealing with Scaling In/Out the application
# # this script will be executed only on the first Service/Instance
# (ie: Service[0])
if "@@{calm_array_index}@@" != "0":
    print("This task is not required on this Instance ..")
    print("Skipping this task ..")
    exit(0)
#endregion

#region capture Calm variables
username = "@@{vc.username}@@"
password = "@@{vc.secret}@@"
vm_folder_root_id = "@@{vc_vm_folder_root_id}@@" # retreived from VcSoapGetObjects
vm_folder_name = "@@{calm_application_name}@@"
api_server = "@@{vc_endpoint}@@"
datacenter = "@@{vc_datacenter}@@"
#endregion

#region API call function
def process_request(url, method, headers, payload):
    r = urlreq(url, verb=method, params=payload, verify=False, headers=headers)
    if r.ok:
        print("Request was successful")
        print("Status Code: {}".format(r))
    else:
        print("Request failed")
        print("Status Code: {}".format(r))
        #print("Headers: {}".format(headers))
        #print("Payload: {}".format(payload))
        #print("Response: {}".format(r.text))
        resp_parse = ET.fromstring(r.text)
        for element in resp_parse.iter('*'):
          if "faultstring" in element.tag:
            print("Error: {}".format(element.text))
            break
    return r
#endregion

#region login
#region prepare login API call
ET = xml.etree.ElementTree
api_server_port = "443"
api_server_endpoint = "/sdk/vimService.wsdl"
method = "POST"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/xml', 'Accept': 'application/xml'}
#endregion

#region login API call
payload = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:vim25">
   <soapenv:Body>
      <Login>
         <_this type="SessionManager">SessionManager</_this>
         <userName>'''+username+'''</userName>
         <password>'''+password+'''</password>
      </Login>
   </soapenv:Body>
</soapenv:Envelope>'''

# making the api call
print("STEP: Logging in to vCenter...")
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)

# pass the cookie in vc_soap_session so that it may be captured by Calm.
vc_cookie = resp.headers.get('Set-Cookie').replace('"','').split(";")[0]
#endregion
#endregion

#region main processing
#region prepare api call
ET = xml.etree.ElementTree
api_server_port = "443"
api_server_endpoint = "/sdk/vimService.wsdl"
method = "POST"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/xml', 'Accept': 'application/xml', 'Cookie': vc_cookie}
#endregion


#region create vm folder
payload = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:vim25">  
<soapenv:Body>
    <CreateFolder>
      <_this type="Folder">'''+vm_folder_root_id+'''</_this>
      <name>'''+vm_folder_name+'''</name>
    </CreateFolder>
  </soapenv:Body>
</soapenv:Envelope>'''

# making the call
print("STEP: Creating the folder...")
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)
base_payload = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:vim25">
  <soapenv:Body>
    <FindByInventoryPath>
      <_this type="SearchIndex">SearchIndex</_this>
    </FindByInventoryPath>
  </soapenv:Body>
</soapenv:Envelope>'''
if resp.ok:
  # print the vm_folder_id
  resp_parse = ET.fromstring(resp.text)
  for element in resp_parse.iter('*'):
      if "returnval" in element.tag:
          print("vc_vm_folder_id: {}".format(element.text))
elif resp.status_code == 500:
  resp_parse = ET.fromstring(resp.text)
  #//debug: print("resp_parse:{}".format(resp_parse))
  for element in resp_parse.iter('*'):
    #//debug: print("element.text:{}".format(element.text))
    if "faultstring" in element.tag:
      if "already exists" in element.text:
        #fetch the existing folder id
        payload_parse = ET.fromstring(base_payload)
        payload_find = payload_parse.find(".//{urn:vim25}FindByInventoryPath")
        payload_push = ET.SubElement(payload_find,"inventoryPath")
        payload_push.text = "/{0}/vm/{1}".format(datacenter,vm_folder_name)
        payload = ET.tostring(payload_parse)

        # making the call
        print("STEP: Fetching folder object id...")
        print("Making a {} API call to {}".format(method, url))
        resp = process_request(url, method, headers, payload)

        # get vm_folder_root_id
        resp_parse = ET.fromstring(resp.text)
        resp_find = resp_parse.findall(".//{urn:vim25}returnval")
        if resp_find:
          for element in resp_find:
              print("vc_vm_folder_id={}".format(element.text))
              exit(0)
        else:
          print("Error, couldn't retrieve the folder object..")
          exit(1)
else:
  exit(1)
#endregion

#endregion

#region logout
#region prepare api call
ET = xml.etree.ElementTree
api_server_port = "443"
api_server_endpoint = "/sdk/vimService.wsdl"
method = "POST"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/xml', 'Accept': 'application/xml', 'Cookie': vc_cookie}
#endregion

#region logout API call
payload = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:vim25">
   <soapenv:Body>
      <Logout>
         <_this type="SessionManager">SessionManager</_this>
      </Logout>
   </soapenv:Body>
</soapenv:Envelope>'''

# making the api call
print("STEP: Logging out of vCenter...")
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)
#endregion
#endregion

exit(0)
