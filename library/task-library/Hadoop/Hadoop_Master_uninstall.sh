#!/bin/bash

set -ex

##############################################
# Name        : Hadoop_Master_uninstall.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to uninstall hadoop master 
# Compatibility : Centos 6, 7
##############################################


sudo yum remove -y wget java-1.8.0-openjdk
sudo yum -y remove cloudera-cdh-5-0.x86_64.rpm 
sudo yum -y remove zookeeper-server
sudo yum -y remove hadoop*
