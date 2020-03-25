# Nutanix Kalm & Persistent Volume Claim

This Nutanix Kalm blueprint will create a Persistent Volume Claim and deploy a BusyBox pod to mount the volume.

**Note:** The reason to call it Kalm, Kubernetes Application Lifecycle Management, is because this blueprint is a Kubernetes application. The Nutanix product name is Calm, this is just to difference if we are talking about a native Kubernetes app.

## Mandatory Requirements Section

- Created on Prism Central 5.16.1.  Tested on 5.16.1
- Minimum Calm version is 2.9.8
- A Kubernetes cluster is required (This blueprint uses a Karbon K8s cluster)
- The project must have configured a Kubernetes cluster
- Tested on Nutanix Karbon 2.0 only but should work the same way on any platform that supports native Kubernetes API
- Minimum hardware requirements: few resources, CPU and memory, available on your Kubernetes cluster
- Variables: kube_namespace, kube_pvc_name, kube_pvc_storageClass, kube_pvc_accessMode, kube_pvc_size, kube_calm_sa_token, kubemaster_ip
- Credentials: there is a dummy credential. Just complete the password with a dummy one too.
- Minimum # of Pods required: 1
- Actions: Default
- Custom actions: Scale Out i.e. scale out from 1 to 2 BusyBox pods. When scaling out the PVC is only mounted to a single pod.
- License information: No licenses required
- Network information: Kubernetes environment will require Internet connection for image downloads

## Components

- 1x BusyBox pod (persistent)

## Prerequisites

To deploy this blueprint you will need the following things available:

- A Kubernetes cluster with native API (Preferable Karbon because Dynamic Storage Provisioning)
- A Calm project with a Kubernetes cluster (Karbon in this example)
- A Kubernetes namespace must exists before you can deploy the application (this is using the default namespace)

## Usage

- Import the blueprint into your Nutanix Calm environment
- Adjust the Kubernetes cluster in the pods
- Launch the blueprint
- Fill in all required runtime variables.
- After deployment, run *kubectl* to retrieve the Kubernetes pod
- Connect to the running pod with *kubectl exec -it <pod_name> sh*
- In the pod shell, run *df -h* to list the disks and partitions. You will see the PVC mounted in the path /var/lib/mysql
- The BusyBox pod has a sleep of 1000 seconds. After this time the pod is destroyed.

## Support

These blueprints are *unofficial* and are not supported or maintained by Nutanix in any way.

In addition, please also be advised that these blueprints may deploy applications that do not follow best practices.  Please check through each blueprint to ensure the configuration suits your requirements.

***Changes will be required before these application blueprints can be used in production environments.***