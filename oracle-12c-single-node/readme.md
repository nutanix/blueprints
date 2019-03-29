# Oracle - Single Node

This Nutanix Calm blueprint will deploy Oracle 12 on Oracle Linux 7.x.

Requires Oracle 7.x qcow2 image under Prism and Oracle source files avaiable for download.

[Deployment video](https://drive.google.com/file/d/1WD-kJenkWa21gPXaZomJ5zUasq5zCBla/view?usp=sharing)

## Mandatory Requirements Section

This section should be included in all Nutanix Calm blueprints committed to this repository.  For demo or sample blueprints that are not designed to be used in production or "real" environments, high-level information only is required.

- Created on Calm 2.6.0.1. Should work on all Prism deployments which supports Calm versions starting from 2.6.0.1.
- Minimum hardware requirements: 8x vCPU and 32GB vRAM for Oracle database (x1 if using default values).
- Base disk image required: Oracle Linux 7.  Cloud-Init is not used in this blueprint
- Variables: Oracle DB Source URL. Oracle SYS and SYSTEM passwords.
- Credentials: Username and password
- Tested on AHV only but should work the same way on any platform that supports Oracle 7 Linux VMs. Please be cautious of the licensing requirements re Oracle deployments.
- Minimum # of VMs required: 1
- Actions: Default
- Custom actions: None
- License information: Appropriate Oracle licences will be required.
- Network information: Nutanix environment will require Internet connection for package downloads
- Disks information:
      -  Boot disk as configured under the Oracle qcow2 Image
      -  2nd disk 50GB  /u01 ( grid home) # For grid deployment only, not used in this blueprint
      -  3rd disk 50 GB /u02. (Oracle home)
      -  4th disk 100 GB DB   (DATA1)
      -  5th disk 100GB  DB.  (DATA2)
      -  6th disk  100GB DB.  (DATA3)
      -  7th disk. 100GB DB.  (DATA4)
      -  8th disk.  100GB RECO (FRA/REDO)
      -  9th disk.   100GB RECO (FRA/REDO)
      -  Swap 22GB

## Components

- 1x Oracle Linux 7 VM

## Prerequisites

To deploy this blueprint you will need the following things available.

- An Oracle Linux qcow2 image which should be uploaded to Images under Prism. The image needs to have a know set of credentials or should be accessible via an existing ssh key.
- Oracle source zip files downloadable from a url

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