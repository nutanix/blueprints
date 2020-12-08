#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import requests
import json

from calm.common.flags import gflags

import calm.lib.model as model

from helper import change_project, init_contexts

log = logging.getLogger('category')
logging.basicConfig(level=logging.INFO,
                    format="%(message)s",
                    datefmt='%H:%M:%S')

if 'SOURCE_PC_IP' not in os.environ or 'DEST_PC_IP' not in os.environ:
    raise Exception("Please export 'SOURCE_PC_IP' & 'DEST_PC_IP'.")

SOURCE_PC_IP = os.environ['SOURCE_PC_IP']
DEST_PC_IP = os.environ['DEST_PC_IP']
PC_PORT = 9440
LENGTH = 100

if (
    'SOURCE_PC_USER' not in os.environ or
    'DEST_PC_USER' not in os.environ or
    'SOURCE_PC_PASS' not in os.environ or
    'DEST_PC_PASS' not in os.environ
    ):
    raise Exception("Please export 'SOURCE_PC_USER', 'DEST_PC_USER', 'SOURCE_PC_PASS' &  'DEST_PC_PASS'.")

source_base_url = "https://{}:{}/api/nutanix/v3".format(SOURCE_PC_IP,str(PC_PORT))
dest_base_url = "https://{}:{}/api/nutanix/v3".format(DEST_PC_IP,str(PC_PORT))
source_pc_auth = { "username": os.environ['SOURCE_PC_USER'], "password": os.environ['SOURCE_PC_PASS']}
dest_pc_auth = { "username": os.environ['DEST_PC_USER'], "password": os.environ['DEST_PC_PASS']}

user_categories_list = []

SYS_DEFINED_CATEGORY_KEY_LIST = [
    "CalmApplication",
    "CalmDeployment",
    "CalmService",
    "CalmPackage",
    "OSType",
    "CalmVmUniqueIdentifier",
    "CalmUsername",
    "account_uuid"
]

NON_SYS_DEFINED_CATEGORY_KEY_LIST = [
    "CalmUsername",
    "CalmProject",
    "CalmClusterUuid",
    "CalmUser"
]


headers = {'content-type': 'application/json', 'Accept': 'application/json'}

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
        log.info("Failed to create category key '{}'.".format(key))
        log.info('Status code: {}'.format(resp.status_code))
        log.info('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        raise Exception("Failed to create category key '{}'.".format(key))

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
        log.info("Request to get category list for key '{}'.".format(key))
        log.info('Status code: {}'.format(resp.status_code))
        log.info('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        raise Exception("Request to get category list for key '{}'.".format(key))

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
        log.info("Failed to create category value '{}' for key '{}'.".format(value, key))
        log.info('Status code: {}'.format(resp.status_code))
        log.info('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        raise Exception("Failed to create category value '{}' for key '{}'.".format(value, key))

def main():
    try:
        log.info("Creating System category values")

        for key in SYS_DEFINED_CATEGORY_KEY_LIST + NON_SYS_DEFINED_CATEGORY_KEY_LIST:
            total_matches = 1
            offset = 0
            while offset < total_matches:
                total_matches, category_value_list = get_category_values(source_base_url, source_pc_auth, key, offset)
                if key not in SYS_DEFINED_CATEGORY_KEY_LIST:
                    create_category(dest_base_url, dest_pc_auth, key)
                for value in category_value_list:
                    log.info("Creating key: {} - value: {}".format(key,value))
                    create_category_value(dest_base_url, dest_pc_auth, key, value)
                offset += LENGTH

        log.info("Creating User categories/values")

        offset=0
        init_contexts()
        total_substrates = len(model.NutanixSubstrate.query(deleted=False))
        while offset < total_substrates:
            for i in model.NutanixSubstrate.query(deleted=False, length=LENGTH, offset=offset):
                if i.spec.categories != "":
                    user_category = json.loads(i.spec.categories)
                    for key in user_category.keys():
                        if key not in SYS_DEFINED_CATEGORY_KEY_LIST:
                            create_category(dest_base_url, dest_pc_auth, key)
                        create_category_value(dest_base_url, dest_pc_auth, key, user_category[key])
                        log.info("Creating key: {} - value: {}".format(key, user_category[key]))
            offset += LENGTH
    except Exception as e:
        log.info("Exception: %s" % e)
        raise

if __name__ == '__main__':
    main()