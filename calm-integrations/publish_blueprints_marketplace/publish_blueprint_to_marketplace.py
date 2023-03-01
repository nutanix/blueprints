import os, sys, json, re, uuid, time
import logging, argparse
import requests
logging.basicConfig(
        filename='publish_to_marketplace.log',
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

headers = {'content-type': 'application/json', 'Accept': 'application/json'}

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def help_parser():

    parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to vCenter or ESXi')
    parser.add_argument('--pc',
                        required=True,
                        action='store',
                        help='vSphere service to connect to')
    parser.add_argument('--port',
                        type=int,
                        default=9440,
                        action='store',
                        help='Port to connect on')
    parser.add_argument('--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to pc')
    parser.add_argument('--password',
                        required=True,
                        action='store',
                        help='Password to use when connecting to pc')
    parser.add_argument('--blueprint_name',
                        required=True,
                        action='store',
                        help='Blueprint name to be published')
    parser.add_argument('-v', '--version',
                        required=True,
                        action='store',
                        help='Marketplace app version')
    parser.add_argument('-n', '--name',
                        required=True,
                        action='store',
                        help='Marketplace app Name')
    parser.add_argument('-p', '--project',
                        required=True,
                        action='store',
                        help='Projects for marketplace blueprint (used for approving blueprint)')
    parser.add_argument('-i', '--icon',
                        required=True,
                        action='store',
                        help='Marketplace app Icon')
    parser.add_argument('-d', '--description',
                        required=True,
                        action='store',
                        help='Marketplace app description')
    parser.add_argument("--with_secrets", type=str2bool, nargs='?',
                        const=True, default=False,
                        help="Publish with secrets")
    parser.add_argument("--publish_to_marketplace", type=str2bool, nargs='?',
                        const=True, default=False,
                        help="Publish to Marketplace")
    parser.add_argument("--auto_approve", type=str2bool, nargs='?',
                        const=True, default=False,
                        help="Approve from Marketplace manager")
    parser.add_argument("--existing_markeplace_bp", type=str2bool, nargs='?',
                        const=True, default=False,
                        help="Existing marketplace app")
    return parser

### --------------------------------------------------------------------------------- ###
def get_blueprint_uuid(base_url, auth, blueprint_name):
    method = 'POST'
    url = base_url + "/blueprints/list"
    resp = None
    blueprint_uuid = ""
    payload = {
    	"length":100,
    	"offset":0,
    	"filter":"name=={}".format(blueprint_name)
    }
    try:
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )
    except requests.exceptions.ConnectionError as e:
        logging.error("Failed to connect to PC: {}".format(e))
        sys.exit(-1)
    finally:
        if resp.ok:
            json_resp = resp.json()
            if json_resp['metadata']['total_matches'] > 0:
                for bp in json_resp['entities']:
                    if bp["metadata"]["name"] == blueprint_name:
                        return bp["metadata"]["uuid"]
            else:
                logging.error("Not able to find blueprint {}".format(blueprint_name))
                sys.exit(-1)
        else:
            logging.error("Request failed")
            logging.error("Headers: {}".format(headers))
            logging.error('Status code: {}'.format(resp.status_code))
            logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(-1)

### --------------------------------------------------------------------------------- ###
def get_blueprint(base_url, auth, blueprint_uuid):
    method = 'GET'
    url = base_url + "/blueprints/{}/export_json?keep_secrets=true".format(blueprint_uuid)
    resp = None
    try:
        resp = requests.request(
            method,
            url,
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )
    except requests.exceptions.ConnectionError as e:
        logging.error("Failed to connect to PC: {}".format(e))
        sys.exit(-1)
    finally:
        if resp.ok:
            return resp.json()
        else:
            logging.error("Request failed")
            logging.error("Headers: {}".format(headers))
            logging.error('Status code: {}'.format(resp.status_code))
            logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(-1)

### --------------------------------------------------------------------------------- ###
def get_icon_uuid(base_url, auth, icon_name):
    method = 'POST'
    url = base_url + "/app_icons/list"
    app_icon_uuid = None
    payload = {
        "length":100,
        "offset":0
    }
    try:
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )
    except requests.exceptions.ConnectionError as e:
        logging.error("Failed to connect to PC: {}".format(e))
        sys.exit(-1)
    finally:
        if resp.ok:
            json_resp = resp.json()
            if json_resp['metadata']['total_matches'] > 0:
                for icon in json_resp['entities']:
                    if icon["metadata"]["name"] == icon_name:
                        app_icon_uuid = icon["metadata"]["uuid"]
            else:
                logging.error("Not able to find icon {}".format(blueprint_name))
                sys.exit(-1)
            return app_icon_uuid
        else:
            logging.error("Request failed")
            logging.error("Headers: {}".format(headers))
            logging.error('Status code: {}'.format(resp.status_code))
            logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(-1)

### --------------------------------------------------------------------------------- ###
def remove_platform_data(bp_spec):
    for substrate in bp_spec["resources"]["substrate_definition_list"]:
        if substrate['type'] == "VMWARE_VM":
            substrate["create_spec"]["cluster"] = ""
            substrate["create_spec"]["storage_pod"] = ""
            substrate["create_spec"]["host"] = ""
            substrate["create_spec"]["datastore"] = ""
            for nic in substrate["create_spec"]["resources"]["nic_list"]:
                nic["net_name"] = ""
                nic["nic_type"] = ""
        if substrate['type'] == "AHV_VM":
            for disk in substrate["create_spec"]["resources"]["disk_list"]:
                if hasattr(disk, "data_source_reference"):
                    if hasattr(disk["data_source_reference"], 'kind') and disk["data_source_reference"]['kind'] == "image":
                        disk["data_source_reference"]["name"] = ""
                        disk["data_source_reference"]["uuid"] = ""
            for nic in substrate["create_spec"]["resources"]["nic_list"]:
                nic["subnet_reference"]["uuid"] = ""
                nic["subnet_reference"]["name"] = ""
        if substrate["type"] == "AZURE_VM":
            substrate["create_spec"]["resources"]["storage_profile"]["image_details"]["sku"] = ""
            substrate["create_spec"]["resources"]["storage_profile"]["image_details"]["publisher"] = ""
            substrate["create_spec"]["resources"]["storage_profile"]["image_details"]["offer"] = ""
            substrate["create_spec"]["resources"]["storage_profile"]["image_details"]["version"] = ""
            substrate["create_spec"]["resources"]["storage_profile"]["image_details"]["source_image_id"] = ""
            substrate["create_spec"]["resources"]["storage_profile"]["image_details"]["source_image_type"] = ""
            substrate["create_spec"]["resources"]["storage_profile"]["image_details"]["type"] = ""
            #for disk in substrate["create_spec"]["resources"]["storage_profile"]["data_disk_list"]:
            #    disk["lun"] = None
            #    disk["size_in_gb"] = None
            #    disk["name"] = ""
            for nic in substrate["create_spec"]["resources"]["nw_profile"]["nic_list"]:
                nic["nsg_name"] = ""
                nic["vnet_name"] = ""
                nic["subnet_id"] = ""
                nic["nsg_id"] = ""
                nic["private_ip_info"]["ip_address"] = ""
                nic["private_ip_info"]["type"] = ""
                nic["nic_name"] = ""
                nic["subnet_name"] = ""
                nic["vnet_id"] = ""
                nic["type"] = ""
                nic["public_ip_info"] = None
            substrate["create_spec"]["resources"]["resource_group"] = ""
            substrate["create_spec"]["resources"]["hw_profile"]["max_data_disk_count"] = 0
            substrate["create_spec"]["resources"]["hw_profile"]["vm_size"] = ""
            substrate["create_spec"]["resources"]["location"] = ""
            substrate["create_spec"]["resources"]["availability_set_id"] = ""
            substrate["create_spec"]["resources"]["account_uuid"] = ""
    return bp_spec

### --------------------------------------------------------------------------------- ###
def publish_bp_to_marketplace_manager(
    bp_json,
    marketplace_bp_name,
    version,
    description="",
    app_group_uuid=None,
    icon_name=None,
    icon_file=None,
):

    bp_data = bp_json
    bp_status = bp_data["status"]["state"]
    if bp_status != "ACTIVE":
        logging.error("Blueprint is in {} state. Unable to publish it to marketplace manager".format(bp_status))
        sys.exit(-1)

    bp_template = {
        "spec": {
            "name": marketplace_bp_name,
            "description": description,
            "resources": {
                "app_attribute_list": ["FEATURED"],
                "icon_reference_list": [],
                "author": "admin",
                "version": version,
                "app_group_uuid": app_group_uuid or str(uuid.uuid4()),
                "app_blueprint_template": {
                    "status": bp_data["status"],
                    "spec": bp_data["spec"],
                },
            },
        },
        "api_version": "3.0",
        "metadata": {"kind": "marketplace_item"},
    }
    if icon_name:
        app_icon_uuid = get_icon_uuid(base_url, auth, icon_name)
        bp_template["spec"]["resources"]["icon_reference_list"] = [
            {
                "icon_type": "ICON",
                "icon_reference": {"kind": "file_item", "uuid": app_icon_uuid},
            }
        ]
    method = 'POST'
    url = base_url + "/calm_marketplace_items"
    resp = None
    try:
        resp = requests.request(
            method,
            url,
            data=json.dumps(bp_template),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )
    except requests.exceptions.ConnectionError as e:
        logging.error("Failed to connect to PC: {}".format(e))
        sys.exit(-1)
    finally:
        if resp.ok:
            json_resp = resp.json()
            if json_resp["spec"]["resources"]["app_state"] != "PENDING":
                 logging.info("Failed to publish blueprint to Marketplace")
                 sys.exit(-1)
            else:
                return json_resp
        else:
            logging.error("Request failed")
            logging.error("Headers: {}".format(headers))
            logging.error('Status code: {}'.format(resp.status_code))
            logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(-1)

    logging.info("Marketplace Blueprint is published to marketplace manager successfully")

### --------------------------------------------------------------------------------- ###
def get_project_uuid(base_url, auth, project_name):
    method = 'POST'
    url = base_url + "/projects/list"
    payload = {
        "length":100,
        "offset":0,
        "filter":"name=={0}".format(project_name)
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
        json_resp = resp.json()
        if json_resp['metadata']['total_matches'] > 0:
            project = json_resp['entities'][0]
            project_uuid = project["metadata"]["uuid"]
            return project_uuid
        else:
            logging.error("Could not find project")
            sys.exit(-1)
    else:
        logging.error("Request failed")
        logging.error("Headers: {}".format(headers))
        logging.error('Status code: {}'.format(resp.status_code))
        logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
        sys.exit(-1)

### --------------------------------------------------------------------------------- ###
def approve_marketplace_bp(marketplace_json, projects=[], category=None):
    method = 'PUT'
    url = base_url + "/calm_marketplace_items/{}".format(marketplace_json["metadata"]["uuid"])
    resp = None
    marketplace_json["spec"]["resources"]["app_state"] = "ACCEPTED"
    marketplace_json["spec"]["resources"]["project_reference_list"] = projects
    del marketplace_json["status"]
    try:
        resp = requests.request(
            method,
            url,
            data=json.dumps(marketplace_json),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )
    except requests.exceptions.ConnectionError as e:
        logging.error("Failed to connect to PC: {}".format(e))
        sys.exit(-1)
    finally:
        if resp.ok:
            json_resp = resp.json()
            if json_resp["spec"]["resources"]["app_state"] != "ACCEPTED":
                 logging.info("Failed to approve Marketplace Application")
                 sys.exit(-1)
            else:
                return json_resp
        else:
            logging.error("Request failed")
            logging.error("Headers: {}".format(headers))
            logging.error('Status code: {}'.format(resp.status_code))
            logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(-1)

### --------------------------------------------------------------------------------- ###
def publish_marketplace_bp(marketplace_json):
    method = 'PUT'
    url = base_url + "/calm_marketplace_items/{}".format(marketplace_json["metadata"]["uuid"])
    resp = None
    marketplace_json["spec"]["resources"]["app_state"] = "PUBLISHED"
    marketplace_json["metadata"]["spec_version"] = 1

    try:
        resp = requests.request(
            method,
            url,
            data=json.dumps(marketplace_json),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )
    except requests.exceptions.ConnectionError as e:
        logging.error("Failed to connect to PC: {}".format(e))
        sys.exit(-1)
    finally:
        if resp.ok:
            json_resp = resp.json()
            if json_resp["spec"]["resources"]["app_state"] != "PUBLISHED":
                 logging.info("Failed to Publish Marketplace Application")
                 sys.exit(-1)
            else:
                return json_resp
        else:
            logging.error("Request failed")
            logging.error("Headers: {}".format(headers))
            logging.error('Status code: {}'.format(resp.status_code))
            logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(-1)

### --------------------------------------------------------------------------------- ###
def get_app_group_uuid(marketplace_bp_name):
    method = 'POST'
    url = base_url + "/groups"
    app_group_uuid = None
    group = None

    payload = {
      "filter_criteria": "marketplace_item_type_list==APP;app_source==LOCAL;name=={}.*".format(marketplace_bp_name),
      "entity_type": "marketplace_item",
      "group_member_offset": 0,
      "group_member_count": 1,
      "group_count": 64,
      "grouping_attribute": "app_group_uuid",
      "group_member_attributes": [
        {
          "attribute": "name"
        },
        {
          "attribute": "app_group_uuid"
        }
      ],
      "group_member_sort_attribute": "name",
      "group_member_sort_order": "DESCENDING"
    }

    try:
        resp = requests.request(
            method,
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=(auth["username"], auth["password"]),
            verify=False
        )
    except requests.exceptions.ConnectionError as e:
        logging.error("Failed to connect to PC: {}".format(e))
        sys.exit(-1)
    finally:
        if resp.ok:
            json_resp = resp.json()
            if json_resp["filtered_group_count"] != 0:
                for result in json_resp["group_results"]:
                    for data in result["entity_results"][0]["data"]:
                        if data["name"] == "name" and data["values"][0]["values"][0] == marketplace_bp_name:
                            group = result
            else:
                logging.info("Failed to Find exiting Marketplace Application")
            if group != None:
                for data in group["entity_results"][0]["data"]:
                    if data["name"] == "app_group_uuid":
                        app_group_uuid = data["values"][0]["values"][0]
                return app_group_uuid 
            else:
                logging.info("Failed to Find exiting Marketplace Application")
            return app_group_uuid 
        else:
            logging.error("Request failed")
            logging.error("Headers: {}".format(headers))
            logging.error('Status code: {}'.format(resp.status_code))
            logging.error('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
            sys.exit(-1)

### --------------------------------------------------------------------------------- ###
def publish_bp_as_existing_marketplace_bp(
    bp_json,
    marketplace_bp_name,
    version,
    description="",
    publish_to_marketplace=False,
    auto_approve=False,
    projects=[],
    category=None,
    icon_name=None
    ):
    app_group_uuid = get_app_group_uuid(marketplace_bp_name)
    published_json = publish_bp_to_marketplace_manager(bp_json, marketplace_bp_name, version, 
        description=description, app_group_uuid=app_group_uuid, icon_name=icon_name)
    if publish_to_marketplace or auto_approve:
        project_reference_list = []
        for project in projects:
            project_uuid = get_project_uuid(base_url, auth, project)
            project_reference = {"name": project, "kind": "project", "uuid": project_uuid}
            project_reference_list.append(project_reference)

        approved_json = approve_marketplace_bp(
            published_json,
            projects=project_reference_list,
            category=category
        )
        if publish_to_marketplace:
            publish_marketplace_bp(published_json)

if __name__ == "__main__":
    parser = help_parser().parse_args()
    pc_ip = parser.pc
    pc_port = parser.port
    blueprint_name = parser.blueprint_name
    marketplace_bp_name = parser.name
    version = parser.version
    description = parser.description
    project = parser.project
    icon = parser.icon
    auto_approve = parser.auto_approve
    publish_to_marketplace = parser.publish_to_marketplace
    with_secrets = parser.with_secrets
    existing_markeplace_bp = parser.existing_markeplace_bp

    base_url = "https://{}:{}/api/nutanix/v3".format(pc_ip,str(pc_port))
    auth = { "username": parser.user, "password": parser.password}

    blueprint_uuid = get_blueprint_uuid(base_url, auth, blueprint_name)
    blueprint_json = get_blueprint(base_url, auth, blueprint_uuid)
    blueprint_json["spec"] = remove_platform_data(blueprint_json["spec"])
    blueprint_json["status"] = remove_platform_data(blueprint_json["status"])
    publish_bp_as_existing_marketplace_bp(blueprint_json, marketplace_bp_name, 
        version, description=description, publish_to_marketplace=publish_to_marketplace, 
        auto_approve=auto_approve, projects=project.split(','), icon_name=icon)