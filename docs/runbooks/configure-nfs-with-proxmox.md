# Configure NFS With Proxmox

Proxmox needs access to the NFS server for Talos images, and the Terraform host
needs access to Proxmox.

## Prerequisites

- Proxmox
- Synology NAS running DSM 7.0 or newer

## Configure Synology NFS

Follow Synology's NFS setup guide:
<https://kb.synology.com/en-us/DSM/tutorial/How_to_access_files_on_Synology_NAS_within_the_local_network_NFS>

Example NFS rule ranges:

- `192.168.30.0/24`: homelab VLAN
- `172.17.0.0/16`: local devcontainer subnet

## Connect Proxmox To NFS

In Proxmox, select `Datacenter > Storage > Add > NFS`.

| Field | Value | Description |
| --- | --- | --- |
| ID | `nfs` | Storage ID referenced by Proxmox |
| Server | `192.168.30.100` | NAS IP |
| Export | `/volumeX/lab/proxmox` | Remote mount location |
| Content | Disk image, ISO image, Snippets, Container template | Stored artifact types |

## Configure A Mount User

From a Proxmox shell:

```sh
useradd -m nfsuser
groupadd nfs
usermod -aG nfs nfsuser

chown -R :nfs /mnt/pve/nfs
chmod -R 775 /mnt/pve/nfs
chmod g+s /mnt/pve/nfs
```

## Configure Terraform

Set the NFS host and user in the cluster Terraform workspace:

```sh
echo 'nfs_host = "192.168.30.100"' >> /workspaces/homelab/terraform/cluster/terraform.tfvars
echo 'nfs_user = "nfsuser"' >> /workspaces/homelab/terraform/cluster/terraform.tfvars
```
