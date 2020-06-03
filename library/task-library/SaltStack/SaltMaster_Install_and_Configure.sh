#!/bin/sh

MASTER_HOSTNAME="@@{MASTER_HOSTNAME}@@"

#### Perform some setup, first - hostname, package updates
sudo hostnamectl set-hostname @@{MASTER_HOSTNAME}@@

#### Yum updae and upgrade
sudo yum -y update
sudo yum -y upgrade

#### Install some useful packages
sudo yum -y install vim net-tools bind-utils bash-completion wget

#### Uninstall the firewall
#### don't do this in production!
sudo yum -y remove firewalld

#### Install epel-release
sudo yum -y install epel-release

#### Install the repo for the latest SaltStack version
sudo yum -y install https://repo.saltstack.com/yum/redhat/salt-repo-latest-2.el7.noarch.rpm

#### Install the actual SaltStack master
sudo yum -y install salt-master

#### Make sure the salt binaries were installed correctly
#### Installation failure won't cause the script to stop unless we manually exit with an error code here
[ -e /usr/bin/salt ] && echo "salt binary found" || exit $?
sleep 3

#### Bind to and listen on the host IP address only
sudo sed -i -- 's/#interface: 0.0.0.0/interface: @@{address}@@/' /etc/salt/master
sudo echo '@@{address}@@ salt' | sudo tee -a /etc/hosts

#### Enable and start salt master service 
sudo systemctl enable salt-master.service
sudo systemctl start salt-master.service

#### Setup the SaltStack master directory structure
sudo mkdir -p /srv/salt
sudo mkdir -p /srv/salt/all

#### Setup the initial SaltStack states
sudo echo "base:
  '*':
    - all" | sudo tee /srv/salt/top.sls

#### Setup the SaltStack state that will apply to all SaltStack minions
sudo echo "pkg.upgrade:
  module.run
all.packages:
  pkg.installed:
    - pkgs:
      - git
      - nginx
nginx.running:
  service.running:
    - name: nginx" | sudo tee /srv/salt/all/init.sls
