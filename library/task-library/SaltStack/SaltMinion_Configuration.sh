#!/bin/sh

MINION_HOSTNAME="@@{MINION_HOSTNAME}@@-@@{calm_array_index}@@"

#### Perform some setup, first - hostname, package updates
sudo hostnamectl set-hostname $MINION_HOSTNAME
sudo yum -y update
sudo yum -y upgrade

#### Install some useful packages
sudo yum -y install vim net-tools bind-utils bash-completion wget
sudo yum -y install epel-release

#### Remove the firewall package
#### Don't do this in production!
sudo yum -y remove firewalld
