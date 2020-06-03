#!/bin/bash
set -ex

##############################################
# Name        : Chef_Setup.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script will download and install chef
# Compatibility : Centos 6, 7
##############################################

sudo yum install -y --quiet wget

curl -L https://www.chef.io/chef/install.sh | sudo bash

sudo mkdir -p /var/chef/cache /var/chef/cookbooks

wget -qO- https://supermarket.chef.io/cookbooks/chef-server/versions/5.5.2/download | sudo tar xvzC /var/chef/cookbooks

for dep in chef-ingredient
do
  wget -qO- https://supermarket.chef.io/cookbooks/${dep}/download | sudo tar xvzC /var/chef/cookbooks
done

cat > /tmp/dna.json <<EOH
{
  "chef-server": {
    "api_fqdn": "chef-server",
    "addons": ["manage"],
    "accept_license": true,
    "version": "@@{CHEF_SERVER_VERSION}@@"
  }
}
EOH

# GO GO GO!!!
sudo chef-solo --chef-license accept-silent -o 'recipe[chef-server::default],recipe[chef-server::addons]' -j /tmp/dna.json
