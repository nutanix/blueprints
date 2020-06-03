    #!/bin/bash

## Disabling SELinux
sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
sudo setenforce 0

## Install icingaweb2 and httpd
sudo yum install -y icingaweb2 icingacli icingaweb2-selinux httpd

## Enable and start httpd service
sudo systemctl start httpd.service
sudo systemctl enable httpd.service

## Enable and start php-fpm service
sudo systemctl start rh-php71-php-fpm.service
sudo systemctl enable rh-php71-php-fpm.service

sudo yum install -y rh-php71-php-pgsql


## Setting up timezone
echo "date.timezone = \"US/Central\" " | sudo tee -a /etc/opt/rh/rh-php71/php.ini


## Setup API user for IcingaWeb2
sudo icinga2 api setup
echo "object ApiUser \"icingaweb2\" {
  password = \"IcingaWeb2\"
  permissions = [ \"status/query\", \"actions/*\", \"objects/modify/*\", \"objects/query/*\" ]
}" | sudo tee /etc/icinga2/conf.d/api-users.conf


sudo systemctl restart rh-php71-php-fpm.service

## Generating Icinga Access token
sudo icingacli setup config directory --group icingaweb2;
sudo icingacli setup token create
