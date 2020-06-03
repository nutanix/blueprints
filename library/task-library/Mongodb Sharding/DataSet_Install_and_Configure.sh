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
	DATA_IP_LIST="@@{calm_array_address}@@"
  CONFIG_IP_LIST="@@{AHVConfigSet.address}@@"
  ROUTER_IP_LIST="@@{AHVRouter.address}@@"
  REPLICA_IPS="@@{calm_array_address}@@"
	INTERNAL_IP="@@{address}@@"
elif [ "x${PROFILE}" = "xAWS" ]
then
	DATA_IP_LIST="@@{calm_array_private_ip_address}@@"
  CONFIG_IP_LIST="@@{AWSConfigSet.private_ip_address}@@"
  ROUTER_IP_LIST="@@{AWSRouter.private_ip_address}@@"
  REPLICA_IPS="@@{calm_array_private_ip_address}@@"
	INTERNAL_IP="@@{private_ip_address}@@"
elif [ "x${PROFILE}" = "xGCP" ]
then
	DATA_IP_LIST="@@{calm_array_private_ip_address}@@"
  CONFIG_IP_LIST="@@{GCPConfigSet.private_ip_address}@@"
  ROUTER_IP_LIST="@@{GCPRouter.private_ip_address}@@" 
  REPLICA_IPS="@@{calm_array_private_ip_address}@@"
	INTERNAL_IP="@@{private_ip_address}@@"    
elif [ "x${PROFILE}" = "xAZURE" ]
then
	DATA_IP_LIST="@@{calm_array_private_ip_address}@@"
  CONFIG_IP_LIST="@@{AzureConfigSet.private_ip_address}@@"
  ROUTER_IP_LIST="@@{AzureRouter.private_ip_address}@@"  
  REPLICA_IPS="@@{calm_array_private_ip_address}@@"
	INTERNAL_IP="@@{private_ip_address}@@"    
    
elif [ "x${PROFILE}" = "xVMWARE" ]
then
	DATA_IP_LIST="@@{calm_array_address}@@"
  CONFIG_IP_LIST="@@{VMwareConfigSet.address}@@"
  ROUTER_IP_LIST="@@{VMwareRouter.address}@@"  
  REPLICA_IPS="@@{calm_array_address}@@"
	INTERNAL_IP="@@{address}@@"
fi

## Evalaute extra vars 
INDEX=@@{calm_array_index}@@
NODES_PER_REPLICA_SET=@@{NODES_PER_REPLICA_SET}@@
ARRAY_REPLICA_IPS=$(echo ${REPLICA_IPS} | sed 's/^,//' | sed 's/,$//' | tr "," "\n")

tmp=$((${INDEX}+${NODES_PER_REPLICA_SET}))
replicasetNo=$((${tmp}/${NODES_PER_REPLICA_SET}))
replicaSetName="dataReplSet${replicasetNo}"


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

## Configure mongod yum repo
echo '[mongodb-org-3.4]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/3.4/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-3.4.asc' | sudo tee /etc/yum.repos.d/mongodb-3.4.repo

## Install mongoDB
sudo yum install -y --quiet mongodb-org-${VERSION} mongodb-org-server-${VERSION} mongodb-org-shell-${VERSION} mongodb-org-mongos-${VERSION} mongodb-org-tools-${VERSION}

echo 'exclude=mongodb-org*' | sudo tee -a /etc/yum.conf
sudo mkdir -p ${DATA_PATH} ${JOURNAL_PATH} ${LOG_PATH}

## Mount mongo LVM partitions
echo "/dev/mongoDataVG/mongoDataLV  ${DATA_PATH} xfs defaults,auto,noatime,noexec 0 0
/dev/mongoJournalVG/mongoJournalLV ${JOURNAL_PATH} xfs defaults,auto,noexec 0 0
/dev/mongoLogVG/mongoLogLV ${LOG_PATH} xfs defaults,auto,noexec 0 0" | sudo tee -a /etc/fstab
sudo mount -a

sudo ln -s ${JOURNAL_PATH} ${DATA_PATH}/journal
sudo chown -R mongod:mongod ${DATA_PATH} ${JOURNAL_PATH} ${LOG_PATH}

sudo blockdev --setra 32 /dev/dm-2
sudo blockdev --getra /dev/dm-2

## Setup system params
sudo sysctl vm.swappiness=1
echo 'vm.swappiness=1' | sudo tee -a /etc/sysctl.conf

## Configure mongod conf
sudo sed -i 's/bindIp:/#bindIp:/g' /etc/mongod.conf
sudo sed -i "s#/var/lib/mongo#${DATA_PATH}#g" /etc/mongod.conf
sudo sed -i "s/#replication:/replication:\n  replSetName: $replicaSetName/g" /etc/mongod.conf
sudo sed -i 's/#sharding:/sharding:\n  clusterRole: shardsvr/g' /etc/mongod.conf
sudo sed -i 's#  path: /var/log/mongodb/mongod.log#  path: /mongodb/log/mongod.log#' /etc/mongod.conf

## Getting replicaset members details 
replica_cnt=0
declare -a replicaset_members

for replica in $ARRAY_REPLICA_IPS
do
  tmp=$((${replica_cnt}+${NODES_PER_REPLICA_SET}))
  i="$((${tmp}/${NODES_PER_REPLICA_SET}))"
  replicaset_members[$i]=${replicaset_members[$i]}"{\"_id\": $replica_cnt, host:\"$replica:27017\"},"
  replica_cnt=$(($replica_cnt + 1))
done

if [[ -f /sys/kernel/mm/transparent_hugepage/enabled ]];then
	echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
fi
if [[ -f /sys/kernel/mm/transparent_hugepage/defrag ]];then
	echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag
fi

sudo systemctl restart mongod
sudo systemctl enable mongod
sleep 15

### Initiating replicaset 
json=$(cat <<EOF
{
  "_id": "$replicaSetName",
  "members": [ ${replicaset_members[$replicasetNo]}]
}
EOF
)
sudo mongo --host ${INTERNAL_IP} --port 27017 --eval "rs.initiate( $json )"
sleep 2

