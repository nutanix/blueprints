# Anthos on AHV

This blueprint will deploy a hybrid Anthos cluster on AHV.

**Note** There are costs associated to Google Cloud - [Anthos](cloud.google.com/anthos/pricing)

The official repo with the DSL code and more details can be found [here](https://github.com/nutanixdev/anthos-on-ahv/tree/main/calm)

## Components

The characteristics for the Kubernetes cluster are:

* Anthos version: bare metal

  * Supported [1.6.x, 1.7.x, 1.8.x and 1.9.x](https://cloud.google.com/anthos/clusters/docs/bare-metal/1.6/concepts/about-bare-metal)

  * Unsupported [1.10.x](https://cloud.google.com/anthos/clusters/docs/bare-metal/1.7/concepts/about-bare-metal)

* Type: hybrid - <https://cloud.google.com/anthos/clusters/docs/bare-metal/1.6/installing/install-prep#hybrid_cluster_deployment>

* Number of virtual machines: 6 (Total resources: 24 vCPU / 192 GB memory / 768 GB storage )

  * 1 x Admin

  * 3 x Control plane

  * 2 x Worker nodes

* Virtual machine OS: CentOS 8 GenericCloud - <https://cloud.centos.org/centos/8/x86_64/images/CentOS-8-GenericCloud-8.2.2004-20200611.2.x86_64.qcow2>

  * IMPORTANT: CentOS 8.2.2004 used in this blueprint is EOL. The blueprint is using vault.centos.org repository for packages.

* High availability: yes

* Load balancing: yes (bundled)

* Ingress: yes

* Persistent storage: yes (Nutanix CSI)

* Proxy: no

* KubeVirt: no

* OpenID Connect: no

* Application logs/metrics: no

* Scale Out/In: yes

* Upgrade Anthos version: yes

* Decommission Anthos cluster: yes

## Prerequisites

To deploy this blueprint you will need the following things available:

* Nutanix:

  * Cluster:

    * AHV: 20201105.1045 or later

    * AOS: 5.19.1 or later

    * iSCSI data service IP configured

    * VLAN network with AHV IPAM configured

    * Prism Central: 2020.11.0.1 or later

    * Calm:

      * Version: 3.0.0.2 or later

      * A project with AHV provider

* Google Cloud:

  * A project with Owner role

  * The project must have enabled Monitoring - <https://console.cloud.google.com/monitoring>

  * A service account - <https://console.cloud.google.com/iam-admin/serviceaccounts/create>

    * Role: Project Owner

    * A private key: JSON

* Networking:

  * Internet connectivity

  * AHV IPAM: Minimum 6 IP addresses available for the virtual machines

  * Kubernetes:

    * Control plane VIP: One IP address in the same network than virtual machines but not part of the AHV IPAM

    * Ingress VIP: One IP address in the same network than virtual machines but not part of the AHV IPAM. This IP must be part of the load balancing pool

    * Load balancing pool: Range of IP addresses in the same network than virtual machines but not part of the AHV IPAM. The Ingress VIP is included in this pool

    * Pods network: CIDR network with enough IP addresses, usually /16 and not sharing the same network than virtual machines or Kubernetes Services. If your containerized application must communicate with a system out of the Kubernetes cluster, make sure then this network doesn't overlap either with the external system network

    * Services network: CIDR network with enough IP addresses, usually /16 and not sharing the same network than virtual machines or Kubernetes Pods. If your containerized application must communicate with a system out of the Kubernetes cluster, make sure then this network doesn't overlap either with the external system network

* Credentials:

  * Operating system: you need a SSH key. It must start with `---BEGIN RSA PRIVATE KEY---`. To generate one in a terminal:

    ```console
    ssh-keygen -m PEM -t rsa -f <keyname>
    ```

    * Prism Element: an account, local or Active Directory, with *User Admin* role. This is for the CSI plugin configuration

## Usage

* Import the blueprint into your environment

* Adjust virtual machines network, credentials, and application profile variables for *Create* stage

* Launch the blueprint

* After deployment, follow the steps in the application overview to retrieve the token required for GKE. Once you introduced the token in GKE, you will get full access via GKE UI and able to use the GKE marketplace to deploy applications

* (Optional) You can also add this Kubernetes cluster in Calm as an account and use it with your projects. You can use the same service account token that you used for GKE in the previous step

## Support

These blueprints are *unofficial* and are not supported or maintained by Nutanix in any way.

In addition, please also be advised that these blueprints may deploy applications that do not follow best practices.  Please check through each blueprint to ensure the configuration suits your requirements.

***Changes will be required before these application blueprints can be used in production environments.***
