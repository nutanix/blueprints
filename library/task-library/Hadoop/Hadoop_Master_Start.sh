#!/bin/bash

##############################################
# Name        : Hadoop_Master_Start.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to start Hadoop master services
# Compatibility : Centos 6, 7
##############################################

sudo -u hdfs hdfs namenode -format
for x in `cd /etc/init.d ; ls hadoop-hdfs-*` ; do sudo service $x start ; done
sudo -u hdfs hadoop fs -mkdir -p /var/log/hadoop-yarn
sudo -u hdfs hadoop fs -chown yarn:mapred /var/log/hadoop-yarn

#systemctl hadoop-mapreduce-historyserver restart
#systemctl hadoop-yarn-resourcemanager restart
#systemctl hadoop-hdfs-namenode restart
for x in `cd /etc/init.d ; ls hadoop-*` ; do sudo service $x restart ; done

echo "Master service started"

