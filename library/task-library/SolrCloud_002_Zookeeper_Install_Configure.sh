#!/bin/bash -xe

# Variables
APP_ROOT='/opt/apps'
ZK_VERSION=@@{ZK_VERSION}@@
ZK_ROOT='/opt/apps/zookeeper'
ZK_DATA='/opt/apps/zookeeper_data'

# Set hostname
sudo hostnamectl set-hostname "@@{name}@@"

# Install dependencies
sudo yum -y install lsof curl java-1.8.0-openjdk initscripts nc telnet lvm2 iotop

# Disk setup
sudo pvcreate /dev/sdb
sudo vgcreate DataVG /dev/sdb
sudo lvcreate -l 100%FREE -n DataLV DataVG
sudo mkfs.ext4 /dev/DataVG/DataLV

# Create array for storing VM IPs
ZK_IP_ARRAY=(`echo "@@{calm_array_address}@@" | tr ',' ' '`)
ZK_QUORUM=`echo "${ZK_IP_ARRAY[@]}" | sed 's/ /:2181,/g;s/$/:2181/g'`

# Configure partitions
sudo mkdir -p "${APP_ROOT}"
echo "/dev/DataVG/DataLV /opt/apps ext4 rw,noatime,nobarrier 0 0" | sudo tee -a /etc/fstab
sudo mount -a
sudo mkdir -p "${ZK_DATA}"

# Download and install zookeeper
sudo curl https://archive.apache.org/dist/zookeeper/zookeeper-${ZK_VERSION}/zookeeper-${ZK_VERSION}.tar.gz | sudo tar -C /opt/apps/ -xz
sudo ln -s "/opt/apps/zookeeper-${ZK_VERSION}" "${ZK_ROOT}"
sudo useradd -m zookeeper

# Set Zookeeper myid
echo $((@@{calm_array_index}@@+1)) | sudo tee ${ZK_DATA}/myid

# Build zookeeper config
echo "tickTime=2000
dataDir=${ZK_DATA}
clientPort=2181
initLimit=10
syncLimit=5
$(for i in ${!ZK_IP_ARRAY[@]}; do
echo server.$((${i}+1))=${ZK_IP_ARRAY[${i}]}:2888:3888
done)" | sudo tee ${ZK_ROOT}/conf/zoo.cfg

# Set ownership of all zookeeper directories
sudo chown -R zookeeper:zookeeper /opt/apps/zookeeper*

# Create zookeeper daemon
echo "[Unit]
Description=Zookeeper Daemon
Wants=syslog.target

[Service]
Type=forking
WorkingDirectory=${ZK_ROOT}/
User=zookeeper
ExecStart=${ZK_ROOT}/bin/zkServer.sh start
PIDFile=${ZK_DATA}/zookeeper_server.pid
ExecStop=/bin/kill $MAINPID
SuccessExitStatus=1 143
TimeoutSec=120
Restart=on-failure

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/zookeeper.service

sudo systemctl enable zookeeper
sudo systemctl start zookeeper
