# Set creds, headers, and payload
pc_user = '@@{PC_Creds.username}@@'
pc_pass = '@@{PC_Creds.secret}@@'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
username = str("@@{name_prefix}@@" + "@" + "@@{domain}@@")


payload = {
  "name": "@@{bucket_name}@@",
  "bucket_permissions": [
    {
      "username": username,
      "permissions": [
        "READ",
        "WRITE"
      ]
    }
  ]
}

# Set the url and make the call
url = "https://localhost:9440/oss/api/nutanix/v3/objectstores/@@{OSS_UUID}@@/buckets/@@{bucket_name}@@/share"
resp = urlreq(url, verb='PUT', auth='BASIC', user=pc_user, passwd=pc_pass,
              params=json.dumps(payload), headers=headers, verify=False)

# If the call went through successfully
if resp.ok:
  print("User '" + username + "' added to bucket '@@{bucket_name}@@' successfully.")

# If the call failed
else:
  print(url + " call failed.")
  print(resp)
  exit(1)
