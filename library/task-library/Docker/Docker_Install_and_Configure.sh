#!/bin/bash
set -ex

# - * - Variables and constants.
DOCKER_VERSION="@@{DOCKER_VERSION}@@"
CREATE_VOLUME="@@{CREATE_VOLUME}@@"

CREATE_VOLUME="${CREATE_VOLUME:-no}"

# -*- Install Pre-Requisites
sudo yum update -y --quiet

# -*- Install Docker
sudo yum install -y --quiet yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
if [[ "${DOCKER_VERSION}" == "17.03.3.ce" ]]; then
  sudo yum install -y --quiet --setopt=obsoletes=0 docker-ce-${DOCKER_VERSION} docker-ce-selinux-${DOCKER_VERSION}
else
  sudo yum install -y --quiet docker-ce-${DOCKER_VERSION} docker-ce-selinux-${DOCKER_VERSION}
fi

# -*- Configure Docker
sudo sed -i '/ExecStart=/c\\ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock' /usr/lib/systemd/system/docker.service
sudo usermod -a -G docker $USER

sudo mkdir -p /etc/docker
echo '{
  "storage-driver": "overlay2"
}' | sudo tee /etc/docker/daemon.json

if [ "${CREATE_VOLUME}" == "yes" ]; then
  sudo yum install -y lvm2 --quiet
  sudo mkdir -p /var/lib/docker
  sudo pvcreate /dev/sd{b,c,d}
  sudo vgcreate docker /dev/sd{b,c,d}
  sleep 3
  sudo lvcreate -l 100%VG -n docker_lvm docker
  sudo mkfs.xfs /dev/docker/docker_lvm
  echo -e "/dev/docker/docker_lvm \t /var/lib/docker \t xfs \t defaults \t 0 0" | sudo tee -a /etc/fstab
  sudo mount -a
fi

echo 'exclude=docker*' | sudo tee -a /etc/yum.conf

sudo systemctl enable docker
sudo systemctl restart docker