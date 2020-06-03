#!/bin/bash
set -ex

##############################################
# Name        : Install_Jenkins.sh
# Author      : Nutanix Calm
# Version     : 1.0
# Description : Script is used to bootstrap Jenkins
# Compatibility : Centos 7
##############################################

# - * - Variables and constants.
JENKINS_VERSION="@@{JENKINS_VERSION}@@"
INSTALL_BLUEOCEAN="@@{INSTALL_BLUEOCEAN}@@"

#Import jenkins-ci rpm and install jenkins
sudo rpm --import http://pkg.jenkins-ci.org/redhat-stable/jenkins-ci.org.key
sudo curl -o /etc/yum.repos.d/jenkins.repo http://pkg.jenkins-ci.org/redhat-stable/jenkins.repo
sudo yum install -y jenkins-${JENKINS_VERSION}
sudo systemctl enable jenkins

#Download script to install plugins
sudo yum -y install unzip
sudo curl -o batch-install-jenkins-plugins.sh https://gist.githubusercontent.com/micw/e80d739c6099078ce0f3/raw/33a21226b9938382c1a6aa68bc71105a774b374b/install_jenkins_plugin.sh
sudo chmod +x batch-install-jenkins-plugins.sh

#Copy required plugins
echo 'credentials-binding
windows-slaves
ssh-credentials
ssh-slaves
credentials
plain-credentials
credentials-binding
authentication-tokens
nutanix-calm
pam-auth
script-security
cloudbees-folder
cloudbees-credentials' | sudo tee plugins

#Add Blue Ocean if selected by user
if [[ "${INSTALL_BLUEOCEAN}" == "yes" ]];then
  echo 'blueocean' | sudo tee -a plugins
fi

#Install plugins
sudo mkdir -p /var/lib/jenkins/plugins
sudo ./batch-install-jenkins-plugins.sh $(echo $(cat plugins))
sudo systemctl start jenkins
sleep 60
