#script

#Variables used in this script 
KUBERNETES_CLUSTER_IP=""
API_KEY=""

import kubernetes.client
from kubernetes.client.rest import ApiException

# Configure API key authorization: BearerToken
configuration = kubernetes.client.Configuration()
configuration.host="https://%s:6443" %(KUBERNETES_CLUSTER_IP)
configuration.verify_ssl=False
configuration.api_key['authorization'] = "%s" %(API_KEY)
configuration.api_key_prefix['authorization'] = 'Bearer'

# create an instance of the API class
api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
try:
    api_response = api_instance.list_namespace(watch=False)
    for item in api_response.items:
      print(item.metadata.name)
except ApiException as e:
    print("Exception when calling CoreV1Api->list_namespace: %s\n" % e)
