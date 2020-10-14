#!/usr/bin/python
##############################################
# Name        : Karbon.py
# Author      : Calm Devops
# Version     : 1.0
# Description : Script will enable Karbon,download image and create cluster
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

def _do_get(url, cookies=None, params=None, auth=None, timeout=120):
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
ClusterName="<clustername>"  # MyCluster1
VLAN_ID = "<vlan_id>"  # eg. 889
storage_container = "<clusternae>" #eg. default-container-168023
KubVersion = "<version>" #eg 1.16.8-0"

BASE_URL="https://"+pcip+":9440"

path = "/PrismGateway/services/rest/v1/genesis"
enable_payload = {"value":"{\".oid\":\"ClusterManager\",\".method\":\"enable_service_with_prechecks\",\".kwargs\":{\"service_list_json\":\"{\\\"service_list\\\":[\\\"KarbonUIService\\\",\\\"KarbonCoreService\\\"]}\"}}"}
json_resp,resp = _do_post(_url(path),enable_payload)
if "true" not in json_resp['value']:
  print("Karbon Could not be enabled")
  exit(1)
print("Karbon service Enabled")
#time.sleep(60)

SubnetURL = "/api/nutanix/v3/subnets/list"
SubnetPayload = { "kind": "subnet", "filter": "vlan_id=={}".format(VLAN_ID), "length": 100 }
out,resp  = _do_post(_url(SubnetURL),SubnetPayload)
if len(out['entities']) == 0:
  print(VLAN_ID," not found")
  exit(1)
vlan_uuid = out['entities'][0]['metadata']['uuid']
cluster_uuid = out['entities'][0]['spec']['cluster_reference']['uuid']
print("Vlan uuid is", vlan_uuid)

dummypath = "/api/nutanix/v3/users/me"
json_resp,resp = _do_get(_url(dummypath))
cookies = resp.cookies

path = "/karbon/acs/image/list"
image_uuid = []
while len(image_uuid) == 0:
  out,resp  = _do_get(_url(path),cookies=cookies)
  image_uuid = [ (i["uuid"],i["os_flavor"]) for i in out if i["uuid"].strip()!=""]
  if len(image_uuid) == 0 :
    print("Enable in process, Image not found")
    karbonget = "/karbon/"
    out,resp  = _do_get(_url(karbonget),cookies=cookies)
    time.sleep(60)
print("Image uuid is ",image_uuid)
os_flavor = image_uuid[0][1]
print("Os flavor",image_uuid[0][1])

KarbonImageDownload = "/karbon/acs/image/download"
download_payload = {"uuid":image_uuid[0][0] }
out,resp  = _do_post(_url(KarbonImageDownload),download_payload,cookies=cookies)
image_uuid2 = json.loads(resp.text)['image_uuid']
print("Download Resp: ",resp.text)

dlstatus = "Downloading"
while dlstatus == "Downloading":
  out,resp  = _do_get(_url(path),cookies=cookies)
  dlstatus = out[0]['status']
  time.sleep(20)
  print("Status is: ",dlstatus)

time.sleep(10)
ClusterUrl = "/karbon/acs/k8s/cluster"
DevClusterPayload = {"name":ClusterName,"description":"","vm_network":vlan_uuid,"k8s_config":{"service_cluster_ip_range":"172.19.0.0/16","network_cidr":"172.20.0.0/16","fqdn":"","workers":[{"node_pool_name":"","name":"","uuid":"","resource_config":{"cpu":8,"memory_mib":8192,"image":image_uuid2,"disk_mib":122880}}],"masters":[{"node_pool_name":"","name":"","uuid":"","resource_config":{"cpu":2,"memory_mib":4096,"image":image_uuid2,"disk_mib":122880}}],"os_flavor":os_flavor,"network_subnet_len":24,"version":KubVersion},"cluster_ref":cluster_uuid,"logging_config":{"enable_app_logging":False},"storage_class_config":{"metadata":{"name":"default-storageclass"},"spec":{"reclaim_policy":"Delete","sc_volumes_spec":{"cluster_ref":cluster_uuid ,"user":USER_NAME,"password":PASSWORD,"storage_container":storage_container,"file_system":"ext4","flash_mode":False}}},"etcd_config":{"num_instances":1,"name":ClusterName,"nodes":[{"node_pool_name":"","name":"","uuid":"","resource_config":{"cpu":4,"memory_mib":8192,"image":image_uuid2,"disk_mib":40960}}]}}
out,resp  = _do_post(_url(ClusterUrl),DevClusterPayload,cookies=cookies)
print(resp.text)
