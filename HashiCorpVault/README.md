## HashiCorp Vault Deployment
This Calm blueprint deploys [Vault High Availability with Consul](https://learn.hashicorp.com/vault/operations/ops-vault-ha-consul), which consists of 3 Consul VMs, and 2 Vault VMs, running on CentOS 7.

To use this blueprint, import into a Prism Central running >= Calm 2.6.0, and fill in the Credentials and Variables mentioned below.  Once deployed, the vault will need to be [initialized](https://learn.hashicorp.com/vault/getting-started/deploy.html#initializing-the-vault), and the keys must be stored in a secure location.  The initialization API call will be provided on the application overview page.  Once initialized, there are custom actions defined to seal and unseal the vault.

##### Credentials
* CentOS_Key: the SSH Private Key to be used on the five CentOS 7 VMs

##### Variables
* INSTANCE_PUBLIC_KEY: The matching SSH Public key, which in conjunction allow Calm to SSH to the VMs
* ui: If set to 'true', the Vault user interface will be installed.  If the UI is not desired, set to 'false'.
* secret_shares: Specifies the number of shares to split the master key into.
* secret_threshold: Specifies the number of shares required to reconstruct the master key. This must be less than or equal to 'secret_shares'.

