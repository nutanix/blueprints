# Set creds, headers, and payload
pc_user = '@@{PC_Creds.username}@@'
pc_pass = '@@{PC_Creds.secret}@@'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
username = str("@@{name_prefix}@@" + "@" + "@@{domain}@@")
payload = {
    "users":[
        {
            "type":"external",
            "username": username
        }
    ]
}

# Set the address and make the call
url = "https://localhost:9440/oss/iam_proxy/buckets_access_keys"
resp = urlreq(url, verb='POST', auth='BASIC', user=pc_user, passwd=pc_pass,
              params=json.dumps(payload), headers=headers, verify=False)

# If the call went through successfully
if resp.ok:
  entity = json.loads(resp.content)['users'][0]
  
  # Handle a new user
  if entity['buckets_access_keys'] is not None:
    print("USER_UUID=" + entity['uuid'])
    print("ACCESS_KEY_ID=" + entity['buckets_access_keys'][0]['access_key_id'])
    print("SECRET_ACCESS_KEY=" + entity['buckets_access_keys'][0]['secret_access_key'])
    exit(0)

  # If the user already exists, get a list of users
  else:
    print("User already exists, getting user UUID and adding new keys.")
    url = "https://localhost:9440/oss/iam_proxy/users"
    resp = urlreq(url, verb='GET', auth='BASIC', user=pc_user, passwd=pc_pass,
                  headers=headers, verify=False)
    
    # If the user get call went through, find the user UUID
    if resp.ok:
      for user in json.loads(resp.content)['users']:
        if user['username'] == username:
          user_uuid = user['uuid']
          print("USER_UUID=" + user_uuid)
      
      # Now create keys with the user's UUID
      url = 'https://localhost:9440/oss/iam_proxy/users/' + user_uuid + '/buckets_access_keys'
      resp = urlreq(url, verb='POST', auth='BASIC', user=pc_user, passwd=pc_pass,
                    headers=headers, verify=False)
      
      # If resp is ok, set the variables
      if resp.ok:
        entity = json.loads(resp.content)
        print("ACCESS_KEY_ID=" + entity['access_key_id'])
        print("SECRET_ACCESS_KEY=" + entity['secret_access_key'])
        exit(0)
      
      # If the oss/iam_proxy/users/<uuid>/buckets_access_keys call failed
      else:
        print("oss/iam_proxy/users/" + user_uuid + "/buckets_access_keys POST failed.")
        print(resp)
        exit(1)

    # If the oss/iam_proxy/users failed
    else:
      print("oss/iam_proxy/users GET failed.")
      print(resp)
      exit(1)

# If the oss/iam_proxy/buckets_access_keys call failed
else:
  print("oss/iam_proxy/buckets_access_keys POST failed")
  print(resp)
  exit(1)