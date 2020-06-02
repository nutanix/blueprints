#!/usr/bin/env python3

import sys
import requests
import base64
from requests.auth import HTTPBasicAuth
import json
import configparser

account_data = {}
pc_data = {}

#verify_git_creds verifies the given got credentials have access to the repo
def verify_git_creds(repo, owner, username, password):
    git_repo_endpoint = "https://api.github.com/repos/"+owner+"/"+repo
    response = requests.get(git_repo_endpoint, auth=HTTPBasicAuth(username, password))
    if response.status_code == 200:
        return True
    else:
        return False

#verify_pc_creds verifies the given pc credentials
def verify_pc_creds(pc_ip, pc_port, pc_username, pc_password):
    pc_endpoint = "https://"+pc_ip+":"+pc_port+"/api/nutanix/v3/projects/list"
    payload = {}
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.post(pc_endpoint, auth=HTTPBasicAuth(pc_username, pc_password),
               data=json.dumps(payload), headers=headers, verify=False)
    if response.status_code == 200:
        return True
    else:
        return False

#get_content gets the blueprint of previous versions
def get_content_git(blueprint, project, account_data, ref="master"):
    owner       = account_data['owner']
    repo        = account_data['repository']
    username    = account_data['username']
    password    = account_data['password']
    get_content_endpoint = "https://api.github.com/repos/"+owner+"/"+repo+"/contents/"+project+"/blueprints/"+blueprint+".json"
    params      = {"ref": ref}
    response    = requests.get(get_content_endpoint, auth=HTTPBasicAuth(username, password),
                  params=params)
    respData    = json.loads(response.content)
    return respData

#get_git_file_list gets the blueprint of previous versions
def get_git_file_list(blueprint, project, account_data, ref="master"):
    owner       = account_data['owner']
    repo        = account_data['repository']
    username    = account_data['username']
    password    = account_data['password']
    get_content_endpoint = "https://api.github.com/repos/"+owner+"/"+repo+"/contents/"+project+"/blueprints/"
    params      = {"ref": ref}
    response    = requests.get(get_content_endpoint, auth=HTTPBasicAuth(username, password),
                  params=params)
    respData    = json.loads(response.content)
    return respData

#create_blueprint creates blueprint and returns blueprint sha and commit sha
def create_blueprint(blueprint, project, blueprint_json, account_data):
    owner       = account_data['owner']
    repo        = account_data['repository']
    username    = account_data['username']
    password    = account_data['password']
    create_blueprint_endpoint = "https://api.github.com/repos/"+owner+"/"+repo+"/contents/"+project+"/blueprints/"+blueprint+".json"
    payload     = {"message": "creates blueprint "+ blueprint,
                   "content": base64.b64encode(blueprint_json).decode('ascii')}
    response    = requests.put(create_blueprint_endpoint, auth=HTTPBasicAuth(username, password),
                  data=json.dumps(payload))
    respData    = json.loads(response.content)
    return respData['commit']['sha']

#update_blueprint updates blueprint and returns blueprint sha and commit sha
def update_blueprint(blueprint, project, blueprint_json, prev_bp_sha, account_data):
    owner       = account_data['owner']
    repo        = account_data['repository']
    username    = account_data['username']
    password    = account_data['password']
    update_blueprint_endpoint = "https://api.github.com/repos/"+owner+"/"+repo+"/contents/"+project+"/blueprints/"+blueprint+".json"
    payload     = {"message": "updates blueprint "+ blueprint,
                   "content": base64.b64encode(blueprint_json).decode('ascii'),
                   "sha"    : prev_bp_sha}
    response    = requests.put(update_blueprint_endpoint, auth=HTTPBasicAuth(username, password),
                  data=json.dumps(payload))
    respData    = json.loads(response.content)
    return respData['commit']['sha']

def get_bp_list(pc_data, length, offset):
    ip = pc_data["ip"]
    port = pc_data["port"]
    username = pc_data["username"]
    password = pc_data["password"]
    get_bp_url = "https://"+ip+":"+port+"/api/nutanix/v3/blueprints/list"
    payload = {'length': length, 'offset': offset, 'filter': "state!=DELETED"}
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.post(get_bp_url, auth=HTTPBasicAuth(username, password),
               data=json.dumps(payload), headers=headers, verify=False)
    respData = json.loads(response.content)
    return respData

def get_bp_list_in_project(pc_data):
    ip = pc_data["ip"]
    port = pc_data["port"]
    username = pc_data["username"]
    password = pc_data["password"]
    projectList = pc_data["project_list"]
    projectBlueprintList = []
    length = 20
    count = 0
    offset = 0
    blueprintCount = get_bp_list(pc_data, length, offset)["metadata"]["total_matches"]
    while True:
        blueprintList = get_bp_list(pc_data, length, offset)
        for bp in blueprintList["entities"]:
            if bp["metadata"]["project_reference"]["name"] in projectList:
                projectBlueprintList.append(bp)

        offset += length
        count += length
        if (count >= blueprintCount):
            break
    return projectBlueprintList

def get_bp_names(bp_list):
    blueprint_names=[]
    for bp in bp_list:
        blueprint_names.append({ "name" : bp["metadata"]["name"],
                                 "uuid" : bp["metadata"]["uuid"], 
                                 "project" : bp["metadata"]["project_reference"]["name"] 
                          })
    return blueprint_names

def get_content_calm(uuid,pc_data):
    ip = pc_data["ip"]
    port = pc_data["port"]
    username = pc_data["username"]
    password = pc_data["password"]
    get_bp_url = "https://"+ip+":"+port+"/api/nutanix/v3/blueprints/{}/export_json".format(uuid)
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.get(get_bp_url, auth=HTTPBasicAuth(username, password),
               headers=headers, verify=False)
    respData = response.content
    return respData

def git_update(blueprint_names,account_data,pc_data):

    for bp in blueprint_names:
        project     = bp["project"]

        old_bp_sha  = ""
        git_file_list = get_git_file_list(bp["name"], project, account_data, ref="master")
        if  "message" in git_file_list and git_file_list["message"] == "Not Found":
            print("[WARNING] Project directory {} not found in the repository.".format(bp["project"]))
            sys.exit(1)
        print("[INFO] Fetching BP {} details.".format(bp["name"]))
        blueprint_json_from_calm = json.loads(get_content_calm(bp["uuid"], pc_data)) # convert string received from CALM into JSON object
        blueprint_json_pp = json.dumps(blueprint_json_from_calm, indent=4, sort_keys=True) # convert JSON object into prettyprinted JSON string
        blueprint_json = blueprint_json_pp.encode("utf-8") # # encode prettyprinted JSON string into utf-8 for base64 encode
        for file in git_file_list:
            if file["name"] == bp["name"]+".json":
                old_bp_sha = file["sha"]
                break
        if old_bp_sha == "":
            print("[INFO] Creating BP {}.".format(bp["name"]))
            commit_sha = create_blueprint(bp["name"], project, blueprint_json, account_data)
        else:
            print("[INFO] Updating BP {}.".format(bp["name"]))
            commit_sha = update_blueprint(bp["name"], project, blueprint_json, old_bp_sha, account_data)
def get_help():
    print("""config.ini file not found or missing some config parameters:
    [calm]
    pc_ip = <pc_ip>
    pc_port = <pc_port>
    username = <pc_username>
    password = <pc_password>
    project_list = <project1,project2>
    [git]
    owner = <git_owner>
    repository = <git_repository>
    username = <git_username>
    password = <git_password>
    """)

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    if 'calm' not in config or 'git' not in config:
        print("[ERROR] Failed to parse calm/git config in 'config.ini'")
        get_help()
        sys.exit(1)
    try:
        account_data["repository"] = config["git"]["repository"]
        account_data["owner"] = config["git"]["owner"]
        account_data["username"] = config["git"]["username"]
        account_data["password"] = config["git"]["password"]
    except KeyError:
        print("[ERROR] Missing git config 'repository', 'owner', 'username' & 'password'.")
        get_help()
        sys.exit(1)
    except:
        print("[ERROR] Error while loading config file")
    try:
        pc_data["ip"] = config["calm"]["pc_ip"]
        pc_data["port"] = config["calm"]["pc_port"]
        pc_data["username"] = config["calm"]["username"]
        pc_data["password"] = config["calm"]["password"]
        pc_data["project_list"] = config["calm"]["project_list"]
    except KeyError:
        print("[ERROR] Missing pc config 'pc_ip', 'pc_port', 'username', 'password' & 'project_list'.")
        get_help()
        sys.exit(1)
    except:
        print("[ERROR] Error while loading config file.")

    git_status = verify_git_creds(account_data["repository"],account_data["owner"],account_data["username"],account_data["password"])
    if git_status != True:
        print("[ERROR] Failed to authenticate git user.")
        sys.exit(1)
    pc_status = verify_pc_creds(pc_data["ip"], pc_data["port"], pc_data["username"], pc_data["password"])
    if pc_status != True:
        print("[ERROR] Failed to authenticate to PC.")
        sys.exit(1)
    blueprint_list = get_bp_list_in_project(pc_data)
    blueprint_names = get_bp_names(blueprint_list)
    if len(blueprint_names) == 0:
        print("[INFO] No blueprints found in the project.")
        sys.exit(0)
    git_update(blueprint_names,account_data,pc_data)
