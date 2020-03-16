#region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       10/03/2020
# task_name:    VcSoapGetObjects
# description:  Get list of MOID (Managed Object ID) using the SearchIndex Method
# input vars:   vc_cookie, api_server, datacenter, cluster, vm_name
# output vars:  vc_vm_folder_root_id, vc_cluster_id, vc_vm_id
#endregion

#region capture Calm variables
username = "@@{vc.username}@@"
password = "@@{vc.secret}@@"
api_server = "@@{vc_endpoint}@@"
datacenter = "@@{vc_datacenter}@@"
cluster = "@@{vc_cluster}@@"
vm_name = "@@{name}@@" #calm macro for the vm's name
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
#region prepare search index api call
ET = xml.etree.ElementTree
api_server_port = "443"
api_server_endpoint = "/sdk/vimService.wsdl"
method = "POST"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/xml', 'Accept': 'application/xml', 'Cookie': vc_cookie}
base_payload = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:vim25">
  <soapenv:Body>
    <FindByInventoryPath>
      <_this type="SearchIndex">SearchIndex</_this>
    </FindByInventoryPath>
  </soapenv:Body>
</soapenv:Envelope>'''
#endregion

#region get the vm root folder id (/datacenter_name/vm)
payload_parse = ET.fromstring(base_payload)
payload_find = payload_parse.find(".//{urn:vim25}FindByInventoryPath")
payload_push = ET.SubElement(payload_find,"inventoryPath")
payload_push.text = "/{0}/vm/".format(datacenter)
payload = ET.tostring(payload_parse)

# making the call
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)

# get vm_folder_root_id
resp_parse = ET.fromstring(resp.text)
resp_find = resp_parse.findall(".//{urn:vim25}returnval")
if resp_find:
  for element in resp_find:
      print("vc_vm_folder_root_id={}".format(element.text))
else:
  print("Error, couldn't retreive the object..")
  print("The object: "+datacenter+" doesn't seem to be present, check the provided input")
  exit(1) 
#endregion

#region get the cluster id (/datacenter_name/host/cluster_name)
payload_parse = ET.fromstring(base_payload)
payload_find = payload_parse.find(".//{urn:vim25}FindByInventoryPath")
payload_push = ET.SubElement(payload_find,"inventoryPath")
payload_push.text = "/{0}/host/{1}".format(datacenter, cluster)
payload = ET.tostring(payload_parse)

# making the call
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)

# get the cluster_id
resp_parse = ET.fromstring(resp.text)
resp_find = resp_parse.findall(".//{urn:vim25}returnval")
if resp_find:
  for element in resp_find:
      print("vc_cluster_id={}".format(element.text))
else:
  print("Error, couldn't retreive the object..")
  print("The object: "+cluster+" doesn't seem to be present, check the provided input")
  exit(1) 
#endregion

#region get the vm id (/datacenter_name/host/vm_name)
payload_parse = ET.fromstring(base_payload)
payload_find = payload_parse.find(".//{urn:vim25}FindByInventoryPath")
payload_push = ET.SubElement(payload_find,"inventoryPath")
payload_push.text = "/{0}/vm/{1}".format(datacenter, vm_name)
payload = ET.tostring(payload_parse)

# making the call
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)

# get vm id
resp_parse = ET.fromstring(resp.text)
resp_find = resp_parse.findall(".//{urn:vim25}returnval")
if resp_find:
  for element in resp_find:
      print("vc_vm_id={}".format(element.text))
else:
  print("Error, couldn't retreive the object..")
  print("The object: "+vm_name+" doesn't seem to be present, check the provided input")
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
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)
#endregion
#endregion

exit(0)
