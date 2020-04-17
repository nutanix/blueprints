#!/bin/bash

##############################################
# Name        : Hadoop_Slave_Start.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to start Hadoop slave services
# Compatibility : Centos 6, 7
##############################################

sudo service hadoop-hdfs-datanode restart
sudo service hadoop-hdfs-secondarynamenode restart
sudo service hadoop-yarn-nodemanager restart

echo "Service started"
