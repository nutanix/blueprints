#!/bin/bash
set -ex

##############################################
# Name        : Gitlab_setup.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to setup gitlab 
# Compatibility : Centos 6, 7
##############################################

GITLAB_DNS_NAME="@@{GITLAB_DNS_NAME}@@"

sudo yum install -y curl policycoreutils-python openssh-server postfix 

sudo systemctl start postfix
sudo systemctl enable postfix
sudo systemctl status postfix

curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.rpm.sh | sudo bash

sudo yum install -y gitlab-ce
if [[ "${GITLAB_DNS_NAME}x" != "x" ]]; then 
  sudo sed -i "s#external_url 'http://gitlab.example.com'#external_url 'http://${GITLAB_DNS_NAME}'#" /etc/gitlab/gitlab.rb
fi
sudo gitlab-ctl reconfigure
