#!/bin/bash
set -ex

# - * - Variables and constants.
KUBE_CLUSTER_NAME="@@{KUBE_CLUSTER_NAME}@@"
KUBE_VERSION="@@{calm_array_VERSION[0]}@@"
INTERNAL_IP="@@{address}@@"
MASTER_IPS="@@{all_master_ip_address}@@"
MASTER_IP="@@{all_master_ip_address[0]}@@"
NODE_NAME="worker@@{calm_array_index}@@"
CLUSTER_SUBNET="@@{KUBE_CLUSTER_SUBNET}@@"
SERVICE_SUBNET="@@{KUBE_SERVICE_SUBNET}@@"
KUBE_CLUSTER_DNS="@@{KUBE_DNS_IP}@@"
DOCKER_VERSION="@@{DOCKER_VERSION}@@"
SSL_ON="@@{SSL_ON}@@"
KUBE_CERT_PATH="/etc/kubernetes/ssl"
KUBE_MANIFEST_PATH="/etc/kubernetes/manifests"
KUBE_CONFIG_PATH="/etc/kubernetes/config"
KUBE_CNI_BIN_PATH="/opt/cni/bin"
KUBE_CNI_CONF_PATH="/etc/cni/net.d"
ETCD_SERVER_PORT=2379
MASTER_API_HTTPS=6443

SSL_ON="${SSL_ON:-no}"

# -*- Install Kubernetes master
sudo mkdir -p ${KUBE_CERT_PATH} ${KUBE_MANIFEST_PATH} ${KUBE_CNI_CONF_PATH} ${KUBE_CNI_BIN_PATH} ${KUBE_CONFIG_PATH}

curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error https://github.com/containernetworking/plugins/releases/download/v0.7.5/cni-plugins-amd64-v0.7.5.tgz
curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubelet
curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubectl
chmod +x kubelet kubectl
sudo mv kubelet kubectl /usr/bin/

sudo tar -zxvf cni-plugins-amd64-*.tgz -C ${KUBE_CNI_BIN_PATH}
rm -rf cni-plugins-amd64-*.tgz

if [ "${SSL_ON}" == "yes" ]; then
    echo "INFO: Downloading cfssl & cfssljson for creating certs."
    HTTP_METHOD="https"
    curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error https://pkg.cfssl.org/R1.2/cfssl_linux-amd64
    curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64
    chmod +x cfssl_linux-amd64 cfssljson_linux-amd64
    sudo mv cfssl_linux-amd64 /usr/local/bin/cfssl
    sudo mv cfssljson_linux-amd64 /usr/local/bin/cfssljson
fi

# -*- Configure Kubernetes Worker
cat <<EOF | sudo tee ${KUBE_CONFIG_PATH}/kubelet-config.yaml
kind: KubeletConfiguration
apiVersion: kubelet.config.k8s.io/v1beta1
authentication:
  anonymous:
    enabled: false
  webhook:
    enabled: true
  x509:
    clientCAFile: "${KUBE_CERT_PATH}/ca.pem"
authorization:
  mode: Webhook
clusterDomain: "cluster.local"
clusterDNS:
  - "${KUBE_CLUSTER_DNS}"
staticPodPath: "${KUBE_MANIFEST_PATH}"
podCIDR: "${CLUSTER_SUBNET}"
runtimeRequestTimeout: "10m"
tlsCertFile: "${KUBE_CERT_PATH}/${NODE_NAME}.pem"
tlsPrivateKeyFile: "${KUBE_CERT_PATH}/${NODE_NAME}-key.pem"
readOnlyPort: 0
protectKernelDefaults: false
makeIPTablesUtilChains: true
eventRecordQPS: 0
kubeletCgroups: "/systemd/system.slice"
evictionHard:
  memory.available: "200Mi"
  nodefs.available:  "10%"
  nodefs.inodesFree: "5%"
EOF

echo "[Unit]
Description=Kubernetes Kubelet
Documentation=https://github.com/GoogleCloudPlatform/kubernetes
After=docker.service
Requires=docker.service

[Service]
ExecStart=/usr/bin/kubelet \\
  --config=${KUBE_CONFIG_PATH}/kubelet-config.yaml \\
  --container-runtime=docker \\
  --kubeconfig=${KUBE_CERT_PATH}/${NODE_NAME}.kubeconfig \\
  --network-plugin=cni \\
  --register-node=true \\
  --runtime-cgroups=/systemd/system.slice \\
  --node-labels 'node-role.kubernetes.io/worker=true' \\
  --node-labels 'beta.kubernetes.io/fluentd-ds-ready=true' \\
  --v=2
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/kubelet.service

echo "if \$programname == 'kubelet' then /var/log/kubelet.log
& stop" | sudo tee /etc/rsyslog.d/kubelet.conf

cat <<EOF | sudo tee ${KUBE_CONFIG_PATH}/kube-proxy-config.yaml
kind: KubeProxyConfiguration
apiVersion: kubeproxy.config.k8s.io/v1alpha1
clientConnection:
  kubeconfig: "${KUBE_CERT_PATH}/kube-proxy.kubeconfig"
mode: "iptables"
clusterCIDR: "${CLUSTER_SUBNET}"
iptables:
  masqueradeAll: true
EOF

echo "apiVersion: v1
kind: Pod
metadata:
  name: kube-proxy
  namespace: kube-system
  labels:
    k8s-app: kube-proxy
spec:
  hostNetwork: true
  containers:
  - name: kube-proxy
    image: gcr.io/google-containers/hyperkube:${KUBE_VERSION}
    command:
    - /hyperkube
    - kube-proxy
    - --config=${KUBE_CONFIG_PATH}/kube-proxy-config.yaml
    securityContext:
      privileged: true
    volumeMounts:
    - mountPath: ${KUBE_CERT_PATH}
      name: ssl-certs-kubernetes
      readOnly: true
    - mountPath: /etc/ssl/certs
      name: ssl-certs-host
      readOnly: true
    - mountPath: /lib/modules
      name: lib-modules-host
      readOnly: true
    - mountPath: ${KUBE_CONFIG_PATH}
      name: kube-config-path
      readOnly: true
  volumes:
  - hostPath:
      path: ${KUBE_CERT_PATH}
    name: ssl-certs-kubernetes
  - hostPath:
      path: /etc/ssl/certs
    name: ssl-certs-host
  - hostPath:
      path: /lib/modules
    name: lib-modules-host
  - hostPath:
      path: ${KUBE_CONFIG_PATH}
    name: kube-config-path" | sudo tee ${KUBE_MANIFEST_PATH}/kube-proxy.yaml
    
if [ "@@{KUBE_CNI_PLUGIN}@@" == "canal" ] ||  [ "@@{KUBE_CNI_PLUGIN}@@" == "calico" ]; then
  sudo sed -i '/masqueradeAll/d' ${KUBE_CONFIG_PATH}/kube-proxy-config.yaml
fi 

echo '{
  "name": "cbr0",
  "type": "flannel",
  "delegate": {
    "isDefaultGateway": true
  }
}' | sudo tee ${KUBE_CNI_CONF_PATH}/10-flannel.conf

if [ "${SSL_ON}" == "yes" ]; then

  echo "@@{CENTOS.secret}@@" | tee ~/.ssh/id_rsa
  chmod 600 ~/.ssh/id_rsa

  count=0
  while [ ! $(ssh -o stricthostkeychecking=no $MASTER_IP "ls /opt/kube-ssl/encryption-config.yaml 2>/dev/null") ] ; do  echo "waiting for certs sleeping 5" && sleep 5; if [[ $count -eq 600 ]]; then echo "failed to download certs" && exit 1; fi; count=$(($count+5)) ; done

  scp -o stricthostkeychecking=no ${MASTER_IP}:/opt/kube-ssl/{ca*.pem,kubernetes*.pem,kube-proxy.kubeconfig,ca-config.json} .

  echo "{
    \"CN\": \"system:node:${NODE_NAME}\",
    \"key\": {
      \"algo\": \"rsa\",
      \"size\": 2048
    },
    \"names\": [
      {
        \"C\": \"US\",
        \"L\": \"San Jose\",
        \"O\": \"system:nodes\",
        \"OU\": \"Kubernetes The Hard Way\",
        \"ST\": \"California\"
      }
    ]
  }" | tee ${NODE_NAME}-csr.json
  cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -hostname=${NODE_NAME},${INTERNAL_IP} -profile=client-server ${NODE_NAME}-csr.json | cfssljson -bare ${NODE_NAME}

  kubectl config set-cluster ${KUBE_CLUSTER_NAME} --certificate-authority=ca.pem --embed-certs=true --server=https://${MASTER_IP}:${MASTER_API_HTTPS} --kubeconfig=${NODE_NAME}.kubeconfig
  kubectl config set-credentials system:node:${NODE_NAME} --client-certificate=${NODE_NAME}.pem --client-key=${NODE_NAME}-key.pem --embed-certs=true --kubeconfig=${NODE_NAME}.kubeconfig
  kubectl config set-context default --cluster=${KUBE_CLUSTER_NAME} --user=system:node:${NODE_NAME} --kubeconfig=${NODE_NAME}.kubeconfig
  kubectl config use-context default --kubeconfig=${NODE_NAME}.kubeconfig

  sudo cp *.pem *.kubeconfig ${KUBE_CERT_PATH}/
  sudo chmod +r ${KUBE_CERT_PATH}/*

  rm -rf ${NODE_NAME}-csr.json

fi

sudo systemctl start kubelet 
sudo systemctl enable kubelet
sudo systemctl restart rsyslog