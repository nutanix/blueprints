#!/bin/bash

## Download the rpms and install PostgreSQL
sudo wget -c https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
sudo yum -y install pgdg-redhat-repo-latest.noarch.rpm
sudo rpm --import http://packages.2ndquadrant.com/repmgr/RPM-GPG-KEY-repmgr
sudo yum install -y http://packages.2ndquadrant.com/repmgr/yum-repo-rpms/repmgr-rhel-1.0-1.noarch.rpm
sudo yum -y install postgresql96 postgresql96-contrib postgresql96-server postgresql96-devel postgresql96-plpython

## Run initdb
sudo /usr/pgsql-9.6/bin/postgresql96-setup initdb

## Start and stop postgresql to make sure DB creates the required directories
sudo systemctl start postgresql-9.6.service
sudo systemctl stop postgresql-9.6.service

## Copy the created postgres directory to a temp directory
sudo mkdir /tmp/pgsql
sudo mv /var/lib/pgsql/9.6/data /tmp/pgsql

## Create directory, mount LVM and fix permissions 
sudo mkdir /var/lib/pgsql/9.6/data/
sudo mount -o noatime,barrier=0 /dev/pgDataVG/pgDataLV /var/lib/pgsql/9.6/data/ 

sudo mkdir /var/lib/pgsql/9.6/data/pg_xlog
sudo mount -o noatime,barrier=0 /dev/pgLogVG/pgLogLV /var/lib/pgsql/9.6/data/pg_xlog

sudo chown -R postgres:postgres /var/lib/pgsql/9.6/data/

## Move the xlog to the new LVM
sudo find /tmp/pgsql/data/pg_xlog -maxdepth 1 -mindepth 1 -exec mv -t /var/lib/pgsql/9.6/data/pg_xlog/ {} +

## Remove pg_xlog from temp dir to avoid being copied again
sudo rm -rf /tmp/pgsql/data/pg_xlog

## Move the pgsql directory to the LVM
sudo find /tmp/pgsql/data -maxdepth 1 -mindepth 1 -exec mv -t /var/lib/pgsql/9.6/data/ {} +
sudo chmod -R 0700 /var/lib/pgsql/9.6/data

## Enable service on boot
sudo systemctl enable postgresql-9.6.service

## Add mount points to /etc/fstab
echo "/dev/mapper/pgDataVG-pgDataLV /var/lib/pgsql/9.6/data ext4 rw,seclabel,noatime,nobarrier,stripe=4096,data=ordered 0 0" | sudo tee -a /etc/fstab
echo "/dev/mapper/pgLogVG-pgLogLV /var/lib/pgsql/9.6/data/pg_xlog ext4 rw,seclabel,noatime,nobarrier,stripe=2048,data=ordered 0 0" | sudo tee -a  /etc/fstab

## Restart postgresql service
sudo systemctl restart postgresql-9.6
sudo systemctl status postgresql-9.6
