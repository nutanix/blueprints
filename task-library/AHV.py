#!/usr/bin/python
##############################################
# Name        : AHV.py
# Author      : Calm Devops
# Version     : 1.0
# Description : Script will list all VMs available in a PC and update a VM
##############################################
import requests
import json
import re
import time
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class RestUtilException(Exception):
    pass

def _wrap(resp):
    """This function returns json resp if HTTP response is 200 and 
    it accepts session objects function output
    Returns:
       str : json string
    """
    if resp.status_code == 200 :
        try:
           return resp.json()
        except:
           return None
    else:
        try:
            resp_json = resp.json()
            if 'message' in resp_json:
                raise RestUtilException("Rest API request failed with error: %s" % resp_json['message'])
        except Exception:
            print(resp)
            raise RestUtilException("Rest API request failed : %s" % resp.reason)

def _do_get(url, cookies=None, params=None, auth=None, timeout=120):
    """This function is used to make requests.session.get HTTP call.
    This function further sends HTTP call response object to wrap function to get json in return
    Returns:
       str : json string
    """
    try:
        session = RestUtil(BASE_URL).get_session()
        headers = {'Content-Type': 'application/json'}
        for i in range(3):
            resp = session.get(url, params=params,
                            auth=_auth(), timeout=timeout,
                            headers=headers,cookies=cookies, verify=False)
            if resp.status_code in [500,503] :
                print("Sleeping for 60s because of status code",resp.status_code)
                time.sleep(60)
            else:
                break
        return _wrap(resp),resp
    except Exception:
        print("Rest API GET request failed")
        raise

def _do_post(url,params=None, cookies=None,auth=None, timeout=120):
    """This function is used to make requests.session.post HTTP call.
    This function further sends HTTP call response object to wrap function to get json in return
    Returns:
       str : json string
    """
    try:
        session = RestUtil(BASE_URL).get_session()
        headers = {'Content-Type': 'application/json'}
        for i in range(3):
            resp = session.post(url, data=json.dumps(params),
                            auth=_auth(), timeout=timeout,
                            headers=headers, cookies=cookies, verify=False)
            if resp.status_code in [500]:
                time.sleep(300)
            else:
                break
        #print(resp.json())
        return _wrap(resp),resp
    except Exception:
        print("Rest API POST request failed")
        raise

def _do_put(url, params=None, auth=None, timeout=120):
    """This function is used to make requests.session.put HTTP call.
    This function further sends HTTP call response object to wrap function to get json in return
    Returns:
       str : json string
    """
    try:
        session = RestUtil(BASE_URL).get_session()
        headers = {'Content-Type': 'application/json'}
        for i in range(3):
            resp = session.put(url, data=json.dumps(params),
                            auth=_auth(), timeout=timeout,
                            headers=headers, verify=False)
            if resp.status_code in [500] :
                time.sleep(300)
            else:
                break
        return _wrap(resp)
    except Exception:
        print("Rest API PUT request failed")
        raise

def _do_delete(url, params=None, auth=None, timeout=120):
    """This function is used to make requests.session.delete HTTP call.
    This function further sends HTTP call response object to wrap function to get json in return
    Returns:
       str : json string
    """
    try:
        session = RestUtil(BASE_URL).get_session()
        headers = {'Content-Type': 'application/json'}
        for i in range(3):
            resp = session.delete(url, auth=_auth(), timeout=timeout,
                              headers=headers, verify=False)
            if resp.status_code in [500] :
                time.sleep(300)
            else:
                break
        return _wrap(resp)
    except Exception:
        print("Rest API DELETE request failed")
        raise

def _get_session(server):
    http_req_adapter = requests.adapters.HTTPAdapter(max_retries=3, pool_maxsize=30, pool_connections=1)
    s = requests.Session()
    s.mount(server, http_req_adapter)
    return s

class RestUtil(object):
    __instance = None
    def __new__(cls, server):
        if RestUtil.__instance is None:
            RestUtil.__instance = object.__new__(cls)
        RestUtil.__instance.session = _get_session(server)
        return RestUtil.__instance

    def get_session(self):
        return self.session

def _v3_api_url(path):
    return BASE_URL+'/api/nutanix/v3'+path

def _v2_api_url(path):
    return BASE_URL+'/api/nutanix/v2'+path

def _auth():
    return (USER_NAME, PASSWORD)

def connect(url, user_name, password):
    global BASE_URL, USER_NAME, PASSWORD
    BASE_URL = url
    USER_NAME = user_name
    PASSWORD = password
    _s = RestUtil(url)

_url = _v3_api_url

pcip="<PC_IP>"
USER_NAME="<Username>"
PASSWORD="<Password>"
BASE_URL="https://"+pcip+":9440"

def get_cluster_uuid_by_name(name):
  """This function can be used to retrieve cluster uuid by passing name of cluster as an argument
    Returns:
       str : json string
   """
  path = "/clusters/list"
  enable_payload = {"kind":"cluster","sort_attribute": "string","length": 1000,"sort_order":"ASCENDING", "offset": 0 }
  json_resp,resp = _do_post(_url(path),enable_payload)
  cluster = [ i['metadata']['uuid'] for i in json_resp['entities'] if i['spec']['name'] == name ]
  if len(cluster) != 0:
    cluster_details = { "cluster_reference": { 'uuid' : cluster[0] , 'name':name, kind: 'cluster' }}
    return cluster_details

def get_image_uuid_by_name(name):
  """This function can be used to retrieve image uuid by passing name of the image  as an argument 
  Returns:
    str : uuid
  """
  path = "/images/list"
  enable_payload = {"kind":"image","sort_attribute": "string","length": 1000,"sort_order":"ASCENDING", "offset": 0 }
  json_resp,resp = _do_post(_url(path),enable_payload)
  image = [ i['metadata']['uuid'] for i in json_resp['entities'] if i['spec']['name'] == name ]
  if len(image) != 0:
    return image[0]

def get_vm_by_name(name):
  """This function can be used to get vm spec by passing vm name as an argument 
  Returns:
    str : vm spec 
  """
  json_resp = vm_list()
  vm = [ i for i in json_resp['entities'] if i['spec']['name'] == name ]
  if len(vm) != 0:
    return vm[0]

def vm_list():
  """This function can be used to get spec of all the vms present on pc 
  Returns:
    str : vm list spec
  """
  path = "/vms/list"
  enable_payload = {"kind":"vm","sort_attribute": "string","length": 1000,"sort_order":"ASCENDING", "offset": 0 }
  json_resp,resp = _do_post(_url(path),enable_payload)
  return json_resp

def update_vm(name):
  """This function retrieves vm spec using get_vm_by_name function, updates spec and
  then calls requests.session.put to update spec of vm"""
  vm = get_vm_by_name(name)
  del vm['status']
  vm['spec']['resources']['memory_size_mib'] = 1024*3
  print(vm)
  uuid = vm['metadata']['uuid']
  path = "/vms/"+uuid
  _do_put(_url(path),vm)

def delete_vm(name):
  """This function can be used to delete vm by passing vm name as an argument"""
  vm = get_vm_by_name(name)
  uuid = vm['metadata']['uuid']
  print(uuid)
  path = "/vms/"+uuid
  _do_delete(_url(path))
