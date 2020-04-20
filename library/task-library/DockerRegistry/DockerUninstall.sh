#!/bin/bash
set -ex

##############################################
# Name        : DockerUninstall.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script is used to uninstall Docker
# Compatibility : Centos 6, 7
##############################################

sudo yum -y remove docker*
