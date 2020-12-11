import requests
import json
import re
import time
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

pcip = "10.135.20.2"
USER_NAME = "admin"
PASSWORD = "Nutanix@123"

BASE_URL = "https://"+pcip+":9440"

objects_name = "calm-objects"
objects_domain = "nutanix.local"
cluster_name = "calm-objects"
cluster_reference = "00057434-6e66-188a-0000-00000000ae72"
buckets_infra_network_dns = "10.135.22.138"
buckets_infra_network_vip = "10.135.22.139"
buckets_infra_network_reference = "795997e3-ef95-4788-8039-ea56546a018e"
client_access_network_reference = "795997e3-ef95-4788-8039-ea56546a018e"
total_vcpu_count = 30
total_memory_size_mib = 98304
total_capacity_gib = 1024
client_access_network_ip_list = ["10.135.22.140","10.135.22.141","10.135.22.142","10.135.22.145"]

class RestUtilException(Exception):
    pass

def _wrap(resp):
    if resp.status_code in [200, 202]:
        return resp.json()
    else:
        try:
            resp_json = resp.json()
            if 'message_list' in resp_json:
                raise RestUtilException("Rest API request failed with error: %s" % resp_json['message_list'][0]['message'])
        except Exception:
            print(resp)
            raise RestUtilException("Rest API request failed : %s" % resp.content)

def _do_get(url, cookies=None, params=None, auth=None, timeout=120):
    try:
        session = RestUtil(BASE_URL).get_session()
        headers = {'Content-Type': 'application/json'}
        for i in range(3):
            resp = session.get(url, params=params,
                            auth=_auth(), timeout=timeout,
                            headers=headers,cookies=cookies, verify=False)
            if resp.status_code in [500] :
                time.sleep(30)
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
                time.sleep(30)
            else:
                break
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

def main():

    _url = _v3_api_url
    
    create_path = "/oss/api/nutanix/v3/objectstores"
    create_payload = {
    "api_version": "3.0",
    "metadata": {
        "kind": "objectstore"
    },
    "spec": {
        "name": objects_name,
        "description": objects_name,
        "resources": {
        "domain": objects_domain,
        "cluster_reference": {
            "kind": "cluster",
            "uuid": cluster_reference
        },
        "buckets_infra_network_dns": buckets_infra_network_dns,
        "buckets_infra_network_vip": buckets_infra_network_vip,
        "buckets_infra_network_reference": {
            "kind": "subnet",
            "uuid": buckets_infra_network_reference
        },
        "client_access_network_reference": {
            "kind": "subnet",
            "uuid": client_access_network_reference
        },
        "aggregate_resources": {
            "total_vcpu_count": total_vcpu_count,
            "total_memory_size_mib": total_memory_size_mib,
            "total_capacity_gib": total_capacity_gib
        },
        "client_access_network_ip_list": client_access_network_ip_list
        }
    }
    }
    json_resp, resp = _do_post(_url(create_path), create_payload)
    oss_uuid = json_resp["metadata"]["uuid"]
    #oss_uuid = "017bf260-8161-4985-636a-02353fd13d61"

    status_path = "/oss/api/nutanix/v3/objectstores/{}".format(oss_uuid)
    objects_create_pending = True
    while objects_create_pending:
        json_resp, resp = _do_get(_url(status_path))
        if json_resp["status"]["state"] == 'COMPLETE':
            objects_create_pending = False
            print("Objects '{}' creation is Completed.".format(objects_name))
            break
        else:
            print("Objects creation '{}' is in '{}' state : '{}'.".format(oss_uuid, json_resp["status"]["state"], json_resp["status"]["percent_complete"]))
            time.sleep(30)

if __name__ == '__main__':
    main()