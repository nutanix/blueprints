#!/bin/bash
set -ex

##############################################
# Name        : RabbitMQ_uninstall.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script to setup RabbitMQ 
# Compatibility : Centos 6, 7
##############################################

sudo yum remove -y erlang

sudo yum remove -y rabbitmq-server

