#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
import json

from calm.common.flags import gflags

import calm.lib.model as model

from helper import init_contexts, log

from calm.lib.model.store.db import get_insights_db

from calm.lib.proto import AbacEntityCapability

from calm.common.project_util import ProjectUtil

if (
    'DEST_PC_IP' not in os.environ or
    'DEST_PC_USER' not in os.environ or
    'DEST_PC_PASS' not in os.environ or
    'SOURCE_PROJECT_NAME' not in os.environ
):
    raise Exception("Please export 'DEST_PC_IP', 'DEST_PC_USER', 'DEST_PC_PASS' and 'SOURCE_PROJECT_NAME'.")

DEST_PC_IP = os.environ['DEST_PC_IP']
PC_PORT = 9440
LENGTH = 100
DELETED_STATE = 'deleted'
NUTANIX_VM = 'AHV_VM'
SOURCE_PROJECT = os.environ['SOURCE_PROJECT_NAME']

dest_base_url = "https://{}:{}/api/nutanix/v3".format(DEST_PC_IP, str(PC_PORT))
dest_pc_auth = {"username": os.environ['DEST_PC_USER'], "password": os.environ['DEST_PC_PASS']}

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

headers = {'content-type': 'application/json', 'Accept': 'application/json'}

def create_category_key(base_url, auth, key):
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

def get_application_uuids(project_name):

    project_handle = ProjectUtil()

    project_proto = project_handle.get_project_by_name(project_name)

    if not project_proto:
        raise Exception("No project in system with name '{}'".format(project_name))
    project_uuid = str(project_proto.uuid)

    application_uuid_list = []

    db_handle = get_insights_db()
    applications = db_handle.fetch_many(AbacEntityCapability,kind="app",project_reference=project_uuid,select=['kind_id', '_created_timestamp_usecs_'])
    for application in applications:
        application_uuid_list.append(application[1][0])
    
    return application_uuid_list

def create_categories():

    log.info("Creating categories/values")

    init_contexts()
    application_uuid_list = get_application_uuids(SOURCE_PROJECT)
    for app_uuid in application_uuid_list:
        application =  model.Application.get_object(app_uuid)
        if application.state != DELETED_STATE:
            for dep in application.active_app_profile_instance.deployments:
                if dep.substrate.type == NUTANIX_VM:
                    for element in dep.substrate.elements:
                        if element.spec.categories != "":
                            category = json.loads(element.spec.categories)
                            for key in category.keys():
                                if key not in SYS_DEFINED_CATEGORY_KEY_LIST:
                                    create_category_key(dest_base_url, dest_pc_auth, key)
                                log.info("Creating key: {} - value: {}".format(key, category[key]))
                                create_category_value(dest_base_url, dest_pc_auth, key, category[key])

    log.info("Done with creating categories and values")

def main():
    try:
        create_categories()        
    except Exception as e:
        log.info("Exception: %s" % e)
        raise
if __name__ == '__main__':
    main()