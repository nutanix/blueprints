 #script
# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    14082019
# task_name:    GetUuid
# description:  this task is used to grab all the required uuid
# endregion

controller_url = "@@{CONTROLLER_URL}@@"
# setting up object names that we would like to get their uuid
cloud_name = "@@{CLOUD_NAME}@@"
network_name = "@@{NETWORK_NAME}@@"
waf_policy = "@@{WAF_POLICY}@@"
application_profile = "@@{APP_PROFILE_NAME}@@"
se_group_name = "@@{SE_GROUP_NAME}@@"
vrf_context = "@@{VRF_CONTEXT}@@"
# list of all urls that you need to get uuid from
# key is calm variable name, item is the url endpoint for the api call, and the last element is the object name
uuid_url = {"CLOUD_UUID":{"/api/cloud?name=":cloud_name}, "NETWORK_UUID":{"/api/network?name=":network_name},\
            "WAF_UUID":{"/api/wafpolicy?name=":waf_policy}, "APP_PROFILE_UUID":{"/api/applicationprofile?name=":application_profile},
			"SE_GROUP_UUID": {"/api/serviceenginegroup?name=": se_group_name},"VRF_UUID":{"/api//vrfcontext?name=":vrf_context}
           }

def get_uuid(controller_url,uuid_url):
    """ This function return the uuid of the object name specified on uuid_url 
        Args:
         controller_url: http://avi_controller_ip
         uuid_url: list of Calm variable, urls and object name that we would like to get
		Returns:
		 print Calm variable name with the corresponding uuid
    
    """

    # setting up header
    h_api_version = "@@{API_VERSION}@@"
    h_encoding = "@@{ENCODING}@@"
    h_content = "@@{CONTENT}@@"
    h_sessionid = "@@{SESSION_ID}@@"
    h_csrftoken = "@@{CSRF_TOKEN}@@"
    

    headers = {
        'cookie': "sessionid=" + h_sessionid +"; csrftoken=" + h_csrftoken,
        'X-Avi-Version': h_api_version,
        'Accept-Encoding': h_encoding,
        'Content-type': h_content
        }
        
    # endregion
	# going through the uuid_url to get the uuid
    for var_name, url in uuid_url.items():
        for endpoint, object_name in url.items():
            endpoint_url = controller_url + endpoint + object_name
            #print("{}={}".format(var_name, object_name))
            print "Enpoint url =", endpoint_url
        response = urlreq(endpoint_url, verb='GET', headers=headers, verify=False)
    
        # deal with the result/response
        if response.ok:
            print "Request was successfully"
            result = json.loads(response.content)
            print "{}={}".format(var_name,result['results'][0]['uuid'])
            
        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(response.status_code))
            print('Response: {}'.format(response.text))
            exit(1)
        
        # endregion
        
if "@@{AVI_INTEGRATION}@@" == "yes":
    get_uuid(controller_url,uuid_url)
