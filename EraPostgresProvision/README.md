## Era PosgreSQL Database Provisioning
This Calm blueprint deploys a production grade PostgreSQL database by calling Nutanix Era APIs. With the 2018-02-10 update, a minimum of Era Version 1.0.1 is required.

To use this blueprint, import into a Prism Central running >= Calm 2.5.0.1, and fill in the Credentials and Variables mentioned below.

##### Credentials
* era_creds: the admin account credentials for your Era Server
* db_server_creds: a private key that will allow SSH access to the Era provisioned Database

##### Variables
* era_ip: The IP address of your Era Server
* software_profile: The desired Software Profile of your Postgres DB Server
* compute_profile: The desired Compute Profile of your Postgres DB Server
* network_profile: The desired Network Profile of your Postgres DB Server
* database_parameter: The desired Database Parameters of your Postgres DB
* sla_name: The desired Time Machine SLA of your Posgres DB
* db_name: The name of database (be sure to keep this value unique within Era)
* db_password: The password for the "postgres" user of the database
* db_public_key: In conjunction with the "db_server_creds", this allows SSH access to the Postgres DB Server
