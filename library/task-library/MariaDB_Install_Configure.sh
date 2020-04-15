#!/bin/bash

# Disable selinux
sudo setenforce 0
sudo sed -i 's/SELINUX=enforcing/SELINUX=disabled/g;s/SELINUXTYPE=targeted/#&/g' /etc/selinux/config

# Install dependencies
sudo yum -y install lvm2 iotop

# Set hostname
sudo hostnamectl set-hostname "@@{name}@@"

##############
#
# LVM setup script for MariaDB . 4 disks for DATA and 4 for logs
# Data disks are 50GB | Log disks are 25GB
#
#############

#MariaDB data
sudo pvcreate /dev/sdb /dev/sdc /dev/sdd /dev/sde
sudo vgcreate mariadbDataVG /dev/sdb /dev/sdd /dev/sdc /dev/sde
sudo lvcreate -l 100%FREE -i4 -I1M -n mariadbDataLV mariadbDataVG          ## Use 1MB to avoid IO amplification 
#lvcreate -l 100%FREE -i4 -I4M -n pgDataLV pgDataVG


#MariaDB logs
sudo pvcreate /dev/sdf /dev/sdg /dev/sdh /dev/sdi
sudo vgcreate mariadbLogVG /dev/sdf /dev/sdg /dev/sdh /dev/sdi
sudo lvcreate -l 100%FREE -i2 -I1M -n mariadbLogLV mariadbLogVG            ## Use 1MB to avoid IO amplification
#lvcreate -l 100%FREE -i2 -I4M -n pgLogLV pgLogVG


#Disable LVM read ahead
sudo lvchange -r 0 /dev/mariadbDataVG/mariadbDataLV
sudo lvchange -r 0 /dev/mariadbLogVG/mariadbLogLV


#Format LVMs with ext4 and use nodiscard to make sure format time is fast on Nutanix due to SCSI unmap
sudo mkfs.ext4 -E nodiscard /dev/mariadbDataVG/mariadbDataLV
sudo mkfs.ext4 -E nodiscard /dev/mariadbLogVG/mariadbLogLV

sleep 30


# Install Mariadb
echo '[mariadb]
name = MariaDB
baseurl = http://yum.mariadb.org/10.3/rhel7-amd64
gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB
gpgcheck=1' | sudo tee /etc/yum.repos.d/mariadb.repo

sudo yum install MariaDB-server MariaDB-client -y


# Configure Mariadb
echo '!includedir /etc/my.cnf.d' | sudo tee /etc/my.cnf

echo '[mysqld]
binlog-format=mixed
log-bin=mysql-bin
datadir=/mysql/data
sql_mode=NO_ENGINE_SUBSTITUTION,STRICT_TRANS_TABLES
innodb_data_home_dir = /mysql/data
innodb_log_group_home_dir = /mysql/log
innodb_file_per_table
tmpdir=/mysql/tmpdir
innodb_undo_directory = /mysql/undo

default_tmp_storage_engine = innodb
innodb_log_files_in_group = 4
innodb_log_file_size = 1G
innodb_log_buffer_size = 8M
innodb_buffer_pool_size = 6G
large-pages
innodb_buffer_pool_instances = 64
innodb_flush_method=O_DIRECT
innodb_flush_neighbors=0
innodb_flush_log_at_trx_commit=1
innodb_buffer_pool_dump_at_shutdown=1
innodb_buffer_pool_load_at_startup=1
bulk_insert_buffer_size = 256
innodb_thread_concurrency = 16

# Undo tablespace
innodb_undo_tablespaces = 5

# Networking
wait_timeout=57600
max_allowed_packet=1G
socket=/var/lib/mysql/mysql.sock
skip-name-resolve
port=3306
max_connections=1000' | sudo tee /etc/my.cnf.d/nutanix.cnf

sudo sed -i "/\[mysqld\]/a server-id=100" /etc/my.cnf.d/nutanix.cnf

# -*- Sysctl configuration
mysql_grp_id=`id -g mysql`
sudo sysctl -w vm.swappiness=0
sudo sysctl -w vm.nr_hugepages=1024
sudo sysctl -w vm.overcommit_memory=1
sudo sysctl -w vm.dirty_background_ratio=5
sudo sysctl -w vm.dirty_ratio=15
sudo sysctl -w vm.dirty_expire_centisecs=500
sudo sysctl -w vm.dirty_writeback_centisecs=100
sudo sysctl -w vm.hugetlb_shm_group=$mysql_grp_id

echo 'vm.swappiness=0
vm.nr_hugepages=1024
vm.overcommit_memory=1
vm.dirty_background_ratio=5
vm.dirty_ratio=15
vm.dirty_expire_centisecs=500
vm.dirty_writeback_centisecs=100
vm.hugetlb_shm_group=$mysql_grp_id' | sudo tee  -a /etc/sysctl.conf

echo "ACTION=='add|change', SUBSYSTEM=='block', RUN+='/bin/sh -c \"/bin/echo 1024 > /sys%p/queue/max_sectors_kb\"'" | sudo tee /etc/udev/rules.d/71-block-max-sectors.rules
#echo 1024 | sudo tee /sys/block/sd?/queue/max_sectors_kb

echo "/dev/mariadbDataVG/mariadbDataLV /mysql/data ext4 rw,noatime,nobarrier,stripe=4096,data=ordered 0 0" | sudo tee -a /etc/fstab
echo "/dev/mariadbLogVG/mariadbLogLV /mysql/log ext4 rw,noatime,nobarrier,stripe=4096,data=ordered 0 0" | sudo tee -a /etc/fstab
sudo mkdir -p /mysql/log /mysql/data /mysql/tmpdir /mysql/undo
sudo mount -a

sudo rm -rf /mysql/data/*
sudo mysql_install_db &>/dev/null
sudo chown -R mysql:mysql /mysql

sudo systemctl enable mariadb
sudo systemctl start mariadb

# Set root password
sudo mysqladmin password '@@{MARIADB_PASSWORD}@@'
