#!/bin/bash

## Enable icinga repo
sudo yum install -y https://packages.icinga.com/epel/icinga-rpm-release-7-latest.noarch.rpm
sudo yum install -y epel-release
sudo yum install -y centos-release-scl

## Install Icinga and start service
sudo yum install -y icinga2
sudo systemctl enable icinga2
sudo systemctl start icinga2

## Install Postgresql as Icinga DB and start service
sudo yum install -y postgresql-server postgresql
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql

## Install Icinga-IDO module
sudo yum install -y icinga2-ido-pgsql


