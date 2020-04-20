#!/bin/bash
set -ex

##############################################
# Name        : Docker_registry_setup.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script is used to configure registry with specified arguments
# Compatibility : Centos 6, 7
##############################################

sudo mkdir -p certs auth
docker run --rm --entrypoint htpasswd registry:2 -Bbn "@@{REGISTRY_USERNAME}@@" "@@{REGISTRY_PASSWORD}@@" | sudo tee auth/htpasswd
if [[ "@@{INSECURE_REGISTRY}@@" == "yes" ]]; then
	sudo openssl req -newkey rsa:4096 -nodes -sha256 -keyout certs/domain.key -x509 -days 365 -out certs/domain.crt -subj "/C=@@{COUNTRY}@@/ST=@@{STATE}@@/L=@@{CITY}@@/O=@@{ORGANIZATION}@@/OU=@@{ORGANIZATIONAL_UNIT}@@/CN=@@{CN}@@"
	sudo docker run -d -p 5000:5000  --restart=always --name DockerRegistry -v /mnt/registry:/var/lib/registry -v `pwd`/auth:/auth -e "REGISTRY_AUTH=htpasswd" -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd -v `pwd`/certs:/certs -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key registry:2
else 
	sudo docker run -d -p 5000:5000  --restart=always --name DockerRegistry -v /mnt/registry:/var/lib/registry -v `pwd`/auth:/auth -e "REGISTRY_AUTH=htpasswd" -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd registry:2
fi

