import requests
import json
import re
import time
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

pcip = "10.0.0.1"
USER_NAME = "admin"
PASSWORD = "xxxxxxx"

BASE_URL = "https://"+pcip+":9440"
VERSIONING_FEATURE = "VERSIONING"

object_store_uuid = "a646eee3-0c43-4a09-5205-bb9525a8d4a5"
bucket_name = "calm-objects-bucket5"
enable_versioning = False
non_current_version_expiration = None #days
expiration = None #days

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
    
    create_path = "/oss/api/nutanix/v3/objectstores/{}/buckets".format(object_store_uuid)
    create_payload = {
        "api_version": "3.0",
        "metadata": {
            "kind": "bucket"
        },
        "spec": {
            "description": "",
            "name": bucket_name,
            "resources": {
                "features": [
                ]
            }
        }
    }

    if enable_versioning:
        create_payload["spec"]["resources"]["features"].append(VERSIONING_FEATURE)
    if non_current_version_expiration or expiration:
        create_payload["spec"]["resources"]["lifecycle_configuration"] = {
            "Rule": [
                {
                    "Filter": {
                    },
                    "ID": "ntnx-frontend-emptyprefix-rule",
                    "Status": "Enabled"
                }
            ]
        }
        if non_current_version_expiration:
            create_payload["spec"]["resources"]["lifecycle_configuration"]["Rule"][0]["NoncurrentVersionExpiration"] = {"NoncurrentDays": non_current_version_expiration}
        if expiration:
            create_payload["spec"]["resources"]["lifecycle_configuration"]["Rule"][0]["Expiration"] = {"Days": expiration}

    json_resp, resp = _do_post(_url(create_path), create_payload)

    status_path = "/oss/api/nutanix/v3/objectstores/{}/buckets/{}".format(object_store_uuid, bucket_name)
    bucket_create_pending = True
    while bucket_create_pending:
        json_resp, resp = _do_get(_url(status_path))
        if json_resp["status"]["state"] == 'COMPLETE':
            bucket_create_pending = False
            print("Bucket '{}' creation is Completed.".format(bucket_name))
            break
        else:
            print("Bucket creation '{}' is in '{}' state.".format(bucket_name, json_resp["status"]["state"]))
            time.sleep(30)

if __name__ == '__main__':
    main()