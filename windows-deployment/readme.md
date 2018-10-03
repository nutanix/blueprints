# Windows Deployment

This Nutanix Calm blueprint will deploy a single Windows virtual machine from a Sysprep'd image, join an AD domain then install IIS Services.

The intention of this blueprint is to demonstrate the use of Calm to deploy Windows virtual machines into an enterprise-style environment.  All user-configurable options have been set as 'Calm Variables'.

## Mandatory Requirements Section

This section should be included in all Nutanix Calm blueprints committed to this repository.  For demo or sample blueprints that are not designed to be used in production or "real" environments, high-level information only is required.

- Created on Prism Central 5.9.  Tested on 5.9 only but **should** work on versions from 5.7 onwards (untested!).
- Minimum hardware requirements: 1x vCPU and 4GB vRAM for deployed VM.
- Base disk image required: Windows Server 2016.  This image **must** be Sysprep'd before use!
- Variables: AD domain name, AD credentials, Organisation name, Windows product key and computer name.
- Credentials: Username and password
- Tested on AHV only but should work the same way on any platform that supports Windows VMs
- Minimum # of VMs required: 1
- Actions: Default
- Custom actions: None
- License information: No licenses required for testing
- Network information: No Internet access required for deployment
- Disks information: 1x SCSI disk per VM (x1 total).

## Components

- 1x Windows 2016 VM

## Prerequisites

To deploy this blueprint you will need the following things available.

- An existing, functional and accessible Microsoft Active Directory.
- AD username and password with appropriate permissions for joining PCs to the domain
- New username and password for the deployed VM (configured through Calm blueprint credentials)

## Usage

- Import the blueprint into your Nutanix Calm environment
- Adjust credentials to suit your requirements (the import will warn about blueprint validation errors, since credentials are not saved in exported blueprints)
- Alter each Calm service/VM so that it deploys your Windows 2016 image
- Alter each Calm service/VM so that it connects to your preferred network
- Launch the blueprint
- Fill in all required runtime variables, paying particular attention to the credentials section

## After Deployment

Browse to the IP address of the deployed VM.  A successful deployment will display the default Windows 2016 IIS page

## Support

These blueprints are *unofficial* and are not supported or maintained by Nutanix in any way.

In addition, please also be advised that these blueprints may deploy applications that do not follow best practices.  Please check through each blueprint to ensure the configuration suits your requirements.

***Changes will be required before these application blueprints can be used in production environments.***