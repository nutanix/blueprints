#script

#Variables used in this script 
KUBERNETES_CLUSTER_IP=""
API_KEY=""
NAMESPACE_NAME=""


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
body = kubernetes.client.V1Namespace() # V1Namespace | 
body.metadata = kubernetes.client.V1ObjectMeta(name="%s" %(NAMESPACE_NAME))
try:
    api_response = api_instance.create_namespace(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CoreV1Api->create_namespace: %s\n" % e)
