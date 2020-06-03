#!/bin/bash
set -ex

##############################################
# Name        : Upgrade_Jenkins.sh
# Author      : Nutanix Calm
# Version     : 1.0
# Description : Script is used to upgrade Jenkins
# Compatibility : Centos 7
##############################################

#Upgrade Jenkins and restart services
sudo yum -y upgrade jenkins
sudo service jenkins restart
