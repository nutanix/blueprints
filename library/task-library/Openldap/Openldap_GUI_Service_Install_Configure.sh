#!/bin/sh

#Variables used in this script 
SECOND_LEVEL_DOMAIN_NAME="@@{SECOND_LEVEL_DOMAIN_NAME}@@"
OpenLDAPServer_address="@@{OpenLDAPServer.address}@@"

#Yum update and upgrade
sudo yum -y update
sudo yum -y upgrade

#Install required packages
sudo yum -y install net-tools bind-utils bash-completion nano firewalld
sudo echo "yum updates completed!" >> ~/status.txt

#Add firewall rule 
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload

#Set hostname
sudo hostnamectl set-hostname openldap-gui
sudo echo "hostname configured!" >> ~/status.txt

#Install epel repo
sudo yum -y install epel-release
sudo rpm -Uvh https://mirror.webtatic.com/yum/el7/webtatic-release.rpm
sudo yum install -y httpd php56w php56w-mysql

#Enable and restart httpd service 
sudo systemctl restart httpd
sudo systemctl enable httpd

sudo echo "<IfModule mod_dir.c>
        DirectoryIndex index.php index.html index.cgi index.pl index.php index.xhtml index.htm
</IfModule>" | sudo tee /etc/httpd/conf.modules.d/dir.conf

sudo echo "<?php
phpinfo();
?>" | sudo tee /var/www/html/info.php

sudo yum install -y phpldapadmin
sudo sed -i -- 's/Require local/Require all granted/' /etc/httpd/conf.d/phpldapadmin.conf
sudo systemctl restart httpd

#Ldap server configuration 
sudo sed -i -- "s/Local LDAP Server/${SECOND_LEVEL_DOMAIN_NAME} LDAP Server/" /etc/phpldapadmin/config.php
sudo sed -i -- "s/127\.0\.0\.1/${OpenLDAPServer_address}/" /etc/phpldapadmin/config.php
sudo sed -i '298s/\/\/ //' /etc/phpldapadmin/config.php
sudo sed -i '397s/\/\/ //' /etc/phpldapadmin/config.php
sudo sed -i '398s/^/\/\/ /' /etc/phpldapadmin/config.php
sudo setsebool -P httpd_can_connect_ldap on
sudo sed -i -- 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
