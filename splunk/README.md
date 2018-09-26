# Nutanix Calm & Splunk
# 
This Nutanix Calm blueprint will deploy a Splunk monolithic instance in a VM.  The intention of this BP is to show the how
Monolithic Splunk can be deployed in no time using Calm.

## Mandatory Requirements Section
## 
This section should be included in all Nutanix Calm blueprints committed to this repository.  For demo or sample blueprints that
are not designed to be used in production or "real" environments, high-level information only is required.

- Created on Prism Central 5.8.2.

- Minimum hardware requirements: edit the blueprint to specify the minimum vCPU, memory and disk requirements before publishing.  They are marked as runtime too to enable end users to override if needed 

- Base disk image required: CentOS Linux 7 with Cloud-Init package preinstalled - Download the CentOS 7 Image from
[here](http://download.nutanix.com/calm/CentOS-7-x86_64-GenericCloud-1801-01.qcow2)

 - Variables: 
    + SERVER_NAME
    + INSTANCE_PUBLIC_KEY 
    + SPLUNK_ADMIN_PASSWORD 
    +  SPLUNK_LICENSE 

- Credentials: Your SSH private key - Tested on AHV only but should
work the same way on any platform that supports CentOS Linux 7 VMs 

- Minimum No of VMs required: 1 
 
- Actions: None

- License information: 60 Days free trial included. 

- Network information: Nutanix environment will require Internet
connection for package downloads 

- Disks information: 1x SCSI disk per VM.

## Important Note
## 
The best-practice configuration mentioned through this readme *WILL NOT* be suitable for every environment!

As such, there is no warranty or guarantee offered alongside any configuration deployed as a result of deploying this blueprint.

*Always* make sure you check the scripts and configuration before using open-source blueprints in a production environment.

## Components
## 
- Splunk

## Prerequisites
## 
To deploy this blueprint you will need the following things available.

- A CentOS 7 Linux VM image, published via the Nutanix Image Service - SSH public and private key credentials for your image (note
that this blueprint does not natively use username and password authentication)

## Configuration
## 
The Splunk server in this blueprint has been configured based on a number of best practice recommendations.  The package install
scripts takes care of implementing these best practices at the OS level:

- Disable THP in the VM once it comes up
- Set the file descriptors to 65535
- Set the hostname to the SERVER_NAME specified as input (runtime variable)

The BP then downloads the Splunk 7.1.2 community edition posted on the Splunk website that comes with a 60-day evaluation license.
It installs Splunk in /opt folder from this binary and sets up the initial admin password as the ADMIN_PASSWORD entered by the 
user (runtime variable).  It starts the Splunk server (silent install) with the right folder/user permissions

Note: If you need to choose a different Splunk version, you need to change the blueprint.  You can also look at parameterizing the
Splunk version in the blueprint if needed

## Splunk instance
## 
Once the app launch is successful, you can access splunk instance at http://<IP>:8000.  You can login as admin and the password
you specified under ADMIN_PASSWORD runtime variable

## Usage
## 
- Import the blueprint into your Nutanix Calm environment - Adjust credentials to suit your requirements (the import will warn
about blueprint validation errors, since credentials are not saved in exported blueprints) - Alter the Nginx service so that it
deploys your CentOS 7 image - Launch the blueprint - Fill in all required runtime variables, paying particular attention to the
credentials section 

## Support
## 
These blueprints are *unofficial* and are not supported or maintained by Nutanix in any way.

In addition, please also be advised that these blueprints may deploy applications that do not follow best practices.  Please check
through each blueprint to ensure the configuration suits your requirements.

***Changes will be required before these application blueprints can be used in production environments.***
