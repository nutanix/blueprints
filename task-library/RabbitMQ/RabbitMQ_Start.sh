#!/bin/bash
set -ex

##############################################
# Name        : RabbitMQ_Start.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to start RabbitMQ 
# Compatibility : Centos 6, 7
##############################################

sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
