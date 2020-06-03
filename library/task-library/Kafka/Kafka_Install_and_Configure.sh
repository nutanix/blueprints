#!/bin/bash
set -ex

# -*- Variables and constants
KAFKA_URL="@@{KAFKA_URL}@@"
ZOOKEEPER_DATA_DIR="@@{ZOOKEEPER_DATA_DIR}@@"
ARRAY_ADDRESS="@@{calm_array_address}@@"
KAFKA_LOG_DIRS="@@{KAFKA_LOG_DIRS}@@"
NUMBER_OF_PARTITIONS="@@{NUMBER_OF_PARTITIONS}@@"

ID=$((@@{calm_array_index}@@+1))
for ip in $(echo "${ARRAY_ADDRESS}" | tr "," "\n"); do
  CON+="${ip}:2181,"
done
ZOOKEEPER_CONNECT=$(echo $CON | sed  's/,$//')

sudo yum -y --quiet update

# -*- Install zookeeper and kafka
sudo yum install -y --quiet java-1.8.0-openjdk.x86_64 wget

sudo wget "${KAFKA_URL}" -O /opt/kafka.tgz
cd /opt/
sudo chmod a+x kafka.tgz
sudo mkdir -p kafka
sudo tar -xzf kafka.tgz -C kafka/
sudo mv /opt/kafka/kafka_*/* /opt/kafka/

# -*- Configure zookeeper and kafka
sudo echo  "[Unit]
Description=Apache Zookeeper server (Kafka)
Documentation=http://zookeeper.apache.org
Requires=network.target remote-fs.target
After=network.target remote-fs.target

[Service]
Type=simple
User=root
Group=root
Environment=JAVA_HOME=/usr/lib/jvm/jre-1.8.0-openjdk
ExecStart=/opt/kafka/bin/zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties
ExecStop=/opt/kafka/bin/zookeeper-server-stop.sh

[Install]
WantedBy=multi-user.target" | sudo tee -a /etc/systemd/system/kafka-zookeeper.service

sudo echo "[Unit]
Description=Apache Kafka server (broker)
Documentation=http://kafka.apache.org/documentation.html
Requires=network.target remote-fs.target
After=network.target remote-fs.target kafka-zookeeper.service

[Service]
Type=simple
User=root
Group=root
Environment=JAVA_HOME=/usr/lib/jvm/jre-1.8.0-openjdk
ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
ExecStop=/opt/kafka/bin/kafka-server-stop.sh" | sudo tee -a /etc/systemd/system/kafka.service

count=0
for ip in $(echo "${ARRAY_ADDRESS}" | tr "," "\n"); do
  count=$((count+1))
  if [[ "${ip}" == "@@{address}@@" ]]; then
  	ip="0.0.0.0"
  fi
  echo "server.${count}=${ip}:2888:3888" | sudo tee -a /opt/kafka/config/zookeeper.properties
done

echo "initLimit=5
syncLimit=2" | sudo tee -a /opt/kafka/config/zookeeper.properties

sudo sed -i "s#dataDir=\/tmp\/zookeeper#dataDir=${ZOOKEEPER_DATA_DIR}#" /opt/kafka/config/zookeeper.properties
mkdir -p ${ZOOKEEPER_DATA_DIR}
echo ${ID} | sudo tee "${ZOOKEEPER_DATA_DIR}/myid"
sudo sed -i "s/broker.id=0/broker.id=${ID}/g" /opt/kafka/config/server.properties
sudo sed -i "s/num.partitions=1/num.partitions=${NUMBER_OF_PARTITIONS}/" /opt/kafka/config/server.properties
sudo sed -i "s/zookeeper.connect=localhost:2181/zookeeper.connect=${ZOOKEEPER_CONNECT}/" /opt/kafka/config/server.properties
sudo sed -i "s#log.dirs=\/tmp\/kafka-logs#log.dirs=${KAFKA_LOG_DIRS}#g" /opt/kafka/config/server.properties
sudo sed -i "s%#listeners=PLAINTEXT://:9092%listeners=PLAINTEXT://@@{address}@@:9092%" /opt/kafka/config/server.properties
