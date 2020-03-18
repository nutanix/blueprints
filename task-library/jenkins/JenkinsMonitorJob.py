# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/03032020 - initial version
# task_name:    JenkinsLaunchBuild
# description:  Monitor a jenkins job 
# input vars:   job_build_id
# output vars:  job_status
# endregion

# region capture Calm variables
api_server = "@@{jenkins_endpoint}@@"
jenkins_login = "@@{jenkins.username}@@"
jenkins_api_token = "@@{jenkins.secret}@@"
jenkins_job_name = "@@{jenkins_job_name}@@"
job_build_id = "@@{job_build_id}@@" # job that need to be monitored
# endregion

# region prepare api call
api_server_port = "8080"
api_server_endpoint = "/job/" + jenkins_job_name + "/" + job_build_id + "/api/json"
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "GET"
headers = {
    'Accept': 'application/json'
}
# endregion


job_status = ''
timeout = 300
while job_status != 'SUCCESS':
    
   # region make api call
   # make the API call and capture the results in the variable called "resp"
   print("Making a {} API call to {}".format(method, url))
   resp = urlreq(url, verb=method, auth='BASIC', user=jenkins_login, passwd=jenkins_api_token,
                 headers=headers, verify=False
                 )
   # deal with the result/response
   if resp.ok:
       print("Request was successful. Status code: {}".format(resp.status_code))
       job_status = json.loads(resp.content)['result']
       if job_status == 'SUCCESS':
           print("job ok")
           break
       elif job_status == 'FAILURE':
           print("job failed")
           exit(1)
        
       timeout -= 15
       if timeout == 0:
           print("timeout")
           exit(1)
       else:
           print("still waiting for the job to finish")
           sleep(15)
    
   else:
       print("Request failed")
       print("Headers: {}".format(headers))
       print('Status code: {}'.format(resp.status_code))
       print('Response: {}'.format(json.dumps(resp.content)))
    # endregion
