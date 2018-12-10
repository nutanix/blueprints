#!/bin/bash
set -ex
##############################################
# Name          : Salt_Bootstrap.sh
# Author        : Calm Devops
# Version       : 1.0
# Description   : Script is used to bootstrap the salt
# Compatibility :
# Sourced From  : "https://raw.githubusercontent.com/saltstack/salt-bootstrap/develop/bootstrap-salt.sh"
##############################################

curl -L "https://raw.githubusercontent.com/saltstack/salt-bootstrap/develop/bootstrap-salt.sh" -o bootstrap-salt.sh
chmod +x bootstrap-salt.sh
./bootstrap-salt.sh
