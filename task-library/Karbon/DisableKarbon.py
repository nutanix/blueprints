#!/usr/bin/python
##############################################
# Name        : Disable_Karbon.py
# Author      : Calm Devops
# Version     : 1.0
# Description : Script will disable Karbon
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
    if resp.status_code == 200:
        return resp.json()
    else:
        try:
            resp_json = resp.json()
            if 'message' in resp_json:
                raise RestUtilException("Rest API request failed with error: %s" % resp_json['message'])
        except Exception:
            print(resp)
            raise RestUtilException("Rest API request failed : %s" % resp.reason)

def _do_get(url, cookies=None, params=None, auth=None, timeout=120):
    try:
        session = RestUtil(BASE_URL).get_session()
        headers = {'Content-Type': 'application/json'}
        for i in range(3):
            resp = session.get(url, params=params,
                            auth=_auth(), timeout=timeout,
                            headers=headers,cookies=cookies, verify=False)
            if resp.status_code in [500] :
                time.sleep(300)
            else:
                break
        return _wrap(resp),resp
    except Exception:
        print("Rest API GET request failed")
        raise

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
PASSWORD="<Password>"

BASE_URL="https://"+pcip+":9440"

path = "/PrismGateway/services/rest/v1/genesis"
disable_payload = {"value":"{\".oid\":\"ClusterManager\",\".method\":\"disable_service\",\".kwargs\":{\"service_list_json\":\"{\\\"service_list\\\":[\\\"KarbonUIService\\\",\\\"KarbonCoreService\\\"]}\"}}"}
json_resp,resp = _do_post(_url(path),disable_payload)
if "true" not in json_resp['value']:
  print("Karbon Could not be enabled")
  exit(1)
print("Karbon service disabled")

