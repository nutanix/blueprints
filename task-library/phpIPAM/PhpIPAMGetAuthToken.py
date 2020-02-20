# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     stephane.bourdeaud@nutanix.com, igor.zecevic@nutanix.com
# * version:    v1.0/20200129 - initial version
# task_name:    PhpipamGetAuthToken
# description:  Given a phpIPAM server ip address or fqdn, a phpIPAM  
#               app id, username and password returns an api 
#               authentication token which can be used for other api 
#               calls.  A phpIPAM token is valid for 6 hours by default.
#!              Note that for obvious security reasons, the phpipam_token
#!              Calm variable should be marked private and secret.
# output vars:  phpipam_token
# endregion

# region capture Calm variables
username = '@@{phpipam.username}@@'
username_secret = "@@{phpipam.secret}@@"
api_server = "@@{phpipam_ip}@@"
phpipam_app_id = "@@{phpipam_app_id}@@"
# endregion

# region prepare api call
#! note that if your app security in php-ipam is set to 'none'
#! you will have to change the port to 80 and url to http.
api_server_port = "443"
api_server_endpoint = "/api/{}/user".format(phpipam_app_id)
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
# endregion

# region make api call
# make the API call and capture the results in the variable called "resp"
print("Making a {} API call to {}".format(method, url))
# ! Get rid of verify=False if you're using proper certificates
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
    print("Request was successful. Status code: {}".format(resp.status_code))
    print("phpipam_token={}".format(json.loads(resp.content)['data']['token']))
    exit(0)
else:
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion
