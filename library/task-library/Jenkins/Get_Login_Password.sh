#!/bin/bash
set -ex

##############################################
# Name        : Get_Login_Password.sh
# Author      : Nutanix Calm
# Version     : 1.0
# Description : Script is used to get first time login password for jenkins
# Compatibility : Centos 7
##############################################

#Get auth password from jenkins master
echo "authpwd="$(sudo cat /var/lib/jenkins/secrets/initialAdminPassword)
