# Oracle - Single Instance

This Nutanix Calm blueprint will deploy Oracle 12 on Oracle Linux 7.

The intention of this blueprint is to show how Nutanix Calm be used to deploy a single instance Oracle database with minimal effort and little to no Oracle-specific knowledge.

While this blueprint must not replace industry best practices with regards to Oracle database design, it can be used as a basis for Oracle deployments from Nutanix Calm.

## Mandatory Requirements Section

This section should be included in all Nutanix Calm blueprints committed to this repository.  For demo or sample blueprints that are not designed to be used in production or "real" environments, high-level information only is required.

- Created on Prism Central 5.6.1.  Tested on all AOS versions from 5.6.1 to 5.8.1
- Minimum hardware requirements: 4x vCPU and 16GB vRAM for Oracle database (x1 if using default values).
- Base disk image required: CentOS Linux 7.  Cloud-Init is not used in this blueprint
- Variables: Oracle VM hostname. Oracle credentials, desired database name, SYS and SYSTEM passwords.
- Credentials: Username and password
- Tested on AHV only but should work the same way on any platform that supports Oracle 7 Linux VMs.  Please be cautious of the licensing requirements re Oracle deployments.
- Minimum # of VMs required: 1
- Actions: Default
- Custom actions: None
- License information: Appropriate Oracle licences will be required, but are beyond the scope of this demo
- Network information: Nutanix environment will require Internet connection for package downloads
- Disks information: Please thoroughly read through the README notes below - important VM image configuration is documented there

## Components

- 1x Oracle Linux 7 VM
- 1x qcow2 disk image containing Oracle installation files ( *do not distribute these* )

## Prerequisites

To deploy this blueprint you will need the following things available.

- This blueprint only.  All settings are contained within the blueprint itself.

## Usage

- Import the blueprint into your Nutanix Calm environment
- Adjust credentials to suit your requirements (the import will warn about blueprint validation errors, since credentials are not saved in exported blueprints)
- Alter all Calm variables to suit your requirements
- Alter the Oracle Linux Calm service/VM so that it connects to your preferred network
- Launch the blueprint
- Fill in all required runtime variables, paying particular attention to the credentials section

## Support

These blueprints are *unofficial* and are not supported or maintained by Nutanix in any way.

In addition, please also be advised that these blueprints may deploy applications that do not follow best practices.  Please check through each blueprint to ensure the configuration suits your requirements.

***Changes will be required before these application blueprints can be used in production environments.***