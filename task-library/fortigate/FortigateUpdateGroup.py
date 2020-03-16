# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/03032020 - initial version
# task_name:    FortigateUpdateGroup
# description:  Update fortigate address group with new members
# input vars:   vm_name, vm_ip, group_name, action
# output vars:  revision_changed
# endregion

# region capture Calm variables
api_server = "@@{fortigate_endpoint}@@"
fortigate_login = "@@{fortigate.username}@@"
fortigate_password = "@@{fortigate.secret}@@"
api_server_port = 80
vm_name = "@@{platform.spec.name}@@"
vm_ip = "@@{address}@@"
group_name = "@@{calm_application_name}@@"
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


def fortiget_update_group(api_server, api_server_port, fortigate_csrf_token, fortigate_cookie,
                          vm_name, vm_ip, group_name, action, vdom="root"):
    
    # region prepare api call
    api_server_endpoint = "/api/v2/cmdb/firewall/addrgrp/"+ group_name + "?&vdom=" + vdom
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
    print(resp.content)
    # deal with the result/response
    if resp.ok:
        print("Request was successful. Status code: {}".format(resp.status_code))
        result = json.loads(resp.content)
        group_members = result['results'][0]
        if len(group_members['member']) == 1:
            # region prepare api call to update the group
            method = "DELETE"
            fortigate_csrf_token = fortigate_csrf_token.replace('"', '')
            headers = {
                'Content-Type': 'application/json',
                'X-CSRFTOKEN': fortigate_csrf_token
            }
            # endregion

            # region make api call
            # make the API call and capture the results in the variable called "resp"
            print("Making a {} API call to {}".format(method, url))
            resp = urlreq(url, verb=method, params=json.dumps(group_members),
                        cookies=fortigate_cookie, headers=headers, verify=False)
            print(resp.content)
            # deal with the result/response
            if resp.ok:
                print("Request was successful. Status code: {}".format(resp.status_code))
                result = json.loads(resp.content)
                print("Group {} was deleted".format(group_name))
                print("revision_changed : {}".format(result['revision_changed']))
            else:
                print("Request failed")
                print("Headers: {}".format(headers))
                print('Status code: {}'.format(resp.status_code))
                print('Response: {}'.format(json.dumps(
                    json.loads(resp.content), indent=4)))
                exit(1)
            # endregion
            exit(0)

        if action == "add":
            group_members['member'].append({'name': vm_name})
        else:
            group_members['member'].remove(
                {'name': vm_name, 'q_origin_key': vm_name})

        print(json.dumps(group_members))
    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(
            json.loads(resp.content), indent=4)))
        exit(1)
    # endregion

    # region prepare api call to update the group
    method = "PUT"
    fortigate_csrf_token = fortigate_csrf_token.replace('"', '')
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFTOKEN': fortigate_csrf_token
    }
    # endregion

    # region make api call
    # make the API call and capture the results in the variable called "resp"
    print("Making a {} API call to {}".format(method, url))
    resp = urlreq(url, verb=method, params=json.dumps(group_members),
                  cookies=fortigate_cookie, headers=headers, verify=False)
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
        print('Response: {}'.format(json.dumps(
            json.loads(resp.content), indent=4)))
        exit(1)
    # endregion


fortigate_csrf_token, fortigate_cookie = fortiget_get_cookie(api_server,
                                                             api_server_port, fortigate_login, fortigate_password)

fortiget_update_group(api_server, api_server_port, fortigate_csrf_token,
                      fortigate_cookie, vm_name, vm_ip, group_name, action, fortigate_vdom)
