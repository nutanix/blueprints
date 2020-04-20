#!/bin/bash
set -ex

##############################################
# Name        : Nagios_uninstall.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to uninstall nagios and plugins
# Compatibility : Centos 6, 7
##############################################


sudo yum remove -y  nagios*
