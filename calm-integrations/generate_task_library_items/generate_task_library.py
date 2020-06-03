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
import logging
import argparse
import requests
logging.basicConfig(
        filename='seed_task_library.log',
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

headers = {'content-type': 'application/json', 'Accept': 'application/json'}


def help_parser():
    parser = argparse.ArgumentParser(
        description='Arguments for seeding task library')
    parser.add_argument('--pc',
                        required=True,
                        action='store',
                        help='PC to connect to')
    parser.add_argument('--port',
                        type=int,
                        default=9440,
                        action='store',
                        help='Port to connect on')
    parser.add_argument('--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to pc')
    parser.add_argument('--password',
                        required=True,
                        action='store',
                        help='Password to use when connecting to pc')
    parser.add_argument('-p', '--project',
                        required=True,
                        action='store',
                        help='Project to which task library item is created ')
    parser.add_argument('-s', '--script',
                        required=True,
                        action='store',
                        help='Script path')
    return parser
# --------------------------------------------------------------------------------- #


def get_project_uuid(base_url, auth, project_name):
    method = 'POST'
    url = base_url + "/projects/list"
    payload = {
        "length": 100,
        "offset": 0,
        "filter": "name=={0}".format(project_name)
    }
    resp = requests.request(
        method,
        url,
        data=json.dumps(payload),
        headers=headers,
        auth=(auth["username"], auth["password"]),
        verify=False
    )

    if resp.ok:
        json_resp = resp.json()
        if json_resp['metadata']['total_matches'] > 0:
            project = json_resp['entities'][0]
            project_uuid = project["metadata"]["uuid"]
            return project_uuid
        else:
            logging.error("Could not find project")
            sys.exit(-1)
    else:
        logging.error("Request failed")
        logging.error("Headers: {}".format(headers))
        logging.error('Status code: {}'.format(resp.status_code))
        logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        sys.exit(-1)

# --------------------------------------------------------------------------------- #


def seed_task_item(base_url, auth, project_name, path):
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
    project_uuid = get_project_uuid(base_url, auth, project_name)

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
    url = base_url + "/app_tasks"
    request_payload = payload
    headers = headers
    response = requests.request(
            "POST",
            url,
            data=json.dumps(request_payload),
            headers=headers,
            auth=auth,
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


if __name__ == "__main__":
    parser = help_parser().parse_args()
    pc_ip = parser.pc
    pc_port = parser.port
    script_path = parser.path
    project_name = "default"
    project = parser.project

    base_url = "https://{}:{}/api/nutanix/v3".format(pc_ip, str(pc_port))
    auth = {"username": parser.user, "password": parser.password}

    seed_task_item(base_url, auth, project, path)
