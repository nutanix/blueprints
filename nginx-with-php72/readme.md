# Nutanix Calm & Nginx

This Nutanix Calm blueprint will deploy Nginx in preparation for use with a web application.

The intention of this blueprint is to allow quick demonstration of web server deployment during customer presentations.  The installation should take less than 5 minutes.

## Mandatory Requirements Section

This section should be included in all Nutanix Calm blueprints committed to this repository.  For demo or sample blueprints that are not designed to be used in production or "real" environments, high-level information only is required.

- Created on Prism Central 5.6.1.  Tested on all versions up to 5.8.1.
- Minimum hardware requirements: 1x vCPU and 1GB vRAM for the Nginx/PHP VM.
- Base disk image required: CentOS Linux 7 with Cloud-Init package preinstalled
- Variables: Your SSH public key, hostname prefix, Yes/No re enable Nginx Access Log, Static Expiration value (in days) for web server content
- Credentials: Your SSH private key
- Tested on AHV only but should work the same way on any platform that supports CentOS Linux 7 VMs
- Minimum # of VMs required: 1
- Actions: Default
- Custom actions: None
- License information: No licenses required
- Network information: Nutanix environment will require Internet connection for package downloads
- Disks information: 1x SCSI disk per VM (x3 total).

## Important Note

The best-practice configuration mentioned through this readme *WILL NOT* be suitable for every environment!

As such, there is no warranty or guarantee offered alongside any configuration deployed as a result of deploying this blueprint.

*Always* make sure you check the scripts and configuration before using open-source blueprints in a production environment.

## Components

- 1x Nginx server
- PHP 7.2
- CentOS firewall
- PHP Composer

## Prerequisites

To deploy this blueprint you will need the following things available.

- A CentOS 7 Linux VM image, published via the Nutanix Image Service
- SSH public and private key credentials for your image (note that this blueprint does not natively use username and password authentication)

## Configuration

The Nginx server in this blueprint has been configured based on a number of Nginx and PHP-FPM best practice recommendations.  For example:

- Worker processes equal the number of CPU cores
- Worker connections set to 1024
- Gzip compression enabled
- Configurable static file expiration (in days)
- User-defined access log enable/disable
- Client buffers
- Client timeouts
- Keepalive timeout
- Default files removed and basic index.php created
- CGI Pathinfo fix enabled - see [here](https://serverfault.com/questions/627903/is-the-php-option-cgi-fix-pathinfo-really-dangerous-with-nginx-php-fpm)
- PHP security extensions configured - see [here](https://www.digitalocean.com/community/questions/php-fpm-security-limit_extension-issue)

Note: 'client_max_body_size' will need to be increased for sites that accept uploads > 1K in size

In addition, the CentOS 7 firewalld has been installed, enabled and configured to allow access on port 80.

## Site

A default site is created in `/usr/share/nginx/html` (default Nginx site location on CentOS 7).  This will contain an `index.php` file only, plus a vanilla `composer.json` ready for you to customise.  

## Usage

- Import the blueprint into your Nutanix Calm environment
- Adjust credentials to suit your requirements (the import will warn about blueprint validation errors, since credentials are not saved in exported blueprints)
- Alter the Nginx service so that it deploys your CentOS 7 image
- Launch the blueprint
- Fill in all required runtime variables, paying particular attention to the credentials section
- After deployment, browse to the service's IP address on port 80, e.g. http://<service_IP_address>:80

## Support

These blueprints are *unofficial* and are not supported or maintained by Nutanix in any way.

In addition, please also be advised that these blueprints may deploy applications that do not follow best practices.  Please check through each blueprint to ensure the configuration suits your requirements.

***Changes will be required before these application blueprints can be used in production environments.***