#!/bin/bash -xe

# -*- Install httpd and php
sudo setenforce 0
sudo sed -i 's/permissive/disabled/' /etc/sysconfig/selinux
sudo yum update -y
sudo yum -y install epel-release
sudo rpm -Uvh https://mirror.webtatic.com/yum/el7/webtatic-release.rpm
sudo yum -y install http://rpms.remirepo.net/enterprise/remi-release-7.rpm
sudo yum-config-manager --enable remi-php56
sudo yum install -y httpd php php-mysql php-fpm php-gd wget unzip

# Enable Apache service
sudo systemctl enable httpd
