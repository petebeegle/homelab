# Configure NFS with Proxmox
In order to upload talos images, proxmox needs access to the nfs server and the host running terraform needs access to proxmox.

## Prerequisites
- Proxmox
- Synology NAS running DSM 7.0

## Configure NFS for Synology
See: [How to access files on Synology NAS within a local network (NFS)](https://kb.synology.com/en-us/DSM/tutorial/How_to_access_files_on_Synology_NAS_within_the_local_network_NFS).

When creating NFS rules for my shared folder, I opted to expose 2 IP address ranges, provided below as an example:
- `192.168.30.0/24`: This is the subnet assigned to the VLAN for my homelab
- `172.17.0.0/16`: The subnet for the devcontainer I work out of

## Configure proxmox to connect to NFS

Select `Datacenter > Storage > Add > NFS`'

|field|value|description|
|---|---|---|
|ID|nfs|Name to be referenced in the file structure|
|Server|`192.168.30.100`|IP of the NAS|
|Export|`/volumeX/lab/proxmox`|Remote mount location|
|Content|Disk image, ISO image, Snippets, Container template|Things to store|

## Configure a user for accessing the mount
Within a proxmox shell, we will create a user and give it access to the mount location.
```shell
# Create the user and group, and associate them
useradd -m nfsuser
groupadd nfs
usermod -aG nfs nfsuser

# Update the file permissions and ensure that new folders/files inherit the proper permissions
chown -R :nfs /mnt/pve/nfs
chmod -R 775 /mnt/pve/nfs
chmod g+s /mnt/pve/nfs
```

## Configure the terraform module
Ensure that terraform is configured for the correct user:
```shell
echo 'nfs_host = "192.168.30.100"' >> /workspaces/homelab/terraform/cluster/terraform.tfvars
echo 'nfs_user = "nfsuser"' >> /workspaces/homelab/terraform/cluster/terraform.tfvars
```
