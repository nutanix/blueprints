#!/bin/bash
set -ex

##  Variable Initialization
PROFILE="@@{PROFILE}@@"
VERSION="@@{MONGO_VERSION}@@"
DATA_PATH="@@{DATA_PATH}@@"
JOURNAL_PATH="@@{JOURNAL_PATH}@@"
LOG_PATH="@@{LOG_PATH}@@"


## Getting data ip and router ip addresses
if [ "x${PROFILE}" = "xAHV" ]
then
	CONFIG_IP_LIST="@@{calm_array_address}@@"
  DATA_IP_LIST="@@{AHVDataSet.address}@@"
  ROUTER_IP_LIST="@@{AHVRouter.address}@@"
  CONFIG_SRV_IPS="@@{calm_array_address}@@"
	INTERNAL_IP="@@{address}@@"
elif [ "x${PROFILE}" = "xAWS" ]
then
	CONFIG_IP_LIST="@@{calm_array_private_ip_address}@@"
  DATA_IP_LIST="@@{AWSDataSet.private_ip_address}@@"
  ROUTER_IP_LIST="@@{AWSRouter.private_ip_address}@@"
  CONFIG_SRV_IPS="@@{calm_array_private_ip_address}@@"
	INTERNAL_IP="@@{private_ip_address}@@"    
elif [ "x${PROFILE}" = "xGCP" ]
then
	CONFIG_IP_LIST="@@{calm_array_private_ip_address}@@"
  DATA_IP_LIST="@@{GCPDataSet.private_ip_address}@@"
  ROUTER_IP_LIST="@@{GCPRouter.private_ip_address}@@" 
  CONFIG_SRV_IPS="@@{calm_array_private_ip_address}@@"
	INTERNAL_IP="@@{private_ip_address}@@"    
elif [ "x${PROFILE}" = "xAZURE" ]
then
	CONFIG_IP_LIST="@@{calm_array_private_ip_address}@@"
  DATA_IP_LIST="@@{AzureDataSet.private_ip_address}@@"
  ROUTER_IP_LIST="@@{AzureRouter.private_ip_address}@@" 
  CONFIG_SRV_IPS="@@{calm_array_private_ip_address}@@"
	INTERNAL_IP="@@{private_ip_address}@@"    
elif [ "x${PROFILE}" = "xVMWARE" ]
then
	CONFIG_IP_LIST="@@{calm_array_address}@@"
  DATA_IP_LIST="@@{VMwareDataSet.address}@@"
  ROUTER_IP_LIST="@@{VMwareRouter.address}@@"
  CONFIG_SRV_IPS="@@{calm_array_address}@@"
	INTERNAL_IP="@@{address}@@"    
fi

## Setup hostname
sudo hostnamectl set-hostname --static @@{name}@@

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

## Disable  SELinux
sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
sudo setenforce 0

## Configure yum repo for mongodb
echo '[mongodb-org-3.4]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/3.4/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-3.4.asc' | sudo tee /etc/yum.repos.d/mongodb-3.4.repo

## Install MongoDB
sudo yum update -y --quiet
sudo yum install -y --quiet mongodb-org-${VERSION} mongodb-org-server-${VERSION} mongodb-org-shell-${VERSION} mongodb-org-mongos-${VERSION} mongodb-org-tools-${VERSION}

echo 'exclude=mongodb-org*' | sudo tee -a /etc/yum.conf

sudo mkdir -p ${DATA_PATH} ${JOURNAL_PATH} ${LOG_PATH}
sudo ln -s ${JOURNAL_PATH} ${DATA_PATH}/journal
sudo chown -R mongod:mongod ${DATA_PATH} ${JOURNAL_PATH} ${LOG_PATH}

## Setting up mongod conf
sudo sed -i 's/bindIp:/#bindIp:/g' /etc/mongod.conf
sudo sed -i "s#/var/lib/mongo#${DATA_PATH}#g" /etc/mongod.conf
sudo sed -i 's/#sharding:/sharding:\n  clusterRole: configsvr/g' /etc/mongod.conf
sudo sed -i 's/#replication:/replication:\n  replSetName: configReplSet/g' /etc/mongod.conf

## Generating config replica set
config_ips=$(echo "${CONFIG_SRV_IPS}" | sed 's/^,//' | sed 's/,$//' | tr "," "\n")
config_cnt=0
config_str=""

for config in $config_ips
do
  config_str=$config_str"{\"_id\": $config_cnt, host:\"$config:27017\"},"
  config_cnt=$(($config_cnt + 1))
done
config_str=`echo $config_str | sed 's/,$//'`
json=$(cat <<EOF
{
  "_id": "configReplSet",
  "members": [
    $config_str
  ]
}
EOF
)

## Setting sysctl params
if [[ -f /sys/kernel/mm/transparent_hugepage/enabled ]];then
	echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
fi
if [[ -f /sys/kernel/mm/transparent_hugepage/defrag ]];then
	echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag
fi

## Enable and restart mongod service
sudo systemctl restart mongod
sudo systemctl enable mongod
sleep 15

if [ @@{calm_array_index}@@ -ne 0 ];then
  exit
fi

## Initializing Config Replica Set
sudo mongo --host ${INTERNAL_IP} --port 27017 --eval "rs.initiate( $json )"
sleep 2
