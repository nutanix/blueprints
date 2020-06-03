#!/bin/bash -xe

# Set hostname
sudo hostnamectl set-hostname --static ElasticSearch@@{calm_array_index}@@

# Disable selinux
sudo setenforce 0
sudo sed -i 's/SELINUX=enforcing/SELINUX=disabled/g;s/SELINUXTYPE=targeted/#&/g' /etc/selinux/config

#Install Ntp
sudo yum install -y ntp
sudo ntpdate pool.ntp.org

#Remove older docker versions if present
sudo yum remove -y docker docker-common container-selinux docker-selinux docker-engine

# Install docker
if [ "@@{DOCKER_EDITION}@@" = "EE" ]; then
  echo "@@{DOCKER_EE_URL}@@" | sudo tee /etc/yum/vars/dockerurl
  sudo yum install -y yum-utils
  sudo yum-config-manager --add-repo @@{DOCKER_EE_URL}@@/docker-ee.repo
  sudo yum install -y docker-ee-@@{DOCKER_VERSION}@@
elif [ "@@{DOCKER_EDITION}@@" = "CE" ]; then
  sudo yum install -y yum-utils
  sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
  sudo yum install -y docker-ce-@@{DOCKER_VERSION}@@
fi

sudo sed -i '/ExecStart=/c\ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock' /usr/lib/systemd/system/docker.service

sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -a -G docker $USER

#Create volume and containers
sudo sysctl -w vm.max_map_count=262144
sudo docker volume create -d local --name=esdata
qu=$(($(($(echo "@@{calm_array_address}@@" | tr "," "\n" | wc -l)/2))+1))
sudo docker run -d --name=elasticsearch@@{calm_array_index}@@ --cap-add=IPC_LOCK --ulimit memlock=-1:-1 --ulimit nofile=65536:65536 -p 9200:9200 -p 9300:9300 -e ES_JAVA_OPTS="-Xms512m -Xmx512m" -e "bootstrap.memory_lock=true" -v esdata:/usr/share/elasticsearch/data elasticsearch:@@{ELASTIC_VERSION}@@ bin/elasticsearch -Enode.name="es@@{calm_array_index}@@" -Ecluster.name="@@{CLUSTER_NAME}@@" -Enetwork.host=_eth0_ -Enetwork.publish_host=@@{Substrate_ElasticAHVCluster_address}@@ -Ediscovery.zen.ping.unicast.hosts=@@{calm_array_address}@@ -Ediscovery.zen.minimum_master_nodes=$qu
