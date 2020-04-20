#!/bin/bash

set -ex

##############################################
# Name        : Hadoop_Master_setup.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to setup gitlab 
# Compatibility : Centos 6, 7
##############################################


sudo yum update -y
sudo yum install -y wget java-1.8.0-openjdk
curl -O https://archive.cloudera.com/cdh5/one-click-install/redhat/7/x86_64/cloudera-cdh-5-0.x86_64.rpm
sudo yum -y --nogpgcheck localinstall cloudera-cdh-5-0.x86_64.rpm 
sudo rpm --import https://archive.cloudera.com/cdh5/redhat/7/x86_64/cdh/RPM-GPG-KEY-cloudera
sudo yum update -y

sudo yum -y install zookeeper-server
sudo mkdir -p /var/lib/zookeeper
sudo chown -R zookeeper /var/lib/zookeeper/
sudo service zookeeper-server init
sudo service zookeeper-server start
sudo yum -y install hadoop-hdfs-namenode
sudo yum -y install hadoop-client
sudo yum install -y hadoop-yarn-resourcemanager
sudo service zookeeper-server start

echo "Master setup done"
