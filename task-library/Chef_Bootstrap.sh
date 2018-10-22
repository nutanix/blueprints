#!/bin/bash
set -ex

##############################################
# Name        : Chef_Bootstrap.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script is used to bootstrap chef nodes
# Compatibility : Centos 6, 7
##############################################

sudo yum update -y
curl -L https://www.chef.io/chef/install.sh | sudo bash
