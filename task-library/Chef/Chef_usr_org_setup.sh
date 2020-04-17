#!/bin/bash
set -ex

##############################################
# Name        : Chef_usr_org_setup.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script is used to configure chef user account.
# Compatibility : Centos 6, 7
##############################################

sudo chef-server-ctl user-create @@{CHEF_USERNAME}@@ @@{FIRST_NAME}@@ @@{MIDDLE_NAME}@@ @@{LAST_NAME}@@ @@{EMAIL}@@ @@{CHEF_PASSWORD}@@
sudo chef-server-ctl org-create @@{CHEF_ORG_NAME}@@ '@@{CHEF_ORG_FULL_NAME}@@' --association_user @@{CHEF_USERNAME}@@
