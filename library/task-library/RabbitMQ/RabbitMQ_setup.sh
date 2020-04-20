#!/bin/bash
set -ex

##############################################
# Name        : RabbitMQ_setup.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to setup RabbitMQ 
# Compatibility : Centos 6, 7
##############################################

sudo hostnamectl set-hostname --static @@{name}@@

sudo yum update -y --quiet
sudo yum install -y epel-release
sudo yum install -y erlang

sudo rpm --import https://www.rabbitmq.com/rabbitmq-release-signing-key.asc
sudo yum install -y rabbitmq-server

sudo systemctl start rabbitmq-server
