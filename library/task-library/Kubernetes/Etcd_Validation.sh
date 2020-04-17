#!/bin/bash
set -ex

# - * - Section 1 <---------- Just a representation of section, Don't use in actual script ---------->
ETCD_CERT_PATH="/etc/ssl/certs/etcd"
INTERNAL_IP="@@{address}@@"
SSL_ON="@@{SSL_ON}@@"
ETCD_SERVER_PORT=2379
HTTP_METHOD="http"

SSL_ON="${SSL_ON:-no}"

if [ "${SSL_ON}" == "yes" ]; then
    HTTP_METHOD="https"
fi

# - * - Section 3 <---------- Just a representation of section, Don't use in actual script ---------->
echo "INFO: Validating ETCD service"
if [ "${SSL_ON}" == "yes" ]; then
    output=$(sudo etcdctl --ca-file ${ETCD_CERT_PATH}/etcd-ca.pem --cert-file ${ETCD_CERT_PATH}/etcd-client.pem --key-file ${ETCD_CERT_PATH}/etcd-client-key.pem --endpoints ${HTTP_METHOD}://${INTERNAL_IP}:${ETCD_SERVER_PORT=2379} -o simple cluster-health)
else
    output=$(sudo etcdctl -endpoints ${HTTP_METHOD}://${INTERNAL_IP}:${ETCD_SERVER_PORT=2379} -o simple cluster-health)
fi
if [[ $output == *"cluster is healthy" ]]; then
	echo "INFO: ETCD Service looks good."
else
	echo $output
	echo "ERROR: ETCD Service failed to start."
    exit 1
fi