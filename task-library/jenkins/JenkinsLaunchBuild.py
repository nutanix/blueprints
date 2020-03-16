# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    v1.0/03032020 - initial version
# task_name:    JenkinsLaunchBuild
# description:  Launching a Parametrized jenkins build 
# input vars:   jenkins_job_name, jenkins_job_params
# output vars:  job_build_id
# endregion

# region capture Calm variables
api_server = "@@{jenkins_endpoint}@@"
jenkins_login = "@@{jenkins.username}@@"
jenkins_api_token = "@@{jenkins.secret}@@"
jenkins_job_name = "@@{jenkins_job_name}@@" # job that need to be executed
jenkins_job_params = "machine_ips=@@{address}@@" # job parameters that need to be executed
# endregion

# region prepare api call
api_server_port = "8080"
api_server_endpoint = "/job/" + jenkins_job_name + "/buildWithParameters?" + jenkins_job_params
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "POST"
headers = {
    'Accept': 'application/json'
}
# endregion

# region make api call
# make the API call and capture the results in the variable called "resp"
print("Making a {} API call to {}".format(method, url))
resp = urlreq(url, verb=method, auth='BASIC', user=jenkins_login, passwd=jenkins_api_token,\
              headers=headers, verify=False
             )

# deal with the result/response
if resp.ok:
    print("Request was successful. Status code: {}".format(resp.status_code))
    job_build_id = resp.headers['Location'].split("/")[-2]
    print("Job {} was successfully launched".format(job_build_id))
    print("job_build_id=",job_build_id)    
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion