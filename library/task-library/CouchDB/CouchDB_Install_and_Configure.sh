#!/bin/bash
set -ex

# - * - Variables and constants.
COUCHDB_USER="@@{COUCHDB_USER}@@"
COUCHDB_PASSWORD="@@{COUCHDB_PASSWORD}@@"
COUCHDB_SECRET="@@{COUCHDB_SECRET}@@"
CREATE_VOLUME="@@{CREATE_VOLUME}@@"
IP="@@{address}@@"
ALL_IPS="@@{calm_array_address}@@"
NODE_COUNT=$(echo "${ALL_IPS}" | tr ',' '\n' | wc -l)
PORT=5984

CREATE_VOLUME="${CREATE_VOLUME:-no}"

echo '[bintray--apache-couchdb-rpm]
name=bintray--apache-couchdb-rpm
baseurl=http://apache.bintray.com/couchdb-rpm/el$releasever/$basearch/
gpgcheck=0
repo_gpgcheck=0
enabled=1' | sudo tee /etc/yum.repos.d/apache-couchdb.repo

# - * - Install CouchDB

sudo yum update -y --quiet
sudo yum install -y --quiet epel-release
sudo yum install -y --quiet couchdb

# - * - Configure CouchDB

sudo sed -i "s|;admin = mysecretpassword|admin = ${COUCHDB_PASSWORD}|" /opt/couchdb/etc/local.ini
sudo sed -i "s/;bind_address = 127.0.0.1/bind_address = 0.0.0.0/" /opt/couchdb/etc/local.ini

if [ "${CREATE_VOLUME}" == "yes" ]; then
  sudo yum install -y lvm2 --quiet
  sudo pvcreate /dev/sd{b,c,d}
  sudo vgcreate couchdbDataVG /dev/sdb /dev/sdc /dev/sdd
  sudo lvcreate -l 100%FREE -i3 -I1M -n couchdbDataLV couchdbDataVG
  sudo lvchange -r 0 /dev/couchdbDataVG/couchdbDataLV
  sudo mkfs.xfs -K /dev/couchdbDataVG/couchdbDataLV
  echo "/dev/couchdbDataVG/couchdbDataLV /var/lib/couchdb xfs inode64,nobarrier,noatime,logbufs=8 0 0" | sudo tee -a /etc/fstab
  sudo mount -a
  sudo chown -R couchdb:couchdb /var/lib/couchdb
fi

sudo systemctl start couchdb
sudo systemctl enable couchdb
sleep 10

if [ @@{calm_array_index}@@ -ne 0 ];then
  exit
fi

for ip in $(echo "${ALL_IPS}" | tr "," "\n"); do
  if [[ "${ip}" != "@@{address}@@" ]]; then
    curl -X POST --user ${COUCHDB_USER}:${COUCHDB_PASSWORD} -H "Content-Type: application/json" \
    -d "{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \"username\": \"${COUCHDB_USER}\", \"password\":\"${COUCHDB_PASSWORD}\", \"port\": 15984, \"node_count\": \"${NODE_COUNT}\", \"remote_node\": \"${ip}\", \"remote_current_user\": \"${COUCHDB_USER}\", \"remote_current_password\": \"${COUCHDB_PASSWORD}\" }" \
    http://${IP}:${PORT}/_cluster_setup || true
    
  	curl -X POST --user ${COUCHDB_USER}:${COUCHDB_PASSWORD} -H "Content-Type: application/json" \
  	-d "{\"action\":\"add_node\",\"username\":\"${COUCHDB_USER}\",\"password\":\"${COUCHDB_PASSWORD}\",\"host\":\"${ip}\",\"port\":$PORT,\"singlenode\":false}" \
  	http://${IP}:${PORT}/_cluster_setup || true
  fi
done

curl -X POST --user ${COUCHDB_USER}:${COUCHDB_PASSWORD} -H "Content-Type: application/json" \
-d '{"action":"finish_cluster"}' http://${IP}:${PORT}/_cluster_setup