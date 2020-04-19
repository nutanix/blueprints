#!/bin/bash

set -ex

## Initialize Variables
ADMIN_PASSWORD="@@{ADMIN_PASSWORD}@@"
ADMIN_EMAIL="@@{ADMIN_EMAIL}@@"
VM_IP="@@{address}@@"

sudo hostnamectl set-hostname --static graylog

sudo yum update -y
sudo setenforce 0

## Install Java
sudo yum -y install epel-release
sudo yum install -y java-1.8.0-openjdk-headless.x86_64
sudo yum -y install pwgen

## Install mongo
echo '[mongodb-org-3.6]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/3.6/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-3.6.asc' | sudo tee -a /etc/yum.repos.d/mongodb-org-3.6.repo
sudo yum install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

## Install and configure elastic search
sudo rpm --import https://packages.elastic.co/GPG-KEY-elasticsearch
echo '[elasticsearch]
name=Elasticsearch repository
baseurl=https://packages.elastic.co/elasticsearch/2.x/centos
gpgcheck=1
gpgkey=https://packages.elastic.co/GPG-KEY-elasticsearch
enabled=1' | sudo tee -a /etc/yum.repos.d/elasticsearch.repo

sudo yum -y install elasticsearch

sudo sed -i '/cluster.name/s/^#//' /etc/elasticsearch/elasticsearch.yml
sudo sed -i '/cluster.name/s/my-application/graylog/' /etc/elasticsearch/elasticsearch.yml

sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch

sleep 15

## Verify elastic search 
sudo curl -XGET 'http://localhost:9200/_cluster/health?pretty=true'


## Install graylog
sudo rpm -Uvh https://packages.graylog2.org/repo/packages/graylog-2.5-repository_latest.rpm
sudo yum -y install graylog-server

## Configure graylog conf
sudo sed -i '/password_secret/s/^/#/' /etc/graylog/server/server.conf
sudo sed -i '/root_password_sha2/s/^/#/' /etc/graylog/server/server.conf
sudo sed -i '/elasticsearch_shards/s/^/#/' /etc/graylog/server/server.conf

pwd_secret=$(sudo pwgen -N 1 -s 96)
root_pwd=$(echo -n ${ADMIN_PASSWORD} | sha256sum | awk '{print $1}')


echo "password_secret=$pwd_secret
root_password_sha2=$root_pwd
root_email=${ADMIN_EMAIL}
root_timezone=UTC
elasticsearch_discovery_zen_ping_unicast_hosts = ${VM_IP}:9300
elasticsearch_shards=1
script.inline: false
script.indexed: false
script.file: false" | sudo tee -a /etc/graylog/server/server.conf



sudo sed -i '/web_listen_uri/s/^#//' /etc/graylog/server/server.conf

sudo sed -i "/rest_listen_uri/s/127.0.0.1/${VM_IP}/" /etc/graylog/server/server.conf
sudo sed -i "/web_listen_uri/s/127.0.0.1/${VM_IP}/" /etc/graylog/server/server.conf


## Start graylog service
sudo systemctl enable graylog-server
sudo systemctl start graylog-server
sudo systemctl status graylog-server


