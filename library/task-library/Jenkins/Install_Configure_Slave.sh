#!/bin/bash
set -ex

##############################################
# Name        : Install_Configure_Slave.sh
# Author      : Nutanix Calm
# Version     : 1.0
# Description : Script is used to bootstrap Jenkins Slave
# Compatibility : Centos 7
##############################################

# - * - Variables and constants.
JENKINS_URL=http://@@{Jenkins_Master.address}@@:8080
NODE_NAME=@@{address}@@
NODE_SLAVE_HOME='/home/centos'
EXECUTORS=1
SSH_PORT=22
CRED_ID=Jenkins_Slave
LABELS=build
USERID=admin

#Download and install jenkins-cli
sudo yum -y install wget
sudo wget http://${JENKINS_URL}/jnlpJars/jenkins-cli.jar

#Create Jenkins credential

echo "Creating credential"

echo '<com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey plugin="ssh-credentials@1.13">
  <scope>GLOBAL</scope>
  <id>Jenkins_Slave</id>
  <description></description>
  <username>@@{CENTOS.username}@@</username>
  <privateKeySource class="com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource">
    <privateKey>
    @@{CENTOS.secret}@@
    </privateKey>
  </privateKeySource>
</com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>' | sudo java -jar jenkins-cli.jar -s "${JENKINS_URL}"  -http -auth ${USERID}:@@{Jenkins_Master.authpwd}@@ create-credentials-by-xml system::system::jenkins _

echo "Creating slave node"

#Create Jenkins Slave Node
cat <<EOF | sudo java -jar jenkins-cli.jar -s "${JENKINS_URL}" -http -auth ${USERID}:@@{Jenkins_Master.authpwd}@@ create-node ${NODE_NAME}
<slave>
  <name>${NODE_NAME}</name>
  <description></description>
  <remoteFS>${NODE_SLAVE_HOME}</remoteFS>
  <numExecutors>${EXECUTORS}</numExecutors>
  <mode>NORMAL</mode>
  <retentionStrategy class="hudson.slaves.RetentionStrategy$Always"/>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher" plugin="ssh-slaves@1.21">
    <host>${NODE_NAME}</host>
    <port>${SSH_PORT}</port>
    <credentialsId>${CRED_ID}</credentialsId>
    <maxNumRetries>0</maxNumRetries>
    <retryWaitTime>0</retryWaitTime>
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.NonVerifyingKeyVerificationStrategy"/>
  </launcher>
  <label>${LABELS}</label>
  <nodeProperties/>
</slave>
EOF

