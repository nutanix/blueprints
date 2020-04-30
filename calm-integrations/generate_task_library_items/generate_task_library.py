"""
This script is used to create task-library items,
that can be pushed to pc if ip and creds are passed to the script.

This script takes script .sh, .es as input
files only (.sh for shell scripts & .es for escripts).

Please pass file name as first argument.
"""
import os
import sys
import json
import ntpath

script_path = sys.argv[1]
project_name = "default"
project_uuid = "7ffa7e0c-0929-41b7-bb30-4dfe836e8435"

script_content = ""

try:
    scriptf = open(script_path, "r")
except IOError:
    print("ERROR: File not found.")
    sys.exit(1)
finally:
    script_content = scriptf.read()

script_name = ntpath.basename(script_path)
item_name = os.path.splitext(script_name.replace("_", ' '))[0]
script_type = os.path.splitext(script_name)[1].replace('.', '')

payload = {
  "api_version": "3.0",
  "metadata": {
    "kind": "app_task",
    "project_reference": {
      "kind": "project",
      "name": project_name,
      "uuid": project_uuid
    }
  },
  "spec": {
    "name": item_name,
    "resources": {
      "variable_list": [],
      "attrs": {
        "script": script_content,
        "script_type": script_type
      },
      "type": "EXEC"
    },
    "description": ""
  }
}

pc_ip = "10.0.0.0"
pc_username = "admin"
pc_password = "secret"

if pc_ip and pc_username and pc_password:
    import requests

    url = "https://{}:9440/api/nutanix/v3/app_tasks".format(pc_ip)
    request_payload = payload
    headers = {'content-type': "application/json"}
    response = requests.request(
            "POST",
            url,
            data=json.dumps(request_payload),
            headers=headers,
            auth=(pc_username, pc_password),
            verify=False
            )
    if response.status_code != 200:
        print("ERROR: Unable to preseed task library item '{}': {}.".format(
            item_name, response.content)
            )
        sys.exit(1)
    if response.json()["status"]["state"] != "ACTIVE":
        print("ERROR: Failed to preseed item '{}': {}.".format(
            item_name, response.json()["message_list"][0]["message"])
            )
        sys.exit(1)
    print("INFO: Preseeded task library '{}'.".format(item_name))
