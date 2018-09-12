# Nutanix Calm & OpenLDAP

This Nutanix Calm blueprint will deploy OpenLDAP in preparation for use with a Nutanix cluster.

The intention of this blueprint is to allow customers testing of OpenLDAP, a common alternative to Active Directory.

## Mandatory Requirements Section

This section should be included in all Nutanix Calm blueprints committed to this repository.  For demo or sample blueprints that are not designed to be used in production or "real" environments, high-level information only is required.

- Created on Prism Central 5.6.1.  Tested on all AOS versions from 5.6.1 to 5.8.1
- Minimum hardware requirements: 1x vCPU and 1GB vRAM for destination/deployed VMs (x3 if using default values).
- Base disk image required: CentOS Linux 7.  Cloud-Init is not used in this blueprint
- Variables: OpenLDAP admin credentials.  SSL certificate properties.  Read-only user credentials (will be created at runtime).
- Credentials: Username and password
- Tested on AHV only but should work the same way on any platform that supports CentOS Linux 7 VMs
- Minimum # of VMs required: 3 if using default values.
- Actions: Default
- Custom actions: CreateLDAPUser - create an OpenLDAP user based on blueprint variables.  DeleteLDAPUser - delete user created by CreateLDAPUser action.
- License information: No licenses required
- Network information: Nutanix environment will require Internet connection for package downloads
- Disks information: 1x SCSI disk per VM (x1 total).

## Components

- 1x OpenLDAP server
- 1x CentOS 7 Linux VM configured to authenticate against the new OpenLDAP directory
- 1x web server hosting phpLDAPAdmin, a web-based GUI for OpenLDAP management

*Note: ntnxdemo.local is hard-coded as the domain, for now*

## Prerequisites

To deploy this blueprint you will need the following things available.

- A CentOS 7 Linux VM image, published via the Nutanix Image Service
- Username and password for your Linux image (note that this blueprint does not natively use of public/private key authentication)

## Usage

- Import the blueprint into your Nutanix Calm environment
- Adjust credentials to suit your requirements (the import will warn about blueprint validation errors, since credentials are not saved in exported blueprints)
- Alter each Calm service/VM so that it deploys your CentOS 7 image
- Alter each Calm service/VM so that it connects to your preferred network
- Launch the blueprint
- Fill in all required runtime variables, paying particular attention to the credentials section
- After deployment, connect to the deployed Linux client and login with the credentials supplied during deployment
- Configure Prism and/or Prism Central Authentication, as per the next section

## phpLDAPAdmin

- To use the GUI OpenLDAP admin app, browse to `http://<phpldapadmin_server_ip_address>/phpldapadmin`
- Enter `cn=ldapadm,dc=ntnxdemo,dc=local` for the Login DN
- Enter the OPENLDAP_PASSWORD that was provided during blueprint launch
- Click `Authenticate`

## Nutanix Authentication

To setup Nutanix Prism or Prism Central to authenticate via OpenLDAP, follow the steps below.

### Directory

- From Prism or Prism Central, click the gear icon and select `Authentication`
- Select `New Directory` and set the type to `OpenLDAP`

For each field, use settings similar to the following:

- Name: The display name for the OpenLDAP directory
- Domain: The domain name, `ntnxdemo.local` in this case
- Directory URL: `ldap://<openldap_server_ip_address>:389`
- User Object Class: `account`
- User Search Base: `ou=People,dc=ntnxdemo,dc=local`
- Username Attribute: `uid`
- Group Object Class: `posixgroup`
- Group Search Base: `ou=Group,dc=ntnxdemo,dc=local`
- Group Member Attribute: `memberUid`
- Group Member Attribute Value: `uid`
- Service Account Username: `cn=ldapadm,dc=ntnxdemo,dc=local`
- Service Account Password: `<OPENLDAP_PASSWORD>` as entered during blueprint launch

### Roles

- From Prism or Prism Central, click the gear icon and select Role Mapping
- Click `New Mapping`
- Select your new directory from the Directory dropdown
- Select the type of authentication (for this environment it is recommended to select `group`)
- Select the role (for this environment it is recommended to select `Cluster Admin` the first time)
- Enter the OpenLDAP group name to associate with this role (in this blueprint, preconfigured groups called `ClusterAdmin` and `Viewer` are available)
- Repeat the Roles steps above to create a role for the unused group

## Support

These blueprints are *unofficial* and are not supported or maintained by Nutanix in any way.

In addition, please also be advised that these blueprints may deploy applications that do not follow best practices.  Please check through each blueprint to ensure the configuration suits your requirements.

***Changes will be required before these application blueprints can be used in production environments.***