#!/bin/bash

##############################################
# Name        : Configure_Hadoop_Slave.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to configure slave with master details 
# Compatibility : Centos 6, 7
##############################################

set -ex
sudo cp -r /etc/hadoop/conf.empty /etc/hadoop/conf.my_cluster
sudo alternatives --install /etc/hadoop/conf hadoop-conf /etc/hadoop/conf.my_cluster 50
sudo alternatives --set hadoop-conf /etc/hadoop/conf.my_cluster

sudo mkdir -p /data/1/dfs/dn /data/2/dfs/dn /data/3/dfs/dn /data/4/dfs/dn
sudo chown -R hdfs:hdfs /data/1/dfs/dn /data/2/dfs/dn /data/3/dfs/dn /data/4/dfs/dn
sudo mkdir -p /data/1/yarn/local /data/2/yarn/local /data/3/yarn/local /data/4/yarn/local
sudo mkdir -p /data/1/yarn/logs /data/2/yarn/logs /data/3/yarn/logs /data/4/yarn/logs
sudo chown -R yarn:yarn /data/1/yarn/local /data/2/yarn/local /data/3/yarn/local /data/4/yarn/local
sudo chown -R yarn:yarn /data/1/yarn/logs /data/2/yarn/logs /data/3/yarn/logs /data/4/yarn/logs

sudo mv /etc/hadoop/conf/hdfs-site.xml /etc/hadoop/conf/hdfs-site.xml.backup
sudo mv /etc/hadoop/conf/core-site.xml /etc/hadoop/conf/core-site.xml.backup
sudo mv /etc/hadoop/conf/mapred-site.xml /etc/hadoop/conf/mapred-site.xml.backup
sudo mv /etc/hadoop/conf/yarn-site.xml /etc/hadoop/conf/yarn-site.xml.backup

### Configure hdfs-site.xml
hdfs_site_xml=$(cat <<EOF
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
<property><name>dfs.permissions.superusergroup</name><value>hadoop</value></property>
<property><name>dfs.namenode.name.dir</name><value>file:///data/1/dfs/nn,file:///nfsmount/dfs/nn</value></property>
<property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///data/1/dfs/dn,file:///data/2/dfs/dn,file:///data/3/dfs/dn,file:///data/4/dfs/dn</value>
</property>
<property>
    <name>dfs.namenode.http-address</name>
    <value>#@#IPADDRESS#@#:50070</value>
    <description>The address and the base port on which the dfs NameNode Web UI will listen.</description>
</property>
<property><name>dfs.namenode.datanode.registration.ip-hostname-check</name><value>false</value></property>  
</configuration>
EOF
)
echo $hdfs_site_xml | sudo tee /etc/hadoop/conf/hdfs-site.xml
sudo sed -i -e 's/#@#IPADDRESS#@#/@@{Hadoop_Master.address}@@/g' /etc/hadoop/conf/hdfs-site.xml

### Configure core-site.xml
core_site_xml=$(cat <<EOF
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
<property><name>fs.defaultFS</name><value>hdfs://#@#IPADDRESS#@#</value></property>
<property><name>hadoop.proxyuser.mapred.groups</name><value>*</value></property>
<property><name>hadoop.proxyuser.mapred.hosts</name><value>*</value></property>
</configuration>
EOF
)
echo $core_site_xml | sudo tee /etc/hadoop/conf/core-site.xml
sudo sed -i -e 's/#@#IPADDRESS#@#/@@{Hadoop_Master.address}@@/g' /etc/hadoop/conf/core-site.xml

### Configure mapred-site.xml
mapred_site_xml=$(cat <<EOF
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
<property><name>mapreduce.framework.name</name><value>yarn</value></property>
<property><name>yarn.app.mapreduce.am.staging-dir</name><value>/user</value></property>
<property><name>mapreduce.jobhistory.address</name><value>@#IPADDRESS#@#:10020</value></property>
<property><name>mapreduce.jobhistory.webapp.address</name><value>#@#IPADDRESS#@#:19888</value></property>
</configuration>
EOF
)
echo $mapred_site_xml | sudo tee /etc/hadoop/conf/mapred-site.xml
sudo sed -i -e 's/#@#IPADDRESS#@#/@@{Hadoop_Master.address}@@/g' /etc/hadoop/conf/mapred-site.xml


### Configure yarn-site.xml
yarn_site_xml=$(cat <<EOF
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
  <property>
    <name>yarn.nodemanager.aux-services.mapreduce_shuffle.class</name>
    <value>org.apache.hadoop.mapred.ShuffleHandler</value>
  </property>
  <property>
    <name>yarn.log-aggregation-enable</name>
    <value>true</value>
  </property>
  <property>
    <description>Where to store container logs.</description>
    <name>yarn.nodemanager.log-dirs</name>
    <value>file:///var/log/hadoop-yarn/containers</value>
  </property>
  <property>
    <description>Where to aggregate logs to.</description>
    <name>yarn.nodemanager.remote-app-log-dir</name>
    <value>hdfs://var/log/hadoop-yarn/apps</value>
  </property>
  <property>
    <description>Classpath for typical applications.</description>
     <name>yarn.application.classpath</name>
     <value>
        \$HADOOP_CONF_DIR,
        \$HADOOP_COMMON_HOME/*,\$HADOOP_COMMON_HOME/lib/*,
        \$HADOOP_HDFS_HOME/*,\$HADOOP_HDFS_HOME/lib/*,
        \$HADOOP_MAPRED_HOME/*,\$HADOOP_MAPRED_HOME/lib/*,
        \$HADOOP_YARN_HOME/*,\$HADOOP_YARN_HOME/lib/*
     </value>
  </property>
  <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>#@#IPADDRESS#@#</value>
  </property>
  <property>
    <name>yarn.nodemanager.local-dirs</name>
    <value>file:///data/1/yarn/local,file:///data/2/yarn/local,file:///data/3/yarn/local</value>
  </property>
</configuration>
EOF
)
echo $yarn_site_xml | sudo tee /etc/hadoop/conf/yarn-site.xml
sudo sed -i -e 's/#@#IPADDRESS#@#/@@{Hadoop_Master.address}@@/g' /etc/hadoop/conf/yarn-site.xml

echo "Slave @@{address}@@ configured"

