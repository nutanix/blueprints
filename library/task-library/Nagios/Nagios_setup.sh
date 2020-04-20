#!/bin/bash
set -ex

##############################################
# Name        : Nagios_setup.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to setup nagios and plugins
# Compatibility : Centos 6, 7
##############################################

sudo yum update -y --quiet
sudo yum install -y epel-release

sudo hostnamectl set-hostname --static @@{name}@@

sudo yum install -y --quiet nagios nagios-plugins-all nagios-plugins-nrpe
