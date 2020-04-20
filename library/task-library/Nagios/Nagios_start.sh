#!/bin/bash
set -ex

##############################################
# Name        : Nagios_start.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to start nagios service
# Compatibility : Centos 6, 7
##############################################

sudo systemctl start nagios httpd
sudo systemctl enable nagios httpd
