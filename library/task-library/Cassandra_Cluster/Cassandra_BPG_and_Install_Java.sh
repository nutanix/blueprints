i#!/bin/bash
set -ex

#Create seperate vg for cassandra storage
sudo mkdir -p /var/lib/cassandra
sudo yum install -y lvm2
sudo pvcreate /dev/sdb
sudo vgcreate cassandra_vg /dev/sdb
sleep 3
sudo lvcreate -l 100%VG -n cassandra_lvm cassandra_vg
sudo mkfs.xfs /dev/cassandra_vg/cassandra_lvm
echo -e "/dev/cassandra_vg/cassandra_lvm \t /var/lib/cassandra \t xfs \t defaults \t 0 0" | sudo tee -a /etc/fstab
sudo mount -a

#Update yum and install Java
sudo yum update -y
sudo yum install -y java-1.8.0-openjdk
