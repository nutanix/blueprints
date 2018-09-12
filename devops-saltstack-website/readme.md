# Nutanix Calm & SaltStack 3-tier Website

This Nutanix Calm blueprint will deploy a LEMP stack website, based on Linux, Nginx, MariaDB and PHP

Following the initial deployment, a custom action is available to deploy a PHP application based on the Laravel framework and PHP 7.1.

## Mandatory Requirements Section

This section should be included in all Nutanix Calm blueprints committed to this repository.  For demo or sample blueprints that are not designed to be used in production or "real" environments, high-level information only is required.

- Created on Prism Central 5.6.1.  Tested on all versions up to 5.8.1.
- Minimum hardware requirements: 1x vCPU and 1GB vRAM for SaltStack Master and Minions(x3, minimum - default is 4).
- Base disk image required: CentOS Linux 7 with Cloud-Init package preinstalled
- Variables: Your SSH public key, SaltStack Master, SaltStack Minion hostname prefix, database credentials, web server count
- Credentials: Your SSH private key
- Tested on AHV only but should work the same way on any platform that supports CentOS Linux 7 VMs
- Minimum # of VMs required: 4 if using default values
- Actions: Default
- Custom actions: ApplyDesiredState i.e. deploy git on all SaltStack Minions.  DeployLaravel i.e. deploy Laravel PHP framework.  TestPing i.e. carry out a SaltStack comms test.
- License information: No licenses required
- Network information: Nutanix environment will require Internet connection for package downloads
- Disks information: 1x SCSI disk per VM (x3 total).

## Components

- 1x SaltStack Master
- 1x SaltStack Minion for the MariaDB database server
- At least 1x SaltStack Minion for the Nginx web server(s)
- 1x SaltStack Minion for the HAProxy server

## Prerequisites

To deploy this blueprint you will need the following things available.

- A CentOS 7 Linux VM image, published via the Nutanix Image Service
- Public and private key for your environment (see [Generating SSH Key](https://portal.nutanix.com/#/page/docs/details?targetId=Nutanix-Calm-Admin-Operations-Guide-v10:nuc-generating-private-key-t.html) in the Nutanix documentation)

## Usage

- Import the blueprints into your Nutanix Calm environment
- Adjust credentials to suit your requirements (the import will warn about blueprint validation errors, since credentials are not saved in exported blueprints)
- Alter each Calm service/VM so that it deploys your CentOS 7 image
- Alter each Calm service/VM so that it connects to your preferred network
- Launch the blueprint
- Fill in all required runtime variables, paying particular attention to the SSH key sections
- After deployment, browse to http://<ha_proxy_ip_address>:8080/stats to see the availability of the Nginx web servers 
- After deployment, browse to http://<ha_proxy_ip_address> to access the HAProxy-published application (load-balanced across all deployed web servers)
- After deployment, optionally run the `DeployLaravel` custom action to deploy Laravel on all web servers
- If you have run the `DeployLaravel` custom action, browse to http://<ha_proxy_ip_address> to see the Laravel application
- If you are familiar with Laravel, `php artisan migrate` can be run from the `/usr/share/nginx/html` directory on the web servers (this will run a Laravel migration and prepare the application for use with MariaDB)  

## Support

These blueprints are *unofficial* and are not supported or maintained by Nutanix in any way.

In addition, please also be advised that these blueprints may deploy applications that do not follow best practices.  Please check through each blueprint to ensure the configuration suits your requirements.

***Changes will be required before these application blueprints can be used in production environments.***