cloud = get_cloud()

client = cloud.nutanix.GenesisApiClient('@@{address}@@', 9440, auth_mode='basic', username='@@{default_cred.username}@@', password='@@{default_cred.secret}@@')
service_list = ['AossServiceManagerService']
client.enable_service(service_list)