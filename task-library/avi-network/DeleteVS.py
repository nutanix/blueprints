# script
# region headers
# * author:     salaheddine.gassim@nutanix.com
# * version:    14082019
# task_name:    DeleteVS
# description:  this task is used to delete a virtual service and optionally it's pool
# endregion

controller_url = "@@{CONTROLLER_URL}@@"


def delete_virtual_service(controller_url, vs_uuid, pool_uuid="@@{POOL_UUID}@@", delete_pool=True):
    """ This function a virtual service and it's corresponding pool 
        Args:
         controller_url: http://avi_controller_ip
         vs_uuid: uuid of the virtual service to be deleted
         delete_pool: if True, we delete the virtual service and the corresponding pool
         pool_uuid: uuid of the pool to be deleted
        Returns:
         print the REST api call result

    """

    # setting up header
    h_api_version = "@@{API_VERSION}@@"
    h_encoding = "@@{ENCODING}@@"
    h_content = "@@{CONTENT}@@"
    h_sessionid = "@@{SESSION_ID}@@"
    h_csrftoken = "@@{CSRF_TOKEN}@@"
    h_referer = "@@{REFERER}@@"
    # enpoint for deleting objects
    vs_delete_endpoint = "/api/virtualservice/"
    pool_delete_endpoint = "/api/pool/"

    headers = {
        'cookie': "csrftoken=" + h_csrftoken + "; sessionid=" + h_sessionid,
        'X-Avi-Version': h_api_version,
        'Accept-Encoding': h_encoding,
        'Content-type': h_content,
        'Referer': h_referer,
        'X-CSRFToken': h_csrftoken
    }

    # endregion
    # request for deleting the virtual service
    endpoint_url = controller_url + vs_delete_endpoint + vs_uuid
    response = urlreq(endpoint_url, verb='DELETE',
                      headers=headers, verify=False)

    # deal with the result/response
    if response.ok:
        print "Virtual service was successfully deleted"

    else:
        print("Request failed")
        print("Headers: {}".format(headers))
        print('Status code: {}'.format(response.status_code))
        print('Response: {}'.format(response.text))
        exit(1)

    # endregion

    # delete the pool that was memeber of this virtual service by default
    if delete_pool:
        # request for deleting the pool
        endpoint_url = controller_url + pool_delete_endpoint + pool_uuid
        response = urlreq(endpoint_url, verb='DELETE',
                          headers=headers, verify=False)

        # deal with the result/response
        if response.ok:
            print "Pool was successfully deleted"

        else:
            print("Request failed")
            print("Headers: {}".format(headers))
            print('Status code: {}'.format(response.status_code))
            print('Response: {}'.format(response.text))
            exit(1)

delete_virtual_service(controller_url, "@@{VS_UUID}@@",
                       "@@{POOL_UUID}@@", delete_pool=True)
