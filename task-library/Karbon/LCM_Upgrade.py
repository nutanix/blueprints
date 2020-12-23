#!/usr/bin/python
##############################################
# Name        : LCM_Upgrade.py
# Author      : Calm Devops
# Version     : 1.0
# Description : Script will do LCM inventory
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

def _do_post(url,params=None, cookies=None,auth=None, timeout=120):
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
    return BASE_URL+path

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
USER_NAME="<username>"
PASSWORD="<password>"

BASE_URL="https://"+pcip+":9440"

path = "/PrismGateway/services/rest/v1/genesis"
lcm_payload = {"value":"{\".oid\":\"LifeCycleManager\",\".method\":\"lcm_framework_rpc\",\".kwargs\":{\"method_class\":\"LcmFramework\",\"method\":\"get_config\"}}"}
is_lcm_update_needed_payload = {"value":"{\".oid\":\"LifeCycleManager\",\".method\":\"lcm_framework_rpc\",\".kwargs\":{\"method_class\":\"LcmFramework\",\"method\":\"is_lcm_update_needed\"}}"}
json_resp,resp = _do_post(_url(path),is_lcm_update_needed_payload)
if "true" not in json_resp['value']:
  print("LCM is already up to date.")
else:
  print("Performing Inventory")
  lcm_payload = {"value":"{\".oid\":\"LifeCycleManager\",\".method\":\"lcm_framework_rpc\",\".kwargs\":{\"method_class\":\"LcmFramework\",\"method\":\"perform_inventory\",\"args\":[\"http://download.nutanix.com/lcm/2.0\"]}}"}
  json_resp,resp = _do_post(_url(path),lcm_payload)

  Upgrade_status = {"value":"{\".oid\":\"LifeCycleManager\",\".method\":\"lcm_framework_rpc\",\".kwargs\":{\"method_class\":\"LcmFramework\",\"method\":\"is_lcm_operation_in_progress\"}}"}
  while True: 
    json_resp,resp = _do_post(_url(path),Upgrade_status)
    if 'Inventory' not in json_resp['value']:
      print("Upgrade Completed")
      break
    print("Upgrade in process")
    time.sleep(60)
