# Nutanix Calm & PHP Composer

This Nutanix Calm blueprint will deploy PHP Composer on an existing CentOS 7 VM.

## Mandatory Requirements Section

This section should be included in all Nutanix Calm blueprints committed to this repository.  For demo or sample blueprints that are not designed to be used in production or "real" environments, high-level information only is required.

- Created on Prism Central 5.6.1.  Tested on all AOS versions from 5.6.1 to 5.8.1
- Minimum hardware requirements: No VMs are deployed by this blueprint - it deploys PHP Composer to an existing CentOS 7 Linux VM only
- Base disk image required: N/A
- Variables: IP address for destination VM
- Credentials: SSH private key for destination VM authentication (by default this assumes the username is 'centos')
- Tested on AHV only but should work the same way on any platform that supports CentOS Linux 7 VMs
- Minimum # of VMs required: 1x existing CentOS Linux 7 VM
- Actions: Default
- Custom actions: None
- License information: No licenses required
- Network information: Nutanix environment will require Internet connection for package downloads
- Disks information: N/A

## Prerequisites

To deploy this blueprint you will need the following things available.

- An existing CentOS 7 Linux VM with PHP *already installed* (the script will verify this)
- An existing CentOS 7 Linux VM with wget *already installed* (the script will verify this)
- An Internet connection from the CentOS 7 Linux VM
- SSH private key for your VM (the blueprint is configured to use SSH key authentication)

## Usage

- Import the blueprint into your Nutanix Calm environment
- Adjust credentials to suit your requirements (the import will warn about blueprint validation errors, since credentials are not saved in exported blueprints)
- Launch the blueprint
- Fill in all required runtime variables, paying particular attention to the existing VM IP address
- After deployment, SSH to the VM and run `composer`

## Support

These blueprints are *unofficial* and are not supported or maintained by Nutanix in any way.

In addition, please also be advised that these blueprints may deploy applications that do not follow best practices.  Please check through each blueprint to ensure the configuration suits your requirements.

***Changes will be required before these application blueprints can be used in production environments.***