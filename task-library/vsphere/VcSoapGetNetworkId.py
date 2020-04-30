# region headers
# * author:     igor.zecevic@nutanix.com
# * version:    v1.0 - initial version
# * date:       30/03/2020
# task_name:    VcSoapGetNetworkId
# description:  Get vSphere network MOID (Managed Object ID) using the SearchIndex method
# input vars:   datacenter, vc_network_name,
# output vars:  vc_network_id
# endregion

# region capture Calm variables
username = "@@{vc.username}@@"
password = "@@{vc.secret}@@"
api_server = "@@{vc_endpoint}@@"
datacenter = "@@{vc_datacenter}@@"
vc_network_name = "@@{vc_network_name}@@"
# endregion

# region API call function
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
# endregion

# region login
# region prepare login API call
ET = xml.etree.ElementTree
api_server_port = "443"
api_server_endpoint = "/sdk/vimService.wsdl"
method = "POST"
url = "https://{}:{}{}".format(api_server, api_server_port, api_server_endpoint)
headers = {'Content-Type': 'application/xml', 'Accept': 'application/xml'}
# endregion

# region login API call
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
vc_cookie = resp.headers.get('Set-Cookie').replace('"','').split(";")[0]
# endregion
# endregion

# region main processing
# region get vsphere network names
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

# push cluster name into the payload
payload_parse = ET.fromstring(base_payload)
payload_find = payload_parse.find(".//{urn:vim25}FindByInventoryPath")
payload_push = ET.SubElement(payload_find,"inventoryPath")
payload_push.text = "/{0}/network/{1}".format(datacenter, vc_network_name)
payload = ET.tostring(payload_parse)

# making the call
print("STEP: Getting vSphere Networks...")
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)

# get network_id
vc_network_id = ""
resp_parse = ET.fromstring(resp.text)
resp_find = resp_parse.findall(".//{urn:vim25}returnval")
for element in resp_find:
    print("vc_network_id={}".format(element.text))

if not vc_network_id:
   print ("Error: vSphere Portgroup "+vc_network_name+" is not present")
   exit(1)
# endregion

# region logout API call
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
# endregion
# endregion
exit(0)