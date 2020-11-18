#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO- Add authentication
# TODO- Add skip registration flag

# pylint: disable= E402

import gevent.monkey
gevent.monkey.patch_all()
import sys
import logging
import warnings
import os
import requests
import json
from IPython.frontend.terminal.embed import InteractiveShellEmbed

from calm.common.config import init_config, get_config_dict, get_config
cfg = init_config()

from calm.common.flags import gflags
gflags.FLAGS(sys.argv)

from calm.lib.model.store.db import create_db_connection
from calm.pkg.common.scramble import init_scramble
from calm.lib.model.store.db_session import create_session, flush_session, set_session_type
import calm.lib.model as model

warnings.filterwarnings("ignore")
log = logging.getLogger('cshell')
logging.basicConfig(level=logging.INFO,
                    format="%(message)s",
                    datefmt='%H:%M:%S')

SOURCE_PC_IP = "10.44.19.70"
DESTINATION_PC_IP = "10.46.7.50"
PC_PORT = 9440
LENGTH = 100

source_base_url = "https://{}:{}/api/nutanix/v3".format(SOURCE_PC_IP,str(PC_PORT))
dest_base_url = "https://{}:{}/api/nutanix/v3".format(DESTINATION_PC_IP,str(PC_PORT))
source_pc_auth = { "username": os.environ['SOURCE_PC_USER'], "password": os.environ['SOURCE_PC_PASS']}
dest_pc_auth = { "username": os.environ['DEST_PC_USER'], "password": os.environ['DEST_PC_PASS']}

user_categories_list = []

CATEGORY_KEY_LIST = [
    "CalmApplication",
    "CalmDeployment",
    "CalmService",
    "CalmPackage",
    "OSType",
    "CalmVmUniqueIdentifier",
    "CalmUsername",
    "account_uuid"
]

headers = {'content-type': 'application/json', 'Accept': 'application/json'}

def init_contexts():
    cfg = get_config()
    keyfile = cfg.get('security', 'keyfile')
    init_scramble(keyfile)
    set_session_type('green', cfg.get('store', 'flush_parallelisation_factor'), cfg.get('store', 'bulk_size'))
    create_db_connection(register_entities=False)

def create_category(base_url, auth, key):
    method = 'PUT'
    url = base_url + "/categories/{}".format(key)
    payload = {
        "name": key
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
        return True
    else:
        print("Failed to create category key '{}'.".format(key))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)

def get_category_values(base_url, auth, key, offset):
    method = 'POST'
    url = base_url + "/categories/{}/list".format(key)
    category_value_list = []
 
    payload = {"length": LENGTH, "offset": offset}
    resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
    )
    if resp.ok:
        resp_json = resp.json()
        for entity in resp_json["entities"]:
            category_value_list.append(entity["value"])
        return resp_json["metadata"]["total_matches"], category_value_list
    else:
        print("Request to get category list for key '{}'.".format(key))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)

def create_category_value(base_url, auth, key, value):
    method = 'PUT'
    url = base_url + "/categories/{}/{}".format(key, value)
    payload = {
        "value": value,
        "description": ""
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
        return True
    else:
        print("Failed to create category value '{}' for key '{}'.".format(value, key))
        print('Status code: {}'.format(resp.status_code))
        print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        exit(1)

def main():
    for key in CATEGORY_KEY_LIST:
        offset = 0
        while True:
            matches, category_value_list = get_category_values(source_base_url, source_pc_auth, key, offset)
            for value in category_value_list:
                #print("key: {} - value: {}".format(key,value))
                create_category_value(dest_base_url, dest_pc_auth, key, value)
            offset += LENGTH
            if (offset > matches):
                break
    offset=0
    try:
        init_contexts()
        create_session()
        total_substrates = len(model.NutanixSubstrate.query(deleted=False))
        while offset < total_substrates:
            for i in model.NutanixSubstrate.query(deleted=False, length=LENGTH, offset=offset):
                if i.spec.categories != "":
                    user_category = json.loads(i.spec.categories)
                    for key in user_category.keys():
                        if key not in CATEGORY_KEY_LIST:
                            create_category(dest_base_url, dest_pc_auth, key)
                        create_category_value(dest_base_url, dest_pc_auth, key, user_category[key])
                        print("key: {} - value: {}".format(key, user_category[key]))
            offset += LENGTH
    except Exception as e:
        log.info("Exception: %s" % e)
        raise

if __name__ == '__main__':
    main()