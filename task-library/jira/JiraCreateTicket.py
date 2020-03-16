# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/20200219 - initial version
# task_name:    JiraCreateTicket
# description:  Jira ticket creation using the deployed vm specs
# input vars:   application_name, jira_project_key
# output vars:  jira_parent_ticket_name
# endregion

# region capture Calm variables
api_server = "@@{jira_endpoint}@@"
jira_login = "@@{jira_login.username}@@"
jira_api_token = "@@{jira_api_token.secret}@@"
jira_project_key = "@@{jira_project_name}@@"
application_name = "@@{calm_application_name}@@"
# endregion

# region prepare api call
api_server_port = "443"
api_server_endpoint = "/rest/api/3/issue"
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
create_payload = {
    "fields": {
    "project": {
      "key": jira_project_key
    },
    "description": {
      "version": 1,
      "type": "doc",
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "Deployment in progress"
            }
          ]
        }
      ]
    },
    "summary": application_name + " vm deployment",
		"labels": [
      "calm"
    ],		
    "issuetype": {
      "name": "Task"
    }
  }
    
}
# endregion

# region make api call
# make the API call and capture the results in the variable called "resp"
print("Making a {} API call to {}".format(method, url))
resp = urlreq(url, verb=method, params=json.dumps(create_payload),\
              auth='BASIC', user=jira_login, passwd=jira_api_token, headers=headers,\
              verify=False
             )

# deal with the result/response
if resp.ok:
    print("Request was successful. Status code: {}".format(resp.status_code))
    result = json.loads(resp.content)
    print("Ticket {} was created".format(result['key']))
    print("jira_parent_ticket_name=", result['key'])
    
    
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion