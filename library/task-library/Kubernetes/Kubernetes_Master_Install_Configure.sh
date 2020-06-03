#!/bin/bash
set -ex

# - * - Variables and constants.
KUBE_CLUSTER_NAME="@@{KUBE_CLUSTER_NAME}@@"
KUBE_VERSION="@@{calm_array_VERSION[0]}@@"
INTERNAL_IP="@@{address}@@"
MASTER_IPS="@@{all_master_ip_address}@@"
WORKER_IPS="@@{all_worker_ip_address}@@"
NODE_NAME="master@@{calm_array_index}@@"
CLUSTER_SUBNET="@@{KUBE_CLUSTER_SUBNET}@@"
SERVICE_SUBNET="@@{KUBE_SERVICE_SUBNET}@@"
KUBE_CLUSTER_DNS="@@{KUBE_DNS_IP}@@"
SSL_ON="@@{SSL_ON}@@"
ETCD_CERT_PATH="/etc/ssl/certs/etcd"
KUBE_CERT_PATH="/etc/kubernetes/ssl"
KUBE_CONFIG_PATH="/etc/kubernetes/config"
KUBE_MANIFEST_PATH="/etc/kubernetes/manifests"
KUBE_CNI_BIN_PATH="/opt/cni/bin"
KUBE_CNI_CONF_PATH="/etc/cni/net.d"
MASTER_API_HTTPS=6443
ETCD_SERVER_PORT=2379
HTTP_METHOD="http"

SSL_ON="${SSL_ON:-no}"

sudo easy_install netaddr
FIRST_IP_SERVICE_SUBNET=$(python -c "from netaddr import * ; print IPNetwork('${SERVICE_SUBNET}')[1]")
CONTROLLER_COUNT=$(echo "@@{calm_array_address}@@" | tr ',' '\n' | wc -l)

count=0
for ip in $(echo "${MASTER_IPS}" | tr "," "\n"); do
  CONS_NAMES+="master${count}",
  ETCD+="https://${ip}:${ETCD_SERVER_PORT}",
  count=$((count+1))
done

CONTROLLER_NAMES=$(echo $CONS_NAMES | sed  's/,$//')
ETCD_SERVERS=$(echo $ETCD | sed  's/,$//')
  
count=0
for ip in $(echo ${WORKER_IPS} | tr "," "\n"); do
  MIN_NAMES+="worker${count}",
  count=$((count+1))
done
MINION_NAMES=$(echo $MIN_NAMES | sed  's/,$//')  

# -*- Install Kubernetes master
sudo mkdir -p /opt/kube-ssl ${KUBE_CERT_PATH} ${KUBE_MANIFEST_PATH} ${KUBE_CONFIG_PATH} ${KUBE_CNI_BIN_PATH} ${KUBE_CNI_CONF_PATH}
sudo yum update -y --quiet

curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubelet
curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubectl
curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error https://github.com/containernetworking/plugins/releases/download/v0.8.5/cni-plugins-linux-amd64-v0.8.5.tgz

chmod +x kubelet kubectl 
sudo mv kubelet /usr/bin/kubelet
sudo mv kubectl /usr/local/bin/

sudo tar -zxvf cni-plugins-linux-amd64-*.tgz -C ${KUBE_CNI_BIN_PATH}
rm -rf cni-plugins-linux-amd64-*.tgz

if [ "${SSL_ON}" == "yes" ]; then
    echo "INFO: Downloading cfssl & cfssljson for creating certs."
    HTTP_METHOD="https"
    curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error https://pkg.cfssl.org/R1.2/cfssl_linux-amd64
    curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64
    chmod +x cfssl_linux-amd64 cfssljson_linux-amd64
    sudo mv cfssl_linux-amd64 /usr/local/bin/cfssl
    sudo mv cfssljson_linux-amd64 /usr/local/bin/cfssljson
fi

# -*- Configure Kubernetes master
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
  --node-labels 'node.kubernetes.io/master=true' \\
  --node-labels 'node.kubernetes.io/etcd=true' \\
  --register-with-taints=node.kubernetes.io/master=true:NoSchedule \\
  --node-labels 'node.kubernetes.io/fluentd-ds-ready=true' \\
  --v=2
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/kubelet.service

echo "if \$programname == 'kubelet' then /var/log/kubelet.log
& stop" | sudo tee /etc/rsyslog.d/kubelet.conf

echo "apiVersion: v1
kind: Pod
metadata:
  name: kube-apiserver
  namespace: kube-system
  labels:
    k8s-app: kube-apiserver
spec:
  hostNetwork: true
  containers:
  - name: kube-apiserver
    image: gcr.io/google-containers/hyperkube:${KUBE_VERSION}
    command:
    - /hyperkube
    - kube-apiserver
    - --enable-admission-plugins=NamespaceLifecycle,NodeRestriction,LimitRanger,ServiceAccount,DefaultStorageClass,ResourceQuota,DenyEscalatingExec,EventRateLimit
    - --advertise-address=${INTERNAL_IP}
    - --allow-privileged=true
    - --anonymous-auth=false
    - --secure-port=${MASTER_API_HTTPS}
    - --profiling=false
    - --apiserver-count=${CONTROLLER_COUNT}
    - --audit-log-maxage=30
    - --audit-log-maxbackup=10
    - --audit-log-maxsize=100
    - --audit-log-path=/var/lib/audit.log
    - --authorization-mode=Node,RBAC
    - --bind-address=0.0.0.0
    - --kubelet-preferred-address-types=InternalIP,Hostname,ExternalIP
    - --event-ttl=1h
    - --service-account-lookup=true
    - --storage-backend=etcd3
    - --etcd-cafile=${ETCD_CERT_PATH}/etcd-ca.pem
    - --etcd-certfile=${ETCD_CERT_PATH}/etcd-client.pem
    - --etcd-keyfile=${ETCD_CERT_PATH}/etcd-client-key.pem
    - --etcd-servers=${ETCD_SERVERS}
    - --experimental-encryption-provider-config=${KUBE_CERT_PATH}/encryption-config.yaml
    - --admission-control-config-file=${KUBE_CERT_PATH}/admission-control-config-file.yaml
    - --tls-cert-file=${KUBE_CERT_PATH}/kubernetes.pem
    - --tls-private-key-file=${KUBE_CERT_PATH}/kubernetes-key.pem
    - --kubelet-certificate-authority=${KUBE_CERT_PATH}/ca.pem
    - --kubelet-client-certificate=${KUBE_CERT_PATH}/kubernetes.pem
    - --kubelet-client-key=${KUBE_CERT_PATH}/kubernetes-key.pem
    - --kubelet-https=true
    - --runtime-config=api/all=true
    - --service-account-key-file=${KUBE_CERT_PATH}/kubernetes.pem
    - --service-cluster-ip-range=${SERVICE_SUBNET}
    - --service-node-port-range=30000-32767
    - --client-ca-file=${KUBE_CERT_PATH}/ca.pem
    - --v=2
    ports:
    - containerPort: ${MASTER_API_HTTPS}
      hostPort: ${MASTER_API_HTTPS}
      name: https
    - containerPort: 8080
      hostPort: 8080
      name: local
    volumeMounts:
    - mountPath: ${KUBE_CERT_PATH}
      name: ssl-certs-kubernetes
      readOnly: true
    - mountPath: /etc/ssl/certs
      name: ssl-certs-host
      readOnly: true
    - mountPath: /etc/pki
      name: ca-certs-etc-pki
      readOnly: true
  volumes:
  - hostPath:
      path: ${KUBE_CERT_PATH}
    name: ssl-certs-kubernetes
  - hostPath:
      path: /etc/ssl/certs
    name: ssl-certs-host
  - hostPath:
      path: /etc/pki
    name: ca-certs-etc-pki" | sudo tee ${KUBE_MANIFEST_PATH}/kube-apiserver.yaml

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

echo "apiVersion: v1
kind: Pod
metadata:
  name: kube-controller-manager
  namespace: kube-system
  labels:
    k8s-app: kube-controller-manager
spec:
  hostNetwork: true
  containers:
  - name: kube-controller-manager
    image: gcr.io/google-containers/hyperkube:${KUBE_VERSION}
    command:
    - /hyperkube
    - kube-controller-manager
    - --bind-address=0.0.0.0  
    - --allocate-node-cidrs=true  
    - --cluster-cidr=${CLUSTER_SUBNET}
    - --cluster-name=${KUBE_CLUSTER_NAME}
    - --leader-elect=true  
    - --kubeconfig=${KUBE_CERT_PATH}/kube-controller-manager.kubeconfig  
    - --service-account-private-key-file=${KUBE_CERT_PATH}/kubernetes-key.pem
    - --root-ca-file=${KUBE_CERT_PATH}/ca.pem
    - --service-cluster-ip-range=${SERVICE_SUBNET}
    - --terminated-pod-gc-threshold=100  
    - --profiling=false  
    - --use-service-account-credentials=true
    - --v=2
    livenessProbe:
      httpGet:
        host: 127.0.0.1
        path: /healthz
        port: 10252
      initialDelaySeconds: 15
      timeoutSeconds: 1
    volumeMounts:
    - mountPath: ${KUBE_CERT_PATH}
      name: ssl-certs-kubernetes
      readOnly: true
    - mountPath: /etc/ssl/certs
      name: ssl-certs-host
      readOnly: true
    - mountPath: /etc/pki
      name: ca-certs-etc-pki
      readOnly: true
  volumes:
  - hostPath:
      path: ${KUBE_CERT_PATH}
    name: ssl-certs-kubernetes
  - hostPath:
      path: /etc/ssl/certs
    name: ssl-certs-host
  - hostPath:
      path: /etc/pki
    name: ca-certs-etc-pki" | sudo tee ${KUBE_MANIFEST_PATH}/kube-controller-manager.yaml
   
cat <<EOF | sudo tee ${KUBE_CONFIG_PATH}/kube-scheduler.yaml
apiVersion: kubescheduler.config.k8s.io/v1alpha1
kind: KubeSchedulerConfiguration
clientConnection:
  kubeconfig: "${KUBE_CERT_PATH}/kube-scheduler.kubeconfig"
leaderElection:
  leaderElect: true
EOF
   
echo "apiVersion: v1
kind: Pod
metadata:
  name: kube-scheduler
  namespace: kube-system
  labels:
    k8s-app: kube-scheduler
spec:
  hostNetwork: true
  containers:
  - name: kube-scheduler
    image: gcr.io/google-containers/hyperkube:${KUBE_VERSION}
    command:
    - /hyperkube
    - kube-scheduler
    - --config=${KUBE_CONFIG_PATH}/kube-scheduler.yaml
    - --v=2
    livenessProbe:
      httpGet:
        host: 127.0.0.1
        path: /healthz
        port: 10251
      initialDelaySeconds: 15
      timeoutSeconds: 1
    volumeMounts:
    - mountPath: ${KUBE_CERT_PATH}
      name: ssl-certs-kubernetes
      readOnly: true
    - mountPath: ${KUBE_CONFIG_PATH}
      name: kube-config-path
      readOnly: true
  volumes:
  - hostPath:
      path: ${KUBE_CERT_PATH}
    name: ssl-certs-kubernetes
  - hostPath:
      path: ${KUBE_CONFIG_PATH}
    name: kube-config-path" | sudo tee ${KUBE_MANIFEST_PATH}/kube-scheduler.yaml
    
echo "kind: AdmissionConfiguration
apiVersion: apiserver.k8s.io/v1alpha1
plugins:
- name: EventRateLimit
  path: eventconfig.yaml" | sudo tee ${KUBE_CERT_PATH}/admission-control-config-file.yaml
  
echo "kind: Configuration
apiVersion: eventratelimit.admission.k8s.io/v1alpha1
limits:
- type: Namespace
  qps: 50
  burst: 100
  cacheSize: 2000
- type: User
  qps: 10
  burst: 50" | sudo tee ${KUBE_CERT_PATH}/eventconfig.yaml

echo '{
  "cniVersion": "0.3.1",
  "name": "cbr0",
  "type": "flannel",
  "delegate": {
    "isDefaultGateway": true
  }
}' | sudo tee ${KUBE_CNI_CONF_PATH}/10-flannel.conf

if [ "${SSL_ON}" == "yes" ]; then
  if [ @@{calm_array_index}@@ -eq 0 ];then
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
      "CN": "kube-ca",
      "key": {
        "algo": "rsa",
        "size": 2048
      },
      "names": [
        {
          "C": "US",
          "L": "San Jose",
          "O": "kube",
          "OU": "CA",
          "ST": "California"
        }
      ]
    }' | tee kube-ca-csr.json

    cfssl gencert -initca kube-ca-csr.json | cfssljson -bare ca

    echo '{
      "CN": "kubernetes",
      "key": {
        "algo": "rsa",
        "size": 2048
      },
      "names": [
        {
          "C": "US",
          "L": "San Jose",
          "O": "kube",
          "OU": "Cluster",
          "ST": "California"
        }
      ]
    }' | tee kubernetes-csr.json

    cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -hostname=${CONTROLLER_NAMES},${MASTER_IPS},${MINION_NAMES},${WORKER_IPS},${FIRST_IP_SERVICE_SUBNET},127.0.0.1,kubernetes.default,kubernetes,kubernetes.default.svc,kubernetes.default.svc.cluster.local -profile=server kubernetes-csr.json | cfssljson -bare kubernetes

    echo '{
      "CN": "system:kube-controller-manager",
      "hosts": [],
      "key": {
        "algo": "rsa",
        "size": 2048
      },
      "names": [
        {
          "C": "US",
          "L": "San Jose",
          "O": "system:kube-controller-manager",
          "OU": "Cluster",
          "ST": "California"
        }
      ]
    }' | tee kube-controller-manager-csr.json

    cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server kube-controller-manager-csr.json | cfssljson -bare kube-controller-manager

    echo '{
      "CN": "system:kube-scheduler",
      "hosts": [],
      "key": {
        "algo": "rsa",
        "size": 2048
      },
      "names": [
        {
          "C": "US",
          "L": "San Jose",
          "O": "system:kube-scheduler",
          "OU": "Cluster",
          "ST": "California"
        }
      ]
    }' | tee kube-scheduler-csr.json

    cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server kube-scheduler-csr.json | cfssljson -bare kube-scheduler

    count=0
    for ip in $(echo ${MASTER_IPS} | tr "," "\n"); do
    instance="master${count}"
    echo "{
      \"CN\": \"system:node:${instance}\",
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
    }" | tee ${instance}-csr.json
    cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -hostname=${instance},${ip} -profile=client-server ${instance}-csr.json | cfssljson -bare ${instance}
    count=$((count+1))
    done 

    # -*- Creating kube-proxy certificates
    echo '{
      "CN": "system:kube-proxy",
      "hosts": [],
      "key": {
        "algo": "rsa",
        "size": 2048
      },
      "names": [
        {
          "C": "US",
          "L": "San Jose",
          "O": "system:node-proxier",
          "OU": "Cluster",
          "ST": "California"
        }
      ]
    }' | tee kube-proxy-csr.json

    cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=client kube-proxy-csr.json | cfssljson -bare kube-proxy

    echo '{
      "CN": "admin",
      "hosts": [],
      "key": {
        "algo": "rsa",
        "size": 2048
      },
      "names": [
        {
          "C": "US",
          "L": "San Jose",
          "O": "system:masters",
          "OU": "Cluster",
          "ST": "California"
        }
      ]
    }' | tee admin-csr.json

    cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=client admin-csr.json | cfssljson -bare admin

    count=0
    for ip in $(echo ${MASTER_IPS} | tr "," "\n"); do
    kubectl config set-cluster ${KUBE_CLUSTER_NAME} --certificate-authority=ca.pem --embed-certs=true --server=https://${INTERNAL_IP}:${MASTER_API_HTTPS} --kubeconfig=master${count}.kubeconfig
    kubectl config set-credentials system:node:master${count} --client-certificate=master${count}.pem --client-key=master${count}-key.pem --embed-certs=true --kubeconfig=master${count}.kubeconfig
    kubectl config set-context default --cluster=${KUBE_CLUSTER_NAME} --user=system:node:master${count} --kubeconfig=master${count}.kubeconfig
    kubectl config use-context default --kubeconfig=master${count}.kubeconfig
    count=$((count+1))
    done

    kubectl config set-cluster ${KUBE_CLUSTER_NAME} --certificate-authority=ca.pem --embed-certs=true --server=https://${INTERNAL_IP}:${MASTER_API_HTTPS} --kubeconfig=kube-controller-manager.kubeconfig
    kubectl config set-credentials kube-controller-manager --client-certificate=kube-controller-manager.pem --client-key=kube-controller-manager-key.pem --embed-certs=true --kubeconfig=kube-controller-manager.kubeconfig
    kubectl config set-context default --cluster=${KUBE_CLUSTER_NAME} --user=kube-controller-manager --kubeconfig=kube-controller-manager.kubeconfig
    kubectl config use-context default --kubeconfig=kube-controller-manager.kubeconfig

    kubectl config set-cluster ${KUBE_CLUSTER_NAME} --certificate-authority=ca.pem --embed-certs=true --server=https://${INTERNAL_IP}:${MASTER_API_HTTPS} --kubeconfig=kube-scheduler.kubeconfig
    kubectl config set-credentials kube-scheduler --client-certificate=kube-scheduler.pem --client-key=kube-scheduler-key.pem --embed-certs=true --kubeconfig=kube-scheduler.kubeconfig
    kubectl config set-context default --cluster=${KUBE_CLUSTER_NAME} --user=kube-scheduler --kubeconfig=kube-scheduler.kubeconfig
    kubectl config use-context default --kubeconfig=kube-scheduler.kubeconfig

    kubectl config set-cluster ${KUBE_CLUSTER_NAME} --certificate-authority=ca.pem --embed-certs=true --server=https://${INTERNAL_IP}:${MASTER_API_HTTPS} --kubeconfig=kube-proxy.kubeconfig
    kubectl config set-credentials kube-proxy --client-certificate=kube-proxy.pem --client-key=kube-proxy-key.pem --embed-certs=true --kubeconfig=kube-proxy.kubeconfig
    kubectl config set-context default --cluster=${KUBE_CLUSTER_NAME} --user=kube-proxy --kubeconfig=kube-proxy.kubeconfig
    kubectl config use-context default --kubeconfig=kube-proxy.kubeconfig

    ENCRYPTION_KEY=$(head -c 32 /dev/urandom | base64)
    echo "kind: EncryptionConfig
apiVersion: v1
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: ${ENCRYPTION_KEY}
      - identity: {}" | tee encryption-config.yaml

    echo "@@{CENTOS.secret}@@" | tee ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa

    count=0
    for ip in $(echo ${MASTER_IPS} | tr "," "\n"); do
      instance="master${count}"
      scp -o stricthostkeychecking=no admin*.pem ca*.pem kubernetes*.pem ${instance}* kube-proxy.kubeconfig kube-controller-manager.kubeconfig kube-scheduler.kubeconfig encryption-config.yaml ${instance}:
    count=$((count+1))
    done

  else
    count=0
    while [ ! $(ls $HOME/encryption-config.yaml 2>/dev/null) ] ; do  echo "waiting for certs sleeping 5" && sleep 5; if [[ $count -eq 600 ]]; then echo "failed to download certs" && exit 1; fi; count=$(($count+5)) ; done
  fi

  cd $HOME
  sudo cp ca*.pem kubernetes*.pem ${NODE_NAME}* kube-*.kubeconfig encryption-config.yaml ${KUBE_CERT_PATH}/
  sudo chmod +r ${KUBE_CERT_PATH}/*
fi

sudo systemctl start kubelet 
sudo systemctl enable kubelet
sudo systemctl restart rsyslog

mkdir CA
mv admin*.pem ca*.pem kubernetes*.pem master* kube-*.kubeconfig encryption-config.yaml CA/
if [ @@{calm_array_index}@@ -ne 0 ];then
  exit
fi

cp /opt/kube-ssl/admin*.pem CA/
COUNT=0
while [[ $(curl --key CA/admin-key.pem --cert CA/admin.pem --cacert CA/ca.pem https://${INTERNAL_IP}:${MASTER_API_HTTPS}/healthz) != "ok" ]] ; do
    echo "sleep for 5 secs"
  sleep 5
  COUNT=$(($COUNT+1))
  if [[ $COUNT -eq 50 ]]; then
    echo "Error: creating cluster"
    exit 1
  fi
done

kubectl config set-cluster ${KUBE_CLUSTER_NAME}  --certificate-authority=$HOME/CA/ca.pem  --embed-certs=true --server=https://${INTERNAL_IP}:${MASTER_API_HTTPS}
kubectl config set-credentials admin  --client-certificate=$HOME/CA/admin.pem  --client-key=$HOME/CA/admin-key.pem
kubectl config set-context ${KUBE_CLUSTER_NAME}  --cluster=${KUBE_CLUSTER_NAME}  --user=admin
kubectl config use-context ${KUBE_CLUSTER_NAME}

cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRole
metadata:
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "true"
  labels:
    kubernetes.io/bootstrapping: rbac-defaults
  name: system:kube-apiserver-to-kubelet
rules:
  - apiGroups:
      - ""
    resources:
      - nodes/proxy
      - nodes/stats
      - nodes/log
      - nodes/spec
      - nodes/metrics
    verbs:
      - "*"
EOF

cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: system:kube-apiserver
  namespace: ""
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:kube-apiserver-to-kubelet
subjects:
  - apiGroup: rbac.authorization.k8s.io
    kind: User
    name: kubernetes
EOF
