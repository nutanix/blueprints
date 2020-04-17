#!/bin/bash
set -ex

#Variables used in this script 
REDIS_CONFIG_PASSWORD="@@{REDIS_CONFIG_PASSWORD}@@"

#Create seperate vg for redis storage
sudo mkdir -p /var/lib/redis
sudo yum install -y lvm2
sudo pvcreate /dev/sdb
sudo vgcreate redis_vg /dev/sdb
sleep 3
sudo lvcreate -l 100%VG -n redis_lvm redis_vg
sudo mkfs.xfs /dev/redis_vg/redis_lvm
echo -e "/dev/redis_vg/redis_lvm \t /var/lib/redis \t xfs \t defaults \t 0 0" | sudo tee -a /etc/fstab
sudo mount -a

#Update yum repo and install redis
sudo yum install epel-release -y
sudo yum update -y
sudo yum install redis -y

#Configure the redis in /etc/redis.conf
sudo sed -i 's/tcp-keepalive 0/tcp-keepalive 60/' /etc/redis.conf
sudo sed -i 's/bind 127.0.0.1/#bind 127.0.0.1/' /etc/redis.conf
echo "requirepass ${REDIS_CONFIG_PASSWORD}" | sudo tee -a /etc/redis.conf
echo "maxmemory-policy noeviction" | sudo tee -a /etc/redis.conf
sudo sed -i 's/appendonly no/appendonly yes/' /etc/redis.conf
sudo sed -i 's/appendfilename "appendonly.aof"/appendfilename redis-staging-ao.aof/' /etc/redis.conf

#Restart the redis service
sudo systemctl restart redis.service
