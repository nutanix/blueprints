# region headers
# escript-template v20190611 / stephane.bourdeaud@nutanix.com
# * author:     MITU Bogdan Nicolae (EEAS-EXT) <Bogdan-Nicolae.MITU@ext.eeas.europa.eu>
# * version:    2019/09/17
# task_name:    CalmSetProjectAcp
# description:  Configures the Access Control Policy on a Calm project, which
#               will effectively define user and group permissions on that 
#               project.
# endregion

#region capture Calm variables
username = "@@{pc.username}@@"
username_secret = "@@{pc.secret}@@"
api_server = "@@{pc_ip}@@"
calm_user_uuid = "@@{nutanix_calm_user_uuid}@@"
calm_user_upn = "@@{calm_username}@@"
ad_group_name = "@@{ad_group_name}@@"
ad_group_uuid = "@@{ad_group_uuid}@@"
ad_group_dn = "@@{ad_group_dn}@@"
project_admin_role_uuid = "@@{project_admin_role_uuid}@@"
developer_role_uuid = "@@{developer_role_uuid}@@"
consumer_role_uuid = "@@{consumer_role_uuid}@@"
project_uuid = "@@{project_uuid}@@"
directory_uuid = "@@{directory_uuid}@@"
nutanix_cluster_uuid = "@@{nutanix_cluster_uuid}@@"
#endregion

#region prepare api call (get project)
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/projects_internal/{}".format(project_uuid)
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "GET"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
#endregion

#region make the api call (get project)
print("Making a {} API call to {}".format(method, url))
resp = urlreq(
    url,
    verb=method,
    auth='BASIC',
    user=username,
    passwd=username_secret,
    headers=headers,
    verify=False
)
# endregion

#region process the results (get project)
if resp.ok:
   print("Successfully retrieved project details for project with uuid {}".format(project_uuid))
   project_json = json.loads(resp.content)
else:
    #api call failed
    print("Request failed")
    print("Headers: {}".format(headers))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
# endregion

#region prepare api call (update project with acp)
api_server_port = "9440"
api_server_endpoint = "/api/nutanix/v3/projects_internal/{}".format(project_uuid)
url = "https://{}:{}{}".format(
    api_server,
    api_server_port,
    api_server_endpoint
)
method = "PUT"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Compose the json payload
if len(str(project_json['spec']['access_control_policy_list'])) > 2:
    print "ACP is not null"
    exit (1)
else:
    print "ACP is null"
    #removing stuff we don't need for the update
    project_json['metadata'].pop('owner_reference', None)
    project_json.pop('status', None)
    project_json['metadata'].pop('create_time', None)
    #region adding group information
    add_acp_group = {
                "operation": "ADD",
                "acp": {
                    "name": "nuCalmAcp-"+str(uuid.uuid4()),
                    "resources": {
                        "role_reference": {
                            "kind": "role",
                            "uuid": consumer_role_uuid
                        },
                        "user_reference_list": [],
                        "filter_list": {
                            "context_list": [
                                {
                                    "entity_filter_expression_list": [
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "ALL"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        }
                                    ],
                                    "scope_filter_expression_list": [
                                        {
                                            "operator": "IN",
                                            "left_hand_side": "PROJECT",
                                            "right_hand_side": {
                                                "uuid_list": [
                                                    project_uuid
                                                ]
                                            }
                                        }
                                    ]
                                },
                                {
                                    "entity_filter_expression_list": [
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "image"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "marketplace_item"
                                            },
                                            "right_hand_side": {
                                                "collection": "SELF_OWNED"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "app_icon"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "category"
                                            },
                                            "right_hand_side": {
                                                "collection": "ALL"
                                            }
                                        },
                                        {
                                            "operator": "IN",
                                            "left_hand_side": {
                                                "entity_type": "cluster"
                                            },
                                            "right_hand_side": {
                                                "uuid_list": [
                                                    nutanix_cluster_uuid
                                                ]
                                            }
                                        }
                                    ]
                                }
                            ]
                        },
                        "user_group_reference_list": [
                        {
                            "kind": "user_group",
                            "uuid": ad_group_uuid
                        }
                        ]
                    },
                    "description": "ACPDescription-"+str(uuid.uuid4())
                },
                "metadata": {
                    "kind": "access_control_policy"
                }
            }
    project_json['spec']['access_control_policy_list'].append(add_acp_group)
    add_group = {
        "kind": "user_group",
        "uuid": ad_group_uuid
    }
    project_json['spec']['project_detail']['resources']['external_user_group_reference_list'].append(add_group)
    spec_addgroup = {
            "metadata": {
                "kind": "user_group",
                "uuid": ad_group_uuid
            },
            "user_group": {
                "resources": {
                    "directory_service_user_group": {
                        "distinguished_name": ad_group_dn
                    }
                }
            },
            "operation": "ADD"
    }
    project_json['spec']['user_group_list'].append(spec_addgroup)
    #endregion
    #region adding user information
    add_acp_user = {
        "operation": "ADD",
        "acp": {
            "name": "nuCalmAcp-"+str(uuid.uuid4()),
            "resources": {
                "role_reference": {
                    "kind": "role",
                    "uuid": project_admin_role_uuid
                },
                "user_reference_list": [
                    {
                        "kind": "user",
                        "uuid": calm_user_uuid
                    }
                ],
                "filter_list": {
                    "context_list": [
                        {
                            "entity_filter_expression_list": [
                                {
                                    "operator": "IN",
                                    "left_hand_side": {
                                        "entity_type": "ALL"
                                    },
                                    "right_hand_side": {
                                        "collection": "ALL"
                                    }
                                }
                            ],
                            "scope_filter_expression_list": [
                                {
                                    "operator": "IN",
                                    "left_hand_side": "PROJECT",
                                    "right_hand_side": {
                                        "uuid_list": [
                                            project_uuid
                                        ]
                                    }
                                }
                            ]
                        },
                        {
                            "entity_filter_expression_list": [
                                {
                                    "operator": "IN",
                                    "left_hand_side": {
                                        "entity_type": "image"
                                    },
                                    "right_hand_side": {
                                        "collection": "ALL"
                                    }
                                },
                                {
                                    "operator": "IN",
                                    "left_hand_side": {
                                        "entity_type": "marketplace_item"
                                    },
                                    "right_hand_side": {
                                        "collection": "SELF_OWNED"
                                    }
                                },
                                {
                                    "operator": "IN",
                                    "left_hand_side": {
                                        "entity_type": "app_icon"
                                    },
                                    "right_hand_side": {
                                        "collection": "ALL"
                                    }
                                },
                                {
                                    "operator": "IN",
                                    "left_hand_side": {
                                        "entity_type": "category"
                                    },
                                    "right_hand_side": {
                                        "collection": "ALL"
                                    }
                                },
                                {
                                    "operator": "IN",
                                    "left_hand_side": {
                                        "entity_type": "cluster"
                                    },
                                    "right_hand_side": {
                                        "uuid_list": [
                                            nutanix_cluster_uuid
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                },
                "user_group_reference_list": []
            },
            "description": "ACPDescription-"+str(uuid.uuid4())
        },
        "metadata": {
            "kind": "access_control_policy"
        }
    }
    project_json['spec']['access_control_policy_list'].append(add_acp_user)
    add_user = {
        "kind": "user",
        "uuid": calm_user_uuid
    }
    project_json['spec']['project_detail']['resources']['user_reference_list'].append(add_user)
    spec_adduser = {
        "metadata": {
            "kind": "user",
            "uuid": calm_user_uuid
        },
        "user": {
            "resources": {
                "directory_service_user": {
                    "directory_service_reference": {
                        "kind": "directory_service",
                        "uuid": directory_uuid
                    },
                    "user_principal_name": calm_user_upn
                }
            }
        },
        "operation": "ADD"
    }
    project_json['spec']['user_list'].append(spec_adduser)
    #endregion
payload = project_json
#endregion

#region make the api call (update project with acp)
print("Making a {} API call to {}".format(method, url))
resp = urlreq(
    url,
    verb=method,
    auth='BASIC',
    user=username,
    passwd=username_secret,
    params=json.dumps(payload),
    headers=headers,
    verify=False
)
#endregion

#region process the results (update project with acp)
if resp.ok:
    print("Successfully updated the project with uuid {}".format(project_uuid))
    exit(0)
else:
    #api call failed
    print("Request failed")
    print("Headers: {}".format(headers))
    print("Payload: {}".format(json.dumps(payload)))
    print('Status code: {}'.format(resp.status_code))
    print('Response: {}'.format(json.dumps(json.loads(resp.content), indent=4)))
    exit(1)
#endregion