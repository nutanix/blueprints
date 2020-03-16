# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/20200219 - initial version
# task_name:    JiraUpdateTicket
# description:  updating the ticket status with the provided payload
# input vars:   transition_id, ticket_name
# output vars:  none
# endregion

# region capture Calm variables
api_server = "@@{jira_endpoint}@@"
jira_login = "@@{jira_login.username}@@"
jira_api_token = "@@{jira_api_token.secret}@@"
transition_id = 31 # 31 = in progress / 41 = Done
ticket_name = "@@{jira_ticket_name}@@" # ticket that need to be updated
# endregion

# region prepare api call
api_server_port = "443"
api_server_endpoint = "/rest/api/3/issue/" + ticket_name + "/transitions"
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
update_payload = {
    "transition": {
    "id": transition_id
  }
    
}
# endregion

# region make api call
# make the API call and capture the results in the variable called "resp"
print("Making a {} API call to {}".format(method, url))
resp = urlreq(url, verb=method, params=json.dumps(update_payload),\
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