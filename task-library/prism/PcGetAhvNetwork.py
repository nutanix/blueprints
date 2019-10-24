#region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     MITU Bogdan Nicolae (EEAS-EXT) <Bogdan-Nicolae.MITU@ext.eeas.europa.eu>
# * version:    2019/09/16
# task_name:    PcGetAhvNetwork
# description:  Given multiple ranges of VLAN ids and a target AHV cluster, 
#               determine which one is available (not existing already on the 
#               AHV cluster) which has the lowest id.
# output vars:  project_vlan_id
# endregion

#region capture Calm variables
username = '@@{pc.username}@@'
username_secret = "@@{pc.secret}@@"
api_server = "@@{pc_ip}@@"
nutanix_cluster_uuid = "@@{nutanix_cluster_uuid}@@"
# endregion

#region define variables
#! define here which vlan ranges are valid (the last number is not included)
#! for example, to include vlans 1 to 5, add a range(1,6). Multiple ranges can
#! be specified and need to be comma separated (exp: range(1,6),range(10,16))
vlan_ranges = [
    range(10,110)
]
project_vlan_id = ""
#endregion

#region retrieve existing networks on the AHV cluster

# region prepare api call
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/subnets/list"
length = 100
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "POST"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Compose the json payload
payload = {
    "kind": "subnet", 
    "length":length, 
    "offset":0
}
# endregion

#region make the api call
print("Making a {} API call to {}".format(method, url))
resp = urlreq(
    url,
    verb=method,
    auth='BASIC',
    user=username,
    passwd=username_secret,
    params=json.dumps(payload),
    headers=headers,
    verify=False
)
#endregion

#region process results
if resp.ok:
    print("Request was successful; processing results...")
    #process each valid vlan range
    for valid_vlan_range in vlan_ranges:
        #process each vlan id in this range
        for valid_vlan in valid_vlan_range:
            #process all returned values (ahv networks)
            vlan_match = False
            for ahv_vlans in json.loads(resp.content)['entities']:
                if valid_vlan == int(ahv_vlans['spec']['resources']['vlan_id']):
                    #TODO add code here to check the cluster reference
                    if nutanix_cluster_uuid == ahv_vlans['spec']['cluster_reference']['uuid']:
                        #this vlan is already defined on the AHV cluster
                        vlan_match = True
            if vlan_match is False:
                #we have already found a valid and available vlan, so break out 
                # of the loop
                project_vlan_id = valid_vlan
                break
        if project_vlan_id:
                #we have already found a valid and available vlan, so break out 
                # of the loop
                break
    if project_vlan_id == "":
        #we couldn't find an available vlan id
        print("There is no vlan id available on this cluster.")
        exit(1)
    else:
        #we found an available and valid vlan id
        print("A valid vlan id was found.")
        print("project_vlan_id={}".format(project_vlan_id))
else:
    #api call failed
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
#endregion