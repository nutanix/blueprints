#!/bin/bash -xe

# Variables
APP_ROOT='/opt/apps'
SOLR_VERSION=@@{SOLR_VERSION}@@


# Set hostname
sudo hostnamectl set-hostname "@@{name}@@"


# Install dependencies
sudo yum -y install lsof curl java-1.8.0-openjdk initscripts nc telnet lvm2 iotop

# Disk setup
sudo pvcreate /dev/sdb
sudo vgcreate DataVG /dev/sdb
sudo lvcreate -l 100%FREE -n DataLV DataVG
sudo mkfs.ext4 /dev/DataVG/DataLV

# Set Solr Java memory to 70% of available RAM
SOLR_JAVA_MEM_MB=`python -c "print(int(0.7*@@{platform.status.resources.memory_size_mib}@@))"`

# Configure partitions
sudo mkdir -p "${APP_ROOT}"
echo "/dev/DataVG/DataLV /opt/apps ext4 rw,noatime,nobarrier 0 0" | sudo tee -a /etc/fstab
sudo mount -a

# Set file and process limits
sudo sed -i '/# End of file/i \
solr    soft    nofile 65000\
solr    hard    nofile 65000\
solr    soft    nproc 65000\
solr    soft    nproc 65000'  /etc/security/limits.conf

# Install Solr
sudo curl -o solr-${SOLR_VERSION}.tgz "http://archive.apache.org/dist/lucene/solr/${SOLR_VERSION}/solr-${SOLR_VERSION}.tgz"
sudo tar xzf solr-${SOLR_VERSION}.tgz solr-${SOLR_VERSION}/bin/install_solr_service.sh --strip-components=2
sudo ./install_solr_service.sh solr-${SOLR_VERSION}.tgz -d /opt/apps/solr_data -i /opt/apps -n
sudo sed -ri '/SOLR_JAVA_MEM/ s/#//g;s/(Xm)([a-z])([0-9]+)(m)/\1\2'${SOLR_JAVA_MEM_MB}'\4/g' /etc/default/solr.in.sh

sudo service solr start
sudo service solr status

