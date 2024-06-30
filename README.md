# Homelab

## Prerequisites
1. an ansible user provisioned in proxmox
2. an api token provisioned in proxmox
3. NFS for storing our ISO's (`truenas-nfs` in proxmox)

## Quickstart
### From Zero to Cluster

Create and bootstrap a talos vm with the following playbooks:
```sh
# Get the ISO and upload it to our NAS
ansible-playbook ansible/playbooks/upload_talos_iso.yml
# Create the VMs
ansible-playbook ansible/playbooks/provision_talos_cluster.yml
# Bootstrap talos
ansible-playbook ansible/playbooks/bootstrap.yml
```

### Getting Your Kubeconfig

Once the cluster is bootstrapped, you can get your `kubeconfig` by running
```sh
talosctl kubeconfig $HOME/.kube/config
```

## Playbooks

### bootstrap
Creates a kubernetes cluster.

#### Usage
```sh
ansible-playbook ansible/playbooks/bootstrap.yml
```

#### Variable Reference
| Variable | Default Value | Description |
|:---------|:-------------|:-------------|
|`bootstrap_cluster_name`|`"{{ talos.cluster_name }}"`|Name for the cluster|
|`bootstrap_control_plane_endpoint`|`"{{ talos.control_plane.endpoint }}"`|Endpoint of the main initial control plane being bootstrapped|
|`bootstrap_control_plane_ips`|`"{{ groups['k8s_control_planes'] }}"`|Control Plane IPs to bootstrap|
|`bootstrap_worker_ips`|`"{{ groups['k8s_workers'] }}"`|Worker IPs to bootstrap|

### provision_talos_cluster
Creates a series of VMs in proxmox running talos. 

This playbook also reads any existing state and stop already configured VMs prior to applying any TF changes. This ensures that the terraform does not hang due to a failure to shutdown the VM for any reason.

This will create a VM for each provided static IP in `provision_cluster_ips`.

#### Usage
```sh
ansible-playbook ansible/playbooks/provision_talos_cluster.yml --ask-vault-pass
```

#### Variable Reference

| Variable | Default Value | Description |
|:---------|:-------------|:-------------|
|`provision_cluster_image_name`|`"{{ talos.image_src }}{{ talos.image_name }}"`|Image name to use when creating the VMs|
|`provision_cluster_proxmox_token_id`|`"{{ proxmox.token_id }}"`|Api token id for authenticating with proxmox|
|`provision_cluster_proxmox_token_secret`|`"{{ proxmox.token_secret }}"`|Api token secret for authenticating with proxmox|
|`provision_cluster_proxmox_api_url`|`"{{ proxmox.api_url }}"`|Proxmox api url|
|`provision_cluster_ssh_proxmox_private_key`|`"{{ ssh.proxmox_private_key }}"`|SSH Key to provide to the provisioned VMs|
|`provision_cluster_networking_gateway_ip`|`"{{ networking.gateway_ip }}"`|Gateway IP for the VMs|
|`provision_cluster_ips`|`"{{ groups.k8s }}"`|IP addresses of the VMs to create|
|`provision_cluster_operation`|`"apply"`|Whether to create or destroy the cluster. Can be `apply` or `destroy`|

### upload_talos_iso
Downloads a talos ISO and uploads it to the NAS.

#### Usage
```sh
ansible-playbook ansible/playbooks/upload_talos_iso.yml
```

#### Variable Reference

| Variable |Default Value | Description |
|:---------|:-------------|:------------|
|`download_iso_download_url`|`"{{ talos.download_url }}"`|Location to download the iso from|
|`download_iso_out_dir`|`"{{ local.out_dir }}"`|Location to download the iso to|
|`download_iso_image_name`|`"{{ talos.image_name }}"`|Name to give the image|
|`upload_iso_src`|`"{{ hostvars['localhost']['download_iso_cloud_image_dest'] }}"`|Source file to upload. Should include the absolute path|
|`upload_iso_dest`|`/mnt/pool/proxmox-data/template/iso`|Location to upload the file to on the remote host|
|`upload_iso_filename`|`"{{ talos.image_name }}"`|Filename of the file being uploaded|

