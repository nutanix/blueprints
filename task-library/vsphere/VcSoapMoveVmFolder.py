#region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       10/03/2020
# task_name:    VcSoapMoveVmFolder
# description:  Move a VM in a folder
# input vars:   vc_cookie, api_server, vm_folder_id, vm_id
# output vars:  none
#endregion

#region capture Calm variables
username = "@@{vc.username}@@"
password = "@@{vc.secret}@@"
vm_folder_id = "@@{vc_vm_folder_id}@@" #retreived from VcSoapCreateVmFolder
api_server = "@@{vc_endpoint}@@"
vm_id = "@@{vc_vm_id}@@" #retreived from VcSoapGetObjects
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
        print("Headers: {}".format(headers))
        print("Payload: {}".format(payload))
        print("Response: {}".format(r.text))
        resp_parse = ET.fromstring(r.text)
        for element in resp_parse.iter('*'):
          if "faultstring" in element.tag:
            print("")
            print("Error: {}".format(element.text))
            break
        exit(1)
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

#region move vm to folder
payload = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:vim25">
    <soapenv:Body>
        <MoveIntoFolder_Task>
            <_this type="Folder">'''+vm_folder_id+'''</_this>
        </MoveIntoFolder_Task>
    </soapenv:Body>
</soapenv:Envelope>'''

# add vm to the payload
payload_parse = ET.fromstring(payload)
payload_find = payload_parse.find(".//{urn:vim25}MoveIntoFolder_Task")
payload_push = ET.SubElement(payload_find,"list")
payload_push.attrib["type"] = "VirtualMachine"
payload_push.text = vm_id
payload = ET.tostring(payload_parse)

# making the call
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)
#endregion

# print the task id
resp_parse = ET.fromstring(resp.text)
for element in resp_parse.iter('*'):
    if "returnval" in element.tag:
        print("Task is: {}".format(element.text))
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
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)
#endregion
#endregion

exit(0)
