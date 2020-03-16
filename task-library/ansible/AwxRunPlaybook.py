# region headers
# escript-template v20190605 / stephane.bourdeaud@nutanix.com
# * author:     jose.gomez@nutanix.com
# * version:    20200218
# task_type:    Execute
# task_name:    LaunchJobTemplate
# description:  Launch a job template or also known playbook 
# endregion

# region capture Calm variables
# * Capture variables here. This makes sure Calm macros are not referenced
# * anywhere else in order to improve maintainability.
awx_username = '@@{awx.username}@@'
awx_password = '@@{awx.secret}@@'
awx_api = '@@{awx_ip}@@'
awx_job_template_id = int('@@{awx_job_template_id}@@')
awx_extra_vars = "" #@@{awx_extra_vars}@@
host_ip = '@@{address}@@'
# endregion

# region functions
def make_api_call(url,method,username,username_secret,payload=None):
    """Makes an API call to an external API.

    Args:
        url: The URL for the external REST API endpoint.
        method: The REST method to use.
        username: The API user name.
        username_secret: The API user name password.
        payload: The JSON payload to include in the call.
    
    Returns:
        The API response.
    """
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }
    while True:
        print("Making a {} API call to {}".format(method, url))
        if payload:
            resp = urlreq(
                url,
                verb=method,
                auth='BASIC',
                user=username,
                passwd=username_secret,
                params=json.dumps(payload),
                headers=headers,
                verify=False
            )
        else:
            resp = urlreq(
                url,
                verb=method,
                auth='BASIC',
                user=username,
                passwd=username_secret,
                headers=headers,
                verify=False
            )

        # deal with the result/response
        if resp.ok:     
            return resp

        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print("Payload: {}".format(json.dumps(payload)))
            print('Status code: {}'.format(resp.status_code))
            print('Response: {}'.format(
                json.dumps(
                    json.loads(resp.content), 
                    indent=4)))
            exit(1)

def awx_run_job_template(api,username,password,job_template_id,host_ip,extra_vars=None):
    # region prepare api call
    # Form method, url and headers for the API call
    api_port = "80"

    api_endpoint = "/api/v2/job_templates/"
    api_action = "/launch/"

    url = "http://{}:{}{}{}{}".format(
        api,
        api_port,
        api_endpoint,
        job_template_id,
        api_action
    )
    
    method = "POST"

    payload = {
        "extra_vars": extra_vars,
        "limit": "@@{address}@@"
    }

    r = make_api_call(
        url,
        method,
        username,
        password,
        payload
    )

    if r.ok:
        job_id =  json.loads(r.content)['job']
        print 'Ansible Job ID: {0}'.format(job_id)

        awx_poll_job(api,username,password,job_id)
        print 'Ansible job status: successful'
    else:
        print 'Request failed', r.content
        exit(1)
    

def awx_poll_job(api,username,password,job_id):
    # region prepare api call
    # Form method, url and headers for the API call
    api_port = "80"

    api_endpoint = "/api/v2/jobs/"

    url = "http://{}:{}{}{}/".format(
        api,
        api_port,
        api_endpoint,
        job_id,
    )
    
    method = "GET"

    retries = 360
    job_status = ''

    while job_status != 'successful':
        r = make_api_call(
            url,
            method,
            username,
            password,
        )

        if r.ok:
            job_status = json.loads(r.content)['status']

            if job_status == "failed" or job_status == "error":
                print "Ansible job failed"
                break
        else:
            print 'Post request failed', r.content
            exit(1)

        sleep(10)
        retries -= 1
        if retries == 0:
            # if job hasn't finished yet, give up
            print 'Job may still running. Increase the retries or sleep time'
            exit(0)

# endregion
        
awx_run_job_template(awx_api,awx_username,awx_password,awx_job_template_id,host_ip,awx_extra_vars)