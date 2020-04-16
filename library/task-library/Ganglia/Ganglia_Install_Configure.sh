#!/bin/bash -xe

## Disable SELinux
sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
sudo setenforce 0

# Enable epel repo, install ganglia and dependencies
sudo yum install -y epel-release
sudo yum install -y ganglia rrdtool ganglia-gmetad ganglia-gmond ganglia-web

# Ganglia configuration
sudo adduser -m adminganglia
sudo htpasswd -b -c /etc/httpd/auth.basic adminganglia "@@{WEB_LOGIN_PASS}@@"

echo "Alias /ganglia /usr/share/ganglia
<Location /ganglia>
    AuthType basic
    AuthName \"Ganglia web UI\"
    AuthBasicProvider file
    AuthUserFile \"/etc/httpd/auth.basic\"
    Require user adminganglia
</Location>" | sudo tee /etc/httpd/conf.d/ganglia.conf


echo "gridname \"@@{GRID_NAME}@@\"
data_source \"@@{CLUSTER_NAME}@@\" 60 @@{address}@@:@@{WEB_PORT}@@" | sudo tee -a /etc/ganglia/gmetad.conf

sudo sed -i 's/name = "unspecified"/name = "@@{CLUSTER_NAME}@@"/g' /etc/ganglia/gmond.conf
sudo sed -i 's/#mcast_join/mcast_join/g' /etc/ganglia/gmond.conf
sudo sed -i 's/#bind =/bind =/g' /etc/ganglia/gmond.conf

sudo systemctl restart httpd gmetad gmond
sudo systemctl enable httpd gmetad httpd


