#!/bin/bash

sudo yum -y upgrade
sudo curl -O https://dl.fedoraproject.org/pub/epel/7/x86_64/Packages/e/epel-release-7-12.noarch.rpm
sudo rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org
sudo rpm -Uvh http://www.elrepo.org/elrepo-release-7.0-4.el7.elrepo.noarch.rpm 
sudo rpm -ihv epel-release-7-12.noarch.rpm 

sudo yum update -y
sudo yum -y install htop wget iotop xfs* bc unzip lvm2*

sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
sudo setenforce 0

echo "System packages are installed"
