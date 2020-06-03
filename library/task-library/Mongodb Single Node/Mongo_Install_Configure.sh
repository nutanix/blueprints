#!/bin/bash
set -ex

VERSION="@@{MONGO_VERSION}@@"
DATA_PATH="@@{DATA_PATH}@@"
JOURNAL_PATH="@@{JOURNAL_PATH}@@"
LOG_PATH="@@{LOG_PATH}@@"
sudo hostnamectl set-hostname --static @@{name}@@


echo '[mongodb-org-3.4]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/3.4/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-3.4.asc' | sudo tee /etc/yum.repos.d/mongodb-3.4.repo

sudo yum install -y --quiet mongodb-org-${VERSION} mongodb-org-server-${VERSION} mongodb-org-shell-${VERSION} mongodb-org-mongos-${VERSION} mongodb-org-tools-${VERSION}

echo 'exclude=mongodb-org*' | sudo tee -a /etc/yum.conf
sudo mkdir -p ${DATA_PATH} ${JOURNAL_PATH} ${LOG_PATH}

echo "/dev/mongoDataVG/mongoDataLV  ${DATA_PATH} xfs defaults,auto,noatime,noexec 0 0
/dev/mongoJournalVG/mongoJournalLV ${JOURNAL_PATH} xfs defaults,auto,noexec 0 0
/dev/mongoLogVG/mongoLogLV ${LOG_PATH} xfs defaults,auto,noexec 0 0" | sudo tee -a /etc/fstab
sudo mount -a

sudo ln -s ${JOURNAL_PATH} ${DATA_PATH}/journal
sudo chown -R mongod:mongod ${DATA_PATH} ${JOURNAL_PATH} ${LOG_PATH}

sudo blockdev --setra 32 /dev/dm-2
sudo blockdev --getra /dev/dm-2

sudo sysctl vm.swappiness=1
echo 'vm.swappiness=1' | sudo tee -a /etc/sysctl.conf


sudo sed -i 's/bindIp:/#bindIp:/g' /etc/mongod.conf
sudo sed -i "s#/var/lib/mongo#${DATA_PATH}#g" /etc/mongod.conf
sudo sed -i "s#  path: /var/log/mongodb/mongod.log#  path: ${LOG_PATH}/mongod.log#" /etc/mongod.conf
    

if [[ -f /sys/kernel/mm/transparent_hugepage/enabled ]];then
	echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
fi
if [[ -f /sys/kernel/mm/transparent_hugepage/defrag ]];then
	echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag
fi

sudo systemctl enable mongod
sudo systemctl restart mongod
sleep 5
