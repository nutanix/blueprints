#!/bin/bash
set -ex

##############################################
# Name        : Package_Updates_CentOS.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script is used to update repo/packages of CentOS.
# Compatibility : Centos 6, 7
##############################################

sudo yum update -y
