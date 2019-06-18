#!/usr/bin/env python

import sys
import requests
import base64
from requests.auth import HTTPBasicAuth
import json
import configparser
import hashlib

account_data = {}
pc_data = {}

#verify_git_creds verifies the given got credentials have access to the repo
def verify_git_creds(repo, owner, username, password):
    git_repo_endpoint = "https://api.bitbucket.org/2.0/repositories/"+owner+"/"+repo
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
    get_content_endpoint = "https://api.bitbucket.org/2.0/repositories/"+owner+"/"+repo+"/src/master/"+project+"/blueprints/"+blueprint+".json"
    params      = {"ref": ref}
    response    = requests.get(get_content_endpoint, auth=HTTPBasicAuth(username, password),
                  params=params)
    respCode    = response.status_code
    if respCode == 200:
        respData    = response.content
    else:
        respData    = ""
    return respCode, respData

#create_blueprint creates blueprint and returns blueprint sha and commit sha
def create_blueprint(blueprint, project, blueprint_json, account_data):
    owner       = account_data['owner']
    repo        = account_data['repository']
    username    = account_data['username']
    password    = account_data['password']
    create_blueprint_endpoint = "https://api.bitbucket.org/2.0/repositories/"+owner+"/"+repo+"/src" 
    files = {
            project+"/blueprints/"+blueprint+".json":(blueprint+".json", blueprint_json)
            }
    response    = requests.post(create_blueprint_endpoint, auth=HTTPBasicAuth(username, password),
                  files=files)
    respCode    = response.status_code
    respData    = response.reason
    return respCode, respData

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
    get_bp_url = "https://"+ip+":"+port+"/api/nutanix/v3/blueprints/{}".format(uuid)
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.get(get_bp_url, auth=HTTPBasicAuth(username, password),
               headers=headers, verify=False)
    respData = response.content
    return respData

def git_update(blueprint_names,account_data,pc_data):
    hash_md5 = hashlib.md5()
    for bp in blueprint_names:
        project     = bp["project"]

        old_bp_sha  = ""
        git_file_resp_code, git_file_data = get_content_git(bp["name"], project, account_data, ref="master")
        print "Fetching BP {} details.".format(bp["name"])
        blueprint_json = get_content_calm(bp["uuid"], pc_data)
        git_file_hash = hashlib.sha1(git_file_data).hexdigest()
        bp_file_hash = hashlib.sha1(blueprint_json).hexdigest()
        if git_file_resp_code != 200 and git_file_data == "":
            resp_code, resp_data = create_blueprint(bp["name"], project, blueprint_json, account_data)
            print "Creating Bp {} with status code : {} & message '{}'.".format(bp["name"], resp_code, resp_data)
            if resp_code != 201:
                print "Failed to create Blueprint, Please check project directory {}. Reason: {}".format(bp["project"], resp_data)
        else:
            if git_file_hash != bp_file_hash:
                resp_code, resp_data = create_blueprint(bp["name"], project, blueprint_json, account_data)

def get_help():
    print """config.ini file not found or missing below config:
    [calm]
    pc_ip = <pc_ip>
    pc_port = <pc_port>
    username = <pc_username>
    password = <pc_password>
    project_list = <project1,project2>
    [bitbucket]
    owner = <bitbucket_owner>
    repository = <bitbucket_repository>
    username = <bitbucket_username>
    password = <bitbucket_password>
    """

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    if 'calm' not in config or 'bitbucket' not in config: 
        print "Failed to parse calm/bitbucket config in 'config.ini'"
        sys.exit(1)
    try:
        account_data["repository"] = config["bitbucket"]["repository"]
        account_data["owner"] = config["bitbucket"]["owner"]
        account_data["username"] = config["bitbucket"]["username"]
        account_data["password"] = config["bitbucket"]["password"]
    except KeyError:
        print "Missing bitbucket config 'repository', 'owner', 'username' & 'password'."
        get_help()
        sys.exit(1)
    except:
        print "Error while loading config file"
    try:
        pc_data["ip"] = config["calm"]["pc_ip"]
        pc_data["port"] = config["calm"]["pc_port"]
        pc_data["username"] = config["calm"]["username"]
        pc_data["password"] = config["calm"]["password"]
        pc_data["project_list"] = config["calm"]["project_list"]
    except KeyError:
        print "Missing pc config 'pc_ip', 'pc_port', 'username', 'password' & 'project_list'."
        get_help()
        sys.exit(1)
    except:
        print "Error while loading config file."

    git_status = verify_git_creds(account_data["repository"],account_data["owner"],account_data["username"],account_data["password"])
    if git_status != True:
        print "Failed to authenticate Bitbucket user."
        sys.exit(1)
    pc_status = verify_pc_creds(pc_data["ip"], pc_data["port"], pc_data["username"], pc_data["password"])
    if pc_status != True:
        print "Failed to authenticate to PC."
        sys.exit(1)
    blueprint_list = get_bp_list_in_project(pc_data)
    blueprint_names = get_bp_names(blueprint_list)
    if len(blueprint_names) == 0:
        print "No blueprints found in the project."
        sys.exit(0)
    git_update(blueprint_names,account_data,pc_data)