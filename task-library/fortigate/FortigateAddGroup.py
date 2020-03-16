# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/03032020 - initial version
# task_name:    FortigateAddGroup
# description:  Create a new fortigate address group and add vm into it
# input vars:   vms, group_name
# output vars:  fortigate_group_name
# endregion

# region capture Calm variables
api_server = "@@{fortigate_endpoint}@@"
fortigate_login = "@@{fortigate.username}@@"
fortigate_password = "@@{fortigate.secret}@@"
api_server_port = 80
vms = "@@{calm_array_name}@@"
group_name = "@@{calm_application_name}@@"
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
        'Accept': 'plain/text'
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
        print(resp.content)
        print(resp.cookies.get('ccsrftoken'))
        my_cookie = resp.cookies.get_dict()
        return resp.cookies.get('ccsrftoken'), my_cookie
        
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)
    # endregion

def fortiget_add_group(api_server, api_server_port, fortigate_csrf_token, fortigate_cookie, vms, group_name, vdom="root"):
    
    # region prepare api call
    api_server_endpoint = "/api/v2/cmdb/firewall/addrgrp?&vdom=" + vdom
    url = "http://{}:{}{}".format(
        api_server,
        api_server_port,
        api_server_endpoint
    )
    method = "POST"
    fortigate_csrf_token = fortigate_csrf_token.replace('"','')
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFTOKEN': fortigate_csrf_token
    }
    # endregion
   
    create_payload = {}
    create_payload['name'] = group_name
    create_payload['member'] = []
    for vm in vms.split(","):
        create_payload['member'].append({'name' : vm})

    print(json.dumps(create_payload))
    # region make api call
    # make the API call and capture the results in the variable called "resp"
    print("Making a {} API call to {}".format(method, url))
    resp = urlreq(url, verb=method, params=json.dumps(create_payload), cookies=fortigate_cookie, headers=headers, verify=False)
    print(resp.content)
    # deal with the result/response
    if resp.ok:
        print("Request was successful. Status code: {}".format(resp.status_code))
        result = json.loads(resp.content)
        print("fortigate_group_name=".format(result['mkey']))
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)
    # endregion
    

fortigate_csrf_token, fortigate_cookie = fortiget_get_cookie(api_server,
                                                             api_server_port, fortigate_login, fortigate_password)

fortiget_add_group(api_server, api_server_port, fortigate_csrf_token,
                   fortigate_cookie, vms, group_name, fortigate_vdom)
