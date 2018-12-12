## Nutanix Cloud Native - Oscar Application
This Calm blueprints deploys a fully functional [Oscar E-Commerce](http://oscarcommerce.com/) application.  It utilizes:
* Nutanix Karbon - Calm provisions Deployments, Services, and Jobs onto a Nutanix Karbon Kubernetes cluster
* Nutanix Era - Calm makes REST API calls into Nutanix Era to provision a production grade PostgreSQL Database
* Nutanix Buckets - Calm utilizes an existing object storage Bucket to store static website content

To use this blueprint, import into a Prism Central running >= Calm 2.4.0, and fill in the Credentials and Variables mentioned below.  Once the Calm Application is running, access the Oscar Application by combining a kubernetes node IP and the port exposed by the oscar-django-service Kubernetes Service.

##### Credentials
* era_creds: the admin account credentials for your Era Server
* db_server_creds: a private key that will allow SSH access to the Era provisioned Database
* buckets_creds: your Nutanix Buckets username and password
* kube_creds: your Karbon Kubernetes admin account and password (needed to create a Job which seeds application data, as Calm Kubernetes support is Tech Preview and a Job is not natively supported)

##### Variables
* era_ip: The IP address of your Era Server
* software_profile: The desired Software Profile of your Postgres DB Server
* compute_profile: The desired Compute Profile of your Postgres DB Server
* network_profile: The desired Network Profile of your Postgres DB Server
* database_parameter: The desired Database Parameters of your Postgres DB
* sla_name: The desired Time Machine SLA of your Posgres DB
* db_name_prefix: The prefix of the name of database (the time stamp will be appended to keep multiple deployments unique)
* db_password: The password for the "postgres" user of the database
* db_public_key: In conjunction with the "db_server_creds", this allows SSH access to the Postgres DB Server
* kube_namespace: The Kubernetes Namespace to deploy onto (must already exist)
* kubemaster_ip: The IP Address of the Kubernetes Master
* buckets_name: The name of the Nutanix Buckets object storage bucket (must already exist)
* buckets_ip: The Nutanix Buckets object storage endpoint IP
