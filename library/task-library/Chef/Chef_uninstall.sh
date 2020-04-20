#!/bin/bash
set -ex

##############################################
# Name        : Uninstall_chef.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to uninstall chef
# Compatibility : Centos 6, 7
###############################################

sudo yum -y remove chef*
ps -ef | grep -i chef | grep -v grep | awk '{print "sudo kill -9 " $2}' 
