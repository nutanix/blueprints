#script
# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    14082019
# task_name:    Authentication
# description:  this task is used to authenticate again the Avi controller
# endregion
controller_url = "@@{CONTROLLER_URL}@@"
avi_username = "@@{avi.username}@@"
avi_password = "@@{avi.secret}@@"


def avi_login(controller_url,avi_username,avi_password):
    """ This function return two elements, the csrftoken and sessionid to be used later 
        Args:
         controller_url: http://avi_controller_ip
         login: avi controller username
         password: avi controller password
		Returns:
		 CSRF_TOKEN: to be used with other api call
		 SESSION_ID: to be used with other api call
    
    """
    
    login_url = controller_url + "/login"
    h_referer = "@@{REFERER}@@"
    h_api_version = "@@{API_VERSION}@@"
	
    # setting up the headers and payload for the request
    login_payload = "-----CALM\r\n" \
        "Content-Disposition: form-data; name=\"username\"\r\n\r\n" + avi_username +"\r\n" \
        "-----CALM\r\n" \
        "Content-Disposition: form-data; name=\"password\"\r\n\r\n" + avi_password +"\r\n" \
        "-----CALM--\r\n"
    headers = {
        'content-type': "multipart/form-data; boundary=---CALM",
        'X-Avi-Version': h_api_version,
        'Referer': h_referer
        }
    # endregion
	
    response = urlreq(login_url, verb='POST', params=login_payload, headers=headers, verify=False)
    
    # deal with the result/response
    if response.ok:
        print "Successfully authenticated"
        print "CSRF_TOKEN={}".format(response.cookies.get('csrftoken'))
        print "SESSION_ID={}".format(response.cookies.get('sessionid'))       
        
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print("Payload: {}".format(login_payload))
        print('Status code: {}'.format(response.status_code))
        print('Response: {}'.format(response.text))
        exit(1)
    
    # endregion
avi_login(controller_url,avi_username,avi_password)

    
