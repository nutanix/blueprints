# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/20200219 - initial version
# task_name:    JiraUpdateTicket
# description:  Link a ticket to it's parent
# input vars:   jira_link_type
# output vars:  none
# endregion

# region capture Calm variables
api_server = "@@{jira_endpoint}@@"
jira_login = "@@{jira_login.username}@@"
jira_api_token = "@@{jira_api_token.secret}@@"
jira_link_type = "@@{jira_link_type}@@" #10003 = relates to
jira_parent_ticket = "@@{jira_parent_ticket}@@"
jira_child_ticket = "@@{jira_child_ticket}@@"
# endregion

# region prepare api call
api_server_port = "443"
api_server_endpoint = "/rest/api/3/issueLink"
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
link_payload = {
    "type": {
        "id": jira_link_type
    },
    "inwardIssue": {
        "key": jira_parent_ticket
    },
    "outwardIssue": {
        "key": jira_child_ticket
    }
}
# endregion

# region make api call
# make the API call and capture the results in the variable called "resp"
print("Making a {} API call to {}".format(method, url))
resp = urlreq(url, verb=method, params=json.dumps(link_payload),\
              auth='BASIC', user=jira_login, passwd=jira_api_token, headers=headers,\
              verify=False
             )

# deal with the result/response
if resp.ok:
    print("Request was successful. Status code: {}".format(resp.status_code))    
    
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
