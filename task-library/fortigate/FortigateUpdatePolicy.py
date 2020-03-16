# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/03032020 - initial version
# task_name:    FortigateUpdatePolicy
# description:  Update a policy with the specified group as a destination
# input vars:   group_name, policy_id
# output vars:  revision_changed
# endregion

# region capture Calm variables
api_server = "@@{fortigate_endpoint}@@"
fortigate_login = "@@{fortigate.username}@@"
fortigate_password = "@@{fortigate.secret}@@"
api_server_port = 80
policy_id = "@@{fortigate_policy}@@".split("-")[0]
group_name = "@@{calm_application_name}@@" # address group name
fortigate_vdom = "@@{fortigate_vdom}@@"
action = "add"
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
    

def fortiget_update_policy(api_server, api_server_port, fortigate_csrf_token, fortigate_cookie,
                          group_name, action, vdom="root"):
    
    # region prepare api call
    api_server_endpoint = "/api/v2/cmdb/firewall/policy/" + str(policy_id) + "?skip=1&vdom=" + vdom
    url = "http://{}:{}{}".format(
        api_server,
        api_server_port,
        api_server_endpoint
    )
    method = "GET"
    headers = {
        'Content-Type': 'application/json',
    }
    # endregion
    
    # region make api call to get the group members
    # make the API call and capture the results in the variable called "resp"
    print("Making a {} API call to {}".format(method, url))
    resp = urlreq(url, verb=method, cookies=fortigate_cookie, headers=headers, verify=False)
    # deal with the result/response
    if resp.ok:
        print("Request was successful. Status code: {}".format(resp.status_code))
        result = json.loads(resp.content)
        policy_members = result['results'][0]
        if action == "add":
            policy_members['dstaddr'].append({'name' : group_name})
        else:
            policy_members['dstaddr'].remove({'name': group_name, 'q_origin_key': group_name})
            
        print(json.dumps(policy_members))
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)
    # endregion


    # region prepare api call to update the group
    method = "PUT"
    fortigate_csrf_token = fortigate_csrf_token.replace('"','')
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFTOKEN': fortigate_csrf_token
    }
    # endregion

    # region make api call
    # make the API call and capture the results in the variable called "resp"
    print("Making a {} API call to {}".format(method, url))
    resp = urlreq(url, verb=method, params=json.dumps(policy_members), cookies=fortigate_cookie, headers=headers, verify=False)
    print(resp.content)
    # deal with the result/response
    if resp.ok:
        print("Request was successful. Status code: {}".format(resp.status_code))
        result = json.loads(resp.content)
        print("revision_changed : {}".format(result['revision_changed']))
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)
    # endregion
    

fortigate_csrf_token, fortigate_cookie = fortiget_get_cookie(api_server,
                                                             api_server_port, fortigate_login, fortigate_password)
fortiget_update_policy(api_server, api_server_port, fortigate_csrf_token,
                      fortigate_cookie, group_name, action, fortigate_vdom)
