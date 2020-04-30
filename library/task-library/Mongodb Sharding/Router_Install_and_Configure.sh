#!/bin/bash
set -ex

##  Variable Initialization
PROFILE="@@{PROFILE}@@"
VERSION="@@{MONGO_VERSION}@@"
DATA_PATH="@@{DATA_PATH}@@"
JOURNAL_PATH="@@{JOURNAL_PATH}@@"
LOG_PATH="@@{LOG_PATH}@@"


## Set hostname
sudo hostnamectl set-hostname --static @@{name}@@

## Getting data ip and router ip addresses
if [ "x${PROFILE}" = "xAHV" ]
then
    CONFIG_IP_LIST="@@{AHVConfigSet.address}@@"
    DATA_IP_LIST="@@{AHVDataSet.address}@@"
    ROUTER_IP_LIST="@@{calm_array_address}@@"
    CONFIG_SRV_IPS="@@{AHVConfigSet.address}@@"
    REPLICA_IPS=($(echo @@{AHVDataSet.address}@@ | sed 's/^,//' | sed 's/,$//' | tr "," "\n"))
    INTERNAL_IP="@@{address}@@"
elif [ "x${PROFILE}" = "xAWS" ]
then
    CONFIG_IP_LIST="@@{AWSConfigSet.private_ip_address}@@"
    DATA_IP_LIST="@@{AWSDataSet.private_ip_address}@@"
    ROUTER_IP_LIST="@@{calm_array_private_ip_address}@@"
    CONFIG_SRV_IPS="@@{AWSConfigSet.private_ip_address}@@"
    REPLICA_IPS=($(echo @@{AWSDataSet.private_ip_address}@@ | sed 's/^,//' | sed 's/,$//' | tr "," "\n"))
    INTERNAL_IP="@@{private_ip_address}@@"    
elif [ "x${PROFILE}" = "xGCP" ]
then
    CONFIG_IP_LIST="@@{GCPConfigSet.private_ip_address}@@"
    DATA_IP_LIST="@@{GCPDataSet.private_ip_address}@@" 
    ROUTER_IP_LIST="@@{calm_array_private_ip_address}@@"
    CONFIG_SRV_IPS="@@{GCPConfigSet.private_ip_address}@@"
    REPLICA_IPS=($(echo @@{GCPDataSet.private_ip_address}@@ | sed 's/^,//' | sed 's/,$//' | tr "," "\n"))
    INTERNAL_IP="@@{private_ip_address}@@"    
elif [ "x${PROFILE}" = "xAZURE" ]
then
    CONFIG_IP_LIST="@@{AzureConfigSet.private_ip_address}@@"
    DATA_IP_LIST="@@{AzureDataSet.private_ip_address}@@" 
    ROUTER_IP_LIST="@@{calm_array_private_ip_address}@@"
    CONFIG_SRV_IPS="@@{AzureConfigSet.private_ip_address}@@"
    REPLICA_IPS=($(echo @@{AzureDataSet.private_ip_address}@@ | sed 's/^,//' | sed 's/,$//' | tr "," "\n"))
    INTERNAL_IP="@@{private_ip_address}@@"    
elif [ "x${PROFILE}" = "xVMWARE" ]
then
    CONFIG_IP_LIST="@@{VMwareConfigSet.address}@@"
    DATA_IP_LIST="@@{VMwareDataSet.address}@@" 
    ROUTER_IP_LIST="@@{calm_array_address}@@"
    CONFIG_SRV_IPS="@@{VMwareConfigSet.address}@@"
    REPLICA_IPS=($(echo @@{VMwareDataSet.address}@@ | sed 's/^,//' | sed 's/,$//' | tr "," "\n"))
    INTERNAL_IP="@@{address}@@"    
fi

NODES_PER_REPLICA_SET="@@{NODES_PER_REPLICA_SET}@@"
noOfShards=$((${#REPLICA_IPS[@]}/${NODES_PER_REPLICA_SET}))
config_ips=$(echo "${CONFIG_SRV_IPS}" | sed 's/^,//' | sed 's/,$//' | sed 's/,/:27017,/g')
config_ips=$config_ips":27017"

## Update hosts file 
cat > /tmp/set-hostnames.py <<EOF
#!/usr/bin/python
import re
config_ips="${CONFIG_IP_LIST}"
data_ips="${DATA_IP_LIST}"
router_ips="${ROUTER_IP_LIST}"

hostfile = open('/etc/hosts', 'r').read()
print hostfile
hostfile = re.sub('\n#MONGODB-BEGIN.*?#MONGODB-END', '', hostfile, flags=re.DOTALL)
hostfile += "#MONGODB-BEGIN\n"
count=1
for ip in config_ips.split(','):
  hostfile += ip + " config" + str(count) + ".mongodb\n"
  count += 1
count=1
for ip in data_ips.split(','):
  hostfile += ip + " data" + str(count) + ".mongodb\n"
  count += 1
count=1
for ip in router_ips.split(','):
  hostfile += ip + " router" + str(count) + ".mongodb\n"
  count += 1
hostfile += "#MONGODB-END\n"
open('/etc/hosts', 'w').write(hostfile)
EOF

sudo python /tmp/set-hostnames.py

## Update system params
if [[ -f /sys/kernel/mm/transparent_hugepage/enabled ]];then
	echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
fi
if [[ -f /sys/kernel/mm/transparent_hugepage/defrag ]];then
	echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag
fi

## Disable SELinux
sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
sudo setenforce 0

## Configure mongod yum repo
echo '[mongodb-org-3.4]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/3.4/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-3.4.asc' | sudo tee /etc/yum.repos.d/mongodb-3.4.repo

## Install mongod
sudo yum update -y --quiet
sudo yum install -y --quiet mongodb-org-${VERSION} mongodb-org-server-${VERSION} mongodb-org-shell-${VERSION} mongodb-org-mongos-${VERSION} mongodb-org-tools-${VERSION}

echo 'exclude=mongodb-org*' | sudo tee -a /etc/yum.conf

sudo mkdir -p ${DATA_PATH} ${JOURNAL_PATH} ${LOG_PATH}
sudo ln -s ${JOURNAL_PATH} ${DATA_PATH}/journal
sudo chown -R mongod:mongod ${DATA_PATH} ${JOURNAL_PATH} ${LOG_PATH}

## Configure mongod conf
sudo sed -i 's/bindIp:/#bindIp:/g' /etc/mongod.conf
sudo sed -i "s#/var/lib/mongo#${DATA_PATH}#g" /etc/mongod.conf

## Setup systemd conf for mongo service
echo "[Unit]
Description=High-performance, schema-free document-oriented database
After=network.target
Documentation=https://docs.mongodb.org/manual

[Service]
User=mongod
Group=mongod
Environment=\"OPTIONS=--port 27017 --configdb configReplSet/$config_ips --logpath /var/log/mongodb/mongos.log\"
ExecStart=/usr/bin/mongos \$OPTIONS
PermissionsStartOnly=true
PIDFile=/var/run/mongodb/mongos.pid
# file size
LimitFSIZE=infinity
# cpu time
LimitCPU=infinity
# virtual memory size
LimitAS=infinity
# open files
LimitNOFILE=64000
# processes/threads
LimitNPROC=64000
# total threads (user+kernel)
TasksMax=infinity
TasksAccounting=false
# Recommended limits for for mongod as specified in
# http://docs.mongodb.org/manual/reference/ulimit/#recommended-settings

[Install]
WantedBy=multi-user.target" | sudo tee /usr/lib/systemd/system/mongos.service

sudo systemctl start mongos
#sudo -u mongod -b mongos --port 27017 --configdb  --logpath /var/log/mongodb/mongos.log 

sleep 2

count=0
for ((number=1;number <= $noOfShards;number++))
do
  replicaSetName="dataReplSet${number}"
  sudo mongo --host ${INTERNAL_IP} --port 27017 --eval "sh.addShard( \"$replicaSetName/${REPLICA_IPS[${count}]}:27017\" )"
  count=$(($count + ${NODES_PER_REPLICA_SET}))
done

## Setting up mongos and mongod services
sudo systemctl stop mongod
sudo systemctl disable mongod
sudo systemctl start mongos
sudo systemctl enable mongos
sleep 2