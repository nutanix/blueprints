#!/bin/bash
set -ex

##############################################
# Name        : Package_Updates_Ubuntu.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script is used to update repo and upgrade packages of Ubuntu.
# Compatibility : Ubuntu 14, 16
##############################################

sudo apt-get -y update &&
sudo apt-get -y upgrade
