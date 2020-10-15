![KPS!](icn-karbon-color.png "KPS")

# Karbon Platform Services

## Overview
Karbon Platform Services (KPS) is a Kubernetes based multi-cloud PaaS that enables rapid development and deployment of microservices-based applications ranging from simple stateful containerized applications to complex AI, IoT and hybrid applications across any cloud. KPS eliminates complexity, accelerates deployments, and elevates developers to focus on the business logic powering applications and services.

## Getting Started
If you're not already a customer, resources found here can be leveraged in minutes by starting a free trial of Karbon Platform Services.

### Signing up for a Karbon Platform Services trial
Do any of these steps to sign up for a Karbon Platform Services trial.
1. Sign up at [https://www.nutanix.com/products/karbon-platform-services/free-trial](https://www.nutanix.com/products/karbon-platform-services/free-trial).
1. If you already have a My Nutanix account, log on to [https://my.nutanix.com](https://my.nutanix.com) with your existing account credentials and click Launch in the Karbon Platform Services panel.

**Logging in to the Karbon Platform Services Mangement Console**

Before you begin:

Supported web browsers include the current and two previous versions of Google Chrome. You’ll need your My Nutanix credentials for this step.
* Open [https://karbon.nutanix.com/](https://karbon.nutanix.com/) in a web browser, click **Log in with My Nutanix** and log in with your My Nutanix credentials.
* If you are logging on for the first time, click to read the Terms and Conditions, then click to Accept and Continue.
* Take a few moments to read about Karbon Platform Services, then click Get Started.

## Using this Blueprint
Use this Calm Blueprint to deploy a Single or Multinode Service Domain on Nutanix AHV (IPAM required).

### Getting Started
1. Download the required Service Domain Image named "Service Domain VM QCOW2 File for AHV" from the Nutanix Support Portal here: https://portal.nutanix.com/page/downloads?product=karbonplatformservices.
1. After logging into the Karbon Platform Services Cloud Management Console, create an API Token by clicking on your username in the upper right corner and selecting **Manage API Keys**.
1. Launch the Blueprint.

Note that creating a Multinode Service Domain requires the following additional information:
  - Additional free VirtualIP for the Service Domain
  - Prism Element Credentials
  - Data Services IP
  - Storage Container

Credits to @davehocking and @wolfganghuse for the initial development and updates.

