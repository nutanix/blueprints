#!/bin/bash
set -ex

##############################################
# Name        : Docker_Setup.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script is used to install specified version of docker
# Compatibility : Centos 6, 7
##############################################

sudo hostnamectl set-hostname --static docker-registry
#Install Ntp
sudo yum install -y --quiet ntp openssl 
#Remove any Old docker version
sudo yum remove docker docker-common container-selinux docker-selinux docker-engine
sudo yum install -y --quiet yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y --quiet docker-ce-@@{DOCKER_VERSION}@@

sudo sed -i '/ExecStart=/c\\ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock' /usr/lib/systemd/system/docker.service
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -a -G docker $USER
