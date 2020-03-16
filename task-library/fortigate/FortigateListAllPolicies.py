# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/03032020 - initial version
# task_name:    FortigateListAllPolicies
# description:  List all Fortigate policies
# input vars:   fortigate_csrf_token, fortigate_cookie
# output vars:  fortigate_policy_id, fortigate_policy_name
# endregion

# region capture Calm variables
api_server = "@@{fortigate_endpoint}@@"
fortigate_login = "@@{fortigate_username}@@"
fortigate_password = "@@{fortigate_password}@@"
api_server_port = 80
fortigate_vdom = "@@{fortigate_vdom}@@"
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
    #print("Making a {} API call to {}".format(method, url))
    resp = urlreq(url, verb=method, params=auth_payload,
                headers=headers, verify=False)

    # deal with the result/response
    if resp.ok:
        #print("Successfully authenticated")
        my_cookie = resp.cookies.get_dict()
        return resp.cookies.get('ccsrftoken'), my_cookie
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)
    # endregion

def fortiget_get_policies(api_server, api_server_port, fortigate_csrf_token, fortigate_cookie, vdom="root"):
    
    # region prepare api call
    api_server_endpoint = "/api/v2/cmdb/firewall/policy/?format=policyid|name&skip=1&vdom=" + vdom
    url = "http://{}:{}{}".format(
        api_server,
        api_server_port,
        api_server_endpoint
    )
    method = "GET"
    headers = {
        'Accept': 'application/json'
    }
    # endregion

    # region make api call
    # make the API call and capture the results in the variable called "resp"
    resp = urlreq(url, verb=method, cookies=fortigate_cookie, headers=headers, verify=False)

    # deal with the result/response
    if resp.ok:
        policies_list = []
        #print("Request was successful. Status code: {}".format(resp.status_code))
        result = json.loads(resp.content)
        for policy in result['results']:
            policies_list.append(str(policy['policyid']) + "-" + str(policy['name']))
        print(",".join(policies_list))
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)
    # endregion
    

fortigate_csrf_token, fortigate_cookie = fortiget_get_cookie(api_server,
                                                             api_server_port, fortigate_login, fortigate_password)
fortiget_get_policies(api_server, api_server_port, fortigate_csrf_token,
                      fortigate_cookie, fortigate_vdom)
