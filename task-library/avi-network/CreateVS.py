#script
# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    14082019
# task_name:    CreateVS
# description:  this task is used to create a virtual service with the specified user params
# endregion

# setting up the header
controller_url = "@@{CONTROLLER_URL}@@"
h_referer = "@@{REFERER}@@"
h_api_version = "@@{API_VERSION}@@"
h_encoding = "@@{ENCODING}@@"
h_content = "@@{CONTENT}@@"
r_csrftoken = "@@{CSRF_TOKEN}@@"
r_sessionid = "@@{SESSION_ID}@@"
vs_port = "@@{VS_PORT}@@"
vs_subnet = "@@{Node1.NODE1_SUBNET}@@"

headers_post = {
    'cookie': "sessionid=" + r_sessionid +"; csrftoken=" + r_csrftoken,
    'X-Avi-Version': h_api_version,
    'Accept-Encoding': h_encoding,
    'Content-type': h_content,
    'X-CSRFToken': r_csrftoken,
    'Referer': h_referer
    }
# endregion    

def create_virtual_service(controller_url, headers_post, vs_name, cloud_uuid,
                           pool_uuid, waf_uuid, app_profile_uuid, network_uuid,
						   se_group_uuid, vrf_uuid, vs_subnet, vs_port):
    """ This function create a virtual service and return it's uuid to be used later 
        Args:
         controller_url: http://avi_controller_ip
         headers_post: header with the sessionid and csrftoken
         vs_name: virtual service name
		 NAME_uuid: all the required uuid to create the virtual service, you can get them using GetUuid task
		 vs_subnet: the subnet that should be used to get an ip for the virtual service
		 vs_port: the port number for the virtual service / application
		Returns:
		 VS_UUID: uuid of the created virtual service
    
    """
    vs_url = controller_url + "/api/virtualservice"
	# payload for the virtual service with auto-allocated ip address
    create_vs_payload = {	
                        'cloud_ref': cloud_uuid,
                        'name': vs_name,
                        'pool_ref': pool_uuid,
                        'se_group_ref': se_group_uuid,
                        'waf_policy_ref': waf_uuid,
                        'application_profile_ref': app_profile_uuid,
                        'vrf_context_ref': vrf_uuid,
                        'services': [
                          {
                            'port': vs_port,
                            'enable_ssl': True
                          }
                        ],

                       'vip': [
                         {
                           'auto_allocate_ip': True,
                           'ipam_network_subnet': 
                               {
                               'network_ref': network_uuid,
                               'subnet': {
                                     'ip_addr': {
                                         'addr': vs_subnet,
                                         'type': "V4"
                                                 },
                                'mask': 24
                                         },
                              }
                         }
                       ]
                     }
    # endregion
	
    response = urlreq(vs_url, verb='POST', params=json.dumps(create_vs_payload), headers=headers_post, verify=False)
    # deal with the result/response
    if response.ok:
        print("Request was successful")
        vs = response.json()
        print('VS_UUID={}'.format(vs['uuid']))        

    else:
        print("Request failed")
        print("Headers: {}".format(headers_post))
        print("Payload: {}".format(create_vs_payload))
        print('Status code: {}'.format(response.status_code))
        print('Response: {}'.format(response.text))
        exit(1)
    
    # endregion

if "@@{AVI_INTEGRATION}@@" == "yes":
    create_virtual_service(controller_url,headers_post,"VS_@@{calm_application_name}@@","@@{CLOUD_UUID}@@","@@{POOL_UUID}@@",\
                           "@@{WAF_UUID}@@","@@{APP_PROFILE_UUID}@@","@@{NETWORK_UUID}@@","@@{SE_GROUP_UUID}@@", "@@{VRF_UUID}@@", vs_subnet,vs_port)
