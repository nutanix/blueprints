# Azure SDK - Boot diagnostics

This blueprint will deploy a single VM with CentOS in Azure and enable Boot diagnostics.

**Note:** This blueprint demonstrate how to use the Azure SDK available in Calm since version 2.9.7.

## Mandatory Requirements Section

- Created on Prism Central 5.16.1.  Tested on 5.16.1
- Minimum Calm version is 2.9.8
- Azure provider is required
- The project must have configured an Azure provider
- Variables: azure_subscription_id, azure_client_id, azure_tenant_id, azure_secret, azure_storage_account_name
- Credentials: SSH user and password must be set
- Actions: Default
- License information: No licenses required

## Components

- 1x CentOS virtual machine

## Prerequisites

To deploy these blueprints you will need the following things available:

- A project with Azure provider
- Azure network configured to allow public IP access (optional: disable check log-in to avoid public IP req.)

## Usage

- Import the blueprint into your Nutanix Calm environment
- Adjust the Azure resource group, template and networks. OpenLogic provides a CentOS template
- Launch the blueprint
- Fill in all required runtime variables.
- After deployment, in Azure portal check if Boot diagnostics is enabled for the provisioned VM

## Support

These blueprints are *unofficial* and are not supported or maintained by Nutanix in any way.

In addition, please also be advised that these blueprints may deploy applications that do not follow best practices.  Please check through each blueprint to ensure the configuration suits your requirements.

***Changes will be required before these application blueprints can be used in production environments.***
