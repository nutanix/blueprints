#!/bin/bash

## -*- Install Pre-requisites for Mongodb
sudo yum update -y --quiet
sudo yum install -y  wget xfs* bc unzip lvm2* lsscsi numactl

##  Disable SELinux
sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
sudo setenforce 0

echo "System packages are installed"