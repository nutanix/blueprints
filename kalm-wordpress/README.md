# Nutanix Kalm & WordPress

This Nutanix Kalm blueprint will deploy a simple stateless WordPress content management system on Kubernetes.

**Note:** The reason to call it Kalm, Kubernetes Application Lifecycle Management, is because this blueprint is a Kubernetes application. The Nutanix product name is Calm, this is just to difference if we are talking about a native Kubernetes app.

## Mandatory Requirements Section

- Created on Prism Central 5.10.  Tested on 5.10
- Minimum Calm version is 2.4.0
- A Kubernetes cluster is required
- The project must have configured a Kubernetes cluster
- Tested on Nutanix Karbon TP only but should work the same way on any platform that supports native Kubernetes API
- Minimum hardware requirements: few resources, CPU and memory, available on your Kubernetes cluster
- Variables: MySQL password, WordPress version, WordPress Kubernetes service type, Kubernetes namespace
- Credentials: They are configured at the global level in Calm (no credentials at the blueprint level)
- Minimum # of Pods required: 2
- Actions: Default
- Custom actions: Scale Out/In WordPress frontend i.e. scale out from 1 to 2 WordPress frontend pods.
- License information: No licenses required
- Network information: Kubernetes environment will require Internet connection for image downloads

## Components

- 1x MySQL pod (nonpersistent)
- 1x WordPress pod (nonpersistent) that is the PHP web application

## Prerequisites

To deploy these blueprints you will need the following things available:

- A Kubernetes cluster with native API
- A Calm project with a Kubernetes cluster
- A Kubernetes namespace must exists before you can deploy the application

## Usage

- Import the blueprint into your Nutanix Calm environment
- Adjust the Kubernetes cluster in the pods
- Launch the Kalm-WordPress blueprint
- Fill in all required runtime variables. WORDPRESS_SERVICE_TYPE variable accepts the values **NodePort** (default)) or **LoadBalancer**
- After deployment, run *kubectl* to retrieve the Kubernetes service NodePort or the LoadBalancer IP address
- Scale out with an extra pod the WordPress frontend tier using the action Scale Out
- Check with *kubectl* you are running two replicas of the wordpress tier now

## Support

These blueprints are *unofficial* and are not supported or maintained by Nutanix in any way.

In addition, please also be advised that these blueprints may deploy applications that do not follow best practices.  Please check through each blueprint to ensure the configuration suits your requirements.

***Changes will be required before these application blueprints can be used in production environments.***