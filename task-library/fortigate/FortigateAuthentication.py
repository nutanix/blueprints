# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/03032020 - initial version
# task_name:    FortigateAuthentication
# description:  Get a cookie and ccsrf token
# input vars:   fortigate credentials
# output vars:  fortigate_cookie, fortigate_csrf_token
# endregion

# region capture Calm variables
api_server = "@@{fortigate_endpoint}@@"
fortigate_login = "@@{fortigate.username}@@"
fortigate_password = "@@{fortigate.secret}@@"
api_server_port = 80
# endregion


def fortiget_get_cookie(api_server, api_server_port, fortigate_login, fortigate_password):
    
    # region prepare api call
    api_server_endpoint = "/logincheck"
    url = "http://{}:{}{}".format(
        api_server,
        api_server_port,
        api_server_endpoint
    )
    method = "POST"
    headers = {
        'Accept': 'text/plain'
    }
    auth_payload = "username=" + fortigate_login + "&secretkey=" + fortigate_password
    # endregion

    # region make api call
    # make the API call and capture the results in the variable called "resp"
    print("Making a {} API call to {}".format(method, url))
    resp = urlreq(url, verb=method, params=auth_payload,
                headers=headers, verify=False)

    # deal with the result/response
    if resp.ok:
        print("Successfully authenticated")
        my_cookie = resp.cookies.get_dict()
        return resp.cookies.get('ccsrftoken'), my_cookie
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)
    # endregion
        

fortigate_csrf_token , fortigate_cookie = fortiget_get_cookie(api_server, api_server_port,fortigate_login,fortigate_password)
print "fortigate_csrf_token={}".format(fortigate_csrf_token)
print "fortigate_cookie={}".format(fortigate_cookie)