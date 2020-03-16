# region DELETE ME AFTER READING
# ! Meant to be edited in VSCode w/ the BetterComments extension installed

# * Conventions:
# * Golden Rule: Adhere to https://pep8.org/ Anything listed below which is
# * in contradiction with PEP8 is a lie.
# 1. use all lower case for variable names.
# 2. when composing variable names, use underscore to separate words.
#    Exp: username_secret. Use this same convention in Calm.
# 3. name sections with comments, and comment code where deemed useful.
# 4. don't print secrets, including tokens. Favor authentication
#    (login/logout) in each task.
# 5. when saving your script, name it as the task name appears in Calm,
#    using the following convention: NameOfIntegrationPointAPIendpointMethod.py
# 6. use double quotes first, then single quotes.
# 7. Try your best and keep line length under 80 characters, even though
#    it makes your eyes bleed.
# endregion

# region headers
# escript-template v20200316 / stephane.bourdeaud@nutanix.com
# TODO Fill in this section with your information
# * author:     <your email address here>
# * version:    <date / notes>
# task_name:    <enter the name of the task this script is for as it appears
# in your blueprint>
# description:
# task type:    SetVariable or Execute
# input_vars:   credname (credentials), endpoint_ip
# output_vars:
# endregion

# region capture Calm variables
# * Capture variables here. This makes sure Calm macros are not referenced
# * anywhere else in order to improve maintainability.
username = '@@{credname.username}@@'
username_secret = "@@{credname.secret}@@"
api_server = "@@{endpoint_ip}@@"
# endregion

# region api call function
def process_request(url, method, headers, payload=None):
    if (payload is not None):
        payload = json.dumps(payload)
    #* using basic authentication if no cookie was passed in the headers
    if "Cookie" not in headers:
        # ! Get rid of verify=False if you're using proper certificates
        r = urlreq(url, verb=method, auth='BASIC', user=username, passwd=password, params=payload, verify=False, headers=headers)
    else:
        # ! Get rid of verify=False if you're using proper certificates
        r = urlreq(url, verb=method, params=payload, verify=False, headers=headers)
    #* now dealing with the response
    if r.ok:
        print("Request was successful")
        print("Status code: {}".format(r.status_code))
        if (r.content and ('/rest/com/vmware/cis/session' not in url)):
            print('Response: {}'.format(json.dumps(json.loads(r.content), indent=4)))
    #* use this to deal with specific api error code
    #elif ((r.status_code == 400):
    #    print("Status code: {}".format(r.status_code))
    #    print("Object already exists: skipping")
    else:
        print("Request failed")
        print('Status code: {}'.format(r.status_code))
        #* printing headers can be a security breach if you expose the cookie
        if "Cookie" not in headers:
            print("Headers: {}".format(headers))
        if (payload is not None):
            print("Payload: {}".format(json.dumps(payload)))
        if r.content:
            print('Response: {}'.format(json.dumps(json.loads(r.content), indent=4)))
        exit(1)
    return r
# endregion

# region prepare api call
api_server_port = "443"
api_server_endpoint = "/apis/batch/v1/"
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

# Compose the json payload
payload = {
    "example": "example",
    "example": {
        "example": "example"
    }
}
# endregion

# region make api call
# make the API call and capture the results in the variable called "resp"
print("Making a {} API call to {}".format(method, url))
resp = process_request(url, method, headers, payload)

# ! If you are passing on a variable you will need to print it
# ! example: print("calm_variable_name={}".format(python_variable))
# endregion
