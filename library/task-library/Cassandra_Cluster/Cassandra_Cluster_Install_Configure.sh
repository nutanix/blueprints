#!/bin/sh

#Variables used in this script 
SEEDS="@@{calm_array_address}@@"
LISTEN_ADDRESS="@@{address}@@"
DATA_PATH="@@{DATA_PATH}@@"

#Install cassandra from yum
echo "[datastax] 
name = DataStax Repo for Apache Cassandra
baseurl = http://rpm.datastax.com/community
enabled = 1
gpgcheck = 0" | sudo tee -a /etc/yum.repos.d/datastax.repo
sudo yum install -y dsc30
sudo yum install -y cassandra30-tools

#Stop firewalld  
sudo yum install firewalld -y 
sudo systemctl disable firewalld
sudo systemctl stop firewalld

#Configure cassandra 
sudo service cassandra stop
rm -rf /var/lib/cassandra/data/system/*
sudo sed -i 's/cluster_name: \x27Test Cluster\x27/cluster_name: \x27@@{CLUSTER_NAME}@@\x27/' /etc/cassandra/conf/cassandra.yaml
sudo sed -i "s|- seeds: \"127.0.0.1\"|- seeds: \"${SEEDS}\"|" /etc/cassandra/conf/cassandra.yaml
sudo sed -i "s|listen_address: localhost|listen_address: ${LISTEN_ADDRESS}|" /etc/cassandra/conf/cassandra.yaml
sudo sed -i 's/rpc_address: localhost/rpc_address: \x27127.0.0.1\x27/' /etc/cassandra/conf/cassandra.yaml
sudo sed -i 's/endpoint_snitch: SimpleSnitch/endpoint_snitch: GossipingPropertyFileSnitch/' /etc/cassandra/conf/cassandra.yaml
sudo sed -i "s|/var/lib/cassandra/data|${DATA_PATH}|" /etc/cassandra/conf/cassandra.yaml
echo "auto_bootstrap: true" | sudo tee -a /etc/cassandra/conf/cassandra.yaml

#Start cassandra service
sudo service cassandra start
