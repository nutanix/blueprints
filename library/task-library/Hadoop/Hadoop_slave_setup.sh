#!/bin/bash

set -ex

##############################################
# Name        : Hadoop_slave_setup.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to setup Hadoop 
# Compatibility : Centos 6, 7
##############################################


sudo yum update -y
sudo yum install -y wget java-1.8.0-openjdk

curl -O https://archive.cloudera.com/cdh5/one-click-install/redhat/7/x86_64/cloudera-cdh-5-0.x86_64.rpm
sudo yum -y --nogpgcheck localinstall cloudera-cdh-5-0.x86_64.rpm 
sudo rpm --import https://archive.cloudera.com/cdh5/redhat/7/x86_64/cdh/RPM-GPG-KEY-cloudera
sudo yum update -y

sudo yum -y install hadoop-hdfs-secondarynamenode
#yum -y install hadoop-yarn-resourcemanager
sudo yum -y install hadoop-yarn-nodemanager hadoop-hdfs-datanode hadoop-mapreduce
sudo yum -y install hadoop-client
sudo systemctl stop hadoop-hdfs-secondarynamenode
#sudo systemctl stop hadoop-yarn-resourcemanager
sudo systemctl stop hadoop-yarn-nodemanager 
sudo systemctl stop hadoop-hdfs-datanode
#sudo systemctl stop hadoop-mapreduce

echo "Slave Setup Done"
