#!/bin/bash
set -ex

# Script Variables & Constants
PUPPET_VERSION="@@{PUPPET_VERSION}@@"

# install puppet release rpm and puppet server.
sudo hostnamectl set-hostname --static @@{name}@@
sudo rpm -Uvh "http://yum.puppetlabs.com/puppet${PUPPET_VERSION}-release-el-7.noarch.rpm"
sudo yum install -y puppetserver