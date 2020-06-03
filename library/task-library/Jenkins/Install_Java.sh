#!/bin/bash
set -ex

##############################################
# Name        : Install_Java.sh
# Author      : Nutanix Calm
# Version     : 1.0
# Description : Script is used to install Java
# Compatibility : Centos 7
##############################################

#Install epel release and java
sudo yum install -y epel-release
sudo yum update -y
sudo yum install -y java-1.8.0-openjdk.x86_64
