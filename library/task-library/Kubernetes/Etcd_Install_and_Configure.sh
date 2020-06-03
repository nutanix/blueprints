#!/bin/bash
set -ex

# - * - Section 1 <---------- Just a representation of section, Don't use in actual script ---------->
ETCD_VERSION="v3.3.15"
INTERNAL_IP="@@{address}@@"
ETCD_IPS="@@{all_master_ip_address}@@"
# Fetch Private key to push certs to other nodes in case of SSL_ON=yes
PRIVATE_KEY="@@{CENTOS.secret}@@"
NODE_NAME="etcd@@{calm_array_index}@@"
CREATE_VOLUME="@@{CREATE_VOLUME}@@"
SSL_ON="@@{SSL_ON}@@"
ETCD_CERT_PATH="/etc/ssl/certs/etcd"
ETCD_DATA_DIR="/var/lib/etcd"
ETCD_SERVER_PORT=2379
ETCD_CLIENT_PORT=2380
HTTP_METHOD="http"

CREATE_VOLUME="${CREATE_VOLUME:-no}"
SSL_ON="${SSL_ON:-no}"

# - * - Section 2 <---------- Just a representation of section, Don't use in actual script ---------->
# Download cfssl to generate self-signed certificates for secured etcd peer-peer communication.
# Download and install etcd

if [ "${SSL_ON}" == "yes" ]; then
    echo "INFO: Downloading cfssl & cfssljson for creating certs."
    HTTP_METHOD="https"
    curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error https://pkg.cfssl.org/R1.2/cfssl_linux-amd64
    curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64
    chmod +x cfssl_linux-amd64 cfssljson_linux-amd64
    sudo mv cfssl_linux-amd64 /usr/local/bin/cfssl
    sudo mv cfssljson_linux-amd64 /usr/local/bin/cfssljson
fi

echo "INFO: Downloading ETCD tar ball."
curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error "https://github.com/coreos/etcd/releases/download/${ETCD_VERSION}/etcd-${ETCD_VERSION}-linux-amd64.tar.gz"
tar -xvf etcd-${ETCD_VERSION}-linux-amd64.tar.gz
sudo mv etcd-${ETCD_VERSION}-linux-amd64/etcd* /usr/bin/
rm -rf etcd-${ETCD_VERSION}-linux-amd64*

# - * - Section 3 <---------- Just a representation of section, Don't use in actual script ---------->
# Create etcd_lvm lvm and mount to ${ETCD_DATA_DIR}.
# Create etcd system service.
# Generate etcd ca certs.
# Generate Server certs for 1st Etcd nodes.
# Generate Peer certs for remaining Etcd nodes.
# Generate Client certs for kubernetes master nodes.

sudo mkdir -p /opt/kube-ssl ${ETCD_CERT_PATH} ${ETCD_DATA_DIR}

count=0
for ip in $(echo "${ETCD_IPS}" | tr "," "\n"); do
  CON+="etcd${count}=${HTTP_METHOD}://${ip}:${ETCD_CLIENT_PORT}",
  count=$((count+1))
done
ETCD_ALL_CONTROLLERS=$(echo $CON | sed  's/,$//')

echo "INFO: Configuring ETCD service."
echo "[Unit]
Description=etcd
Documentation=https://github.com/coreos

[Service]
ExecStart=/usr/bin/etcd \\
  --name ${NODE_NAME} \\
  --initial-advertise-peer-urls ${HTTP_METHOD}://${INTERNAL_IP}:${ETCD_CLIENT_PORT} \\
  --listen-peer-urls ${HTTP_METHOD}://${INTERNAL_IP}:${ETCD_CLIENT_PORT} \\
  --listen-client-urls ${HTTP_METHOD}://${INTERNAL_IP}:${ETCD_SERVER_PORT},${HTTP_METHOD}://127.0.0.1:${ETCD_SERVER_PORT} \\
  --advertise-client-urls ${HTTP_METHOD}://${INTERNAL_IP}:${ETCD_SERVER_PORT} \\
  --initial-cluster-token etcd-cluster-0 \\
  --initial-cluster ${ETCD_ALL_CONTROLLERS} \\
  --initial-cluster-state new \\
  --data-dir=/var/lib/etcd \\
  --wal-dir=/var/lib/etcd/wal \\
  --max-wals=10
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/etcd.service

echo "if \$programname == 'etcd' then /var/log/etcd.log
& stop" | sudo tee /etc/rsyslog.d/etcd.conf

if [ "${SSL_ON}" == "yes" ]; then
  sudo mkdir -p /etc/systemd/system/etcd.service.d
  echo "[Service]
Environment=ETCD_CERT_FILE=${ETCD_CERT_PATH}/etcd-server.pem
Environment=ETCD_KEY_FILE=${ETCD_CERT_PATH}/etcd-server-key.pem
Environment=ETCD_PEER_CERT_FILE=${ETCD_CERT_PATH}/etcd-peer.pem
Environment=ETCD_PEER_KEY_FILE=${ETCD_CERT_PATH}/etcd-peer-key.pem
Environment=ETCD_TRUSTED_CA_FILE=${ETCD_CERT_PATH}/etcd-ca.pem
Environment=ETCD_PEER_TRUSTED_CA_FILE=${ETCD_CERT_PATH}/etcd-ca.pem
Environment=ETCD_PEER_CLIENT_CERT_AUTH=true
Environment=ETCD_CLIENT_CERT_AUTH=true" | sudo tee /etc/systemd/system/etcd.service.d/override.conf
fi

if [ "${CREATE_VOLUME}" == "yes" ]; then
    echo "INFO: Configuring ETCD data volume."
    sudo yum install -y lvm2 --quiet
    sudo pvcreate /dev/sd{b,c,d}
    sudo vgcreate etcd /dev/sd{b,c,d}
    sleep 3
    sudo lvcreate -l 100%VG -n etcd_lvm etcd
    sudo mkfs.xfs /dev/etcd/etcd_lvm
    echo -e "/dev/etcd/etcd_lvm \t ${ETCD_DATA_DIR} \t xfs \t defaults \t 0 0" | sudo tee -a /etc/fstab
    sudo mount -a
fi

if [ @@{calm_array_index}@@ -eq 0 ] && [ "${SSL_ON}" == "yes" ];then
  echo "INFO: Creating & Configuring ETCD ssl certs."
  sudo chown -R $USER:$USER /opt/kube-ssl && cd /opt/kube-ssl
  echo '{
    "signing": {
      "default": {
        "expiry": "8760h"
      },
      "profiles": {
        "server": {
          "expiry": "8760h",
          "usages": [ "signing", "key encipherment", "server auth", "client auth" ]
        },
        "client": {
          "expiry": "8760h",
          "usages": [ "key encipherment", "client auth" ]
        },
        "client-server": {
          "expiry": "8760h",
          "usages": [ "key encipherment", "server auth", "client auth" ]
        }
      }
    }
  }' | tee ca-config.json

  echo '{
    "CN": "etcd-ca",
    "key": {
      "algo": "rsa",
      "size": 2048
    },
    "names": [
      {
        "C": "US",
        "L": "San Jose",
        "O": "etcd",
        "OU": "CA",
        "ST": "California"
      }
    ]
  }' | tee etcd-ca-csr.json

  cfssl gencert -initca etcd-ca-csr.json | cfssljson -bare etcd-ca

  echo '{
    "CN": "etcd",
    "hosts": [],
    "key": {
      "algo": "rsa",
      "size": 2048
    },
    "names": [
      {
        "C": "US",
        "L": "San Jose",
        "O": "etcd",
        "OU": "CA",
        "ST": "California"
      }
    ]
  }' | tee etcd-csr.json

  cfssl gencert -ca=etcd-ca.pem -ca-key=etcd-ca-key.pem -config=ca-config.json -hostname=${ETCD_IPS} -profile=server etcd-csr.json | cfssljson -bare etcd-server
  cfssl gencert -ca=etcd-ca.pem -ca-key=etcd-ca-key.pem -config=ca-config.json -hostname=${ETCD_IPS} -profile=client-server etcd-csr.json | cfssljson -bare etcd-peer
  cfssl gencert -ca=etcd-ca.pem -ca-key=etcd-ca-key.pem -config=ca-config.json -hostname=${ETCD_IPS} -profile=client etcd-csr.json | cfssljson -bare etcd-client

  echo "${PRIVATE_KEY}" | tee ~/.ssh/id_rsa
  chmod 600 ~/.ssh/id_rsa
  echo "INFO: Copying ssl certs to other nodes."
  for ip in $(echo ${ETCD_IPS} | tr "," "\n"); do
    scp -o stricthostkeychecking=no etcd*.pem ${ip}:
  done
fi

if [ "${SSL_ON}" == "yes" ]; then
    cd $HOME
    while [ ! -f etcd-ca.pem ]; do echo "waiting for ETCD certs." && sleep 5; done
    sudo mv etcd-*.pem ${ETCD_CERT_PATH}/
fi
sudo systemctl start etcd