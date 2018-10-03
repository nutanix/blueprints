# Nutanix Calm & SaltStack

These Nutanix Calm blueprints will deploy a simple SaltStack configuration management environment.

## Mandatory Requirements Section

This section should be included in all Nutanix Calm blueprints committed to this repository.  For demo or sample blueprints that are not designed to be used in production or "real" environments, high-level information only is required.

- Created on Prism Central 5.6.1.  Tested on all versions up to 5.9.
- Minimum hardware requirements: 1x vCPU and 1GB vRAM for SaltStack Master.  Same for each Saltstack Minion (x1).
- Base disk image required: CentOS Linux 7 with Cloud-Init package preinstalled
- Variables: Your SSH public key, SaltStack Master, SaltStack Minion hostname prefix
- Credentials: Your SSH private key
- Tested on AHV only but should work the same way on any platform that supports CentOS Linux 7 VMs
- Minimum # of VMs required: 3
- Actions: Default
- Custom actions: ApplyDesiredState i.e. deploy git on all SaltStack Minions
- License information: No licenses required
- Network information: Nutanix environment will require Internet connection for package downloads
- Disks information: 1x SCSI disk per VM (x3 total).

## Components

- 1x SaltStack Master
- 1x VM that acts as a SaltStack Minion (managed by the SaltStack Master)

## Prerequisites

To deploy these blueprints you will need the following things available.

- A CentOS 7 Linux VM image, published via the Nutanix Image Service
- Public and private key for your environment (see [Generating SSH Key](https://portal.nutanix.com/#/page/docs/details?targetId=Nutanix-Calm-Admin-Operations-Guide-v10:nuc-generating-private-key-t.html) in the Nutanix documentation)

## Usage

- Import the blueprint into your Nutanix Calm environment
- Adjust credentials to suit your requirements (the import will warn about blueprint validation errors, since credentials are not saved in exported blueprints)
- Alter each Calm service/VM so that it deploys your CentOS 7 image
- Alter each Calm service/VM so that it connects to your preferred network
- Launch the SaltStack blueprint
- Fill in all required runtime variables
- After deployment, run the custom action 'ApplyDesiredState' custom action
- Check the Calm action output screens to see that all latest packages have been installed via SaltStack state.  The included demo installs 'git' and 'nginx' on all SaltStack Minions and makes sure the 'nginx' service is running.
- After running the 'ApplyDesiredState' action, browse to the IP address of any managed SaltStack Minion.  The default nginx page will be displayed.

## Support

These blueprints are *unofficial* and are not supported or maintained by Nutanix in any way.

In addition, please also be advised that these blueprints may deploy applications that do not follow best practices.  Please check through each blueprint to ensure the configuration suits your requirements.

***Changes will be required before these application blueprints can be used in production environments.***