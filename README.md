# Homelab

## Prerequisites
1. an ansible user provisioned in proxmox
2. an api token provisioned in proxmox

### Create a vault

Create a new file for your vault password. 
Update values as needed prior to encrypting.

```sh
cd ansible
echo "replace-me" > .vault_pass
cp secrets.yml.example secrets.yml
ansible-vault encrypt secrets.yml
```

## Quickstart

🚧

## Playbook Reference

### create-ubuntu-template
Create a VM template in proxmox based on ubuntu-2004.

#### Usage
```sh
ansible-playbook ansible/create-ubuntu-template.yml
```

#### Variable Reference

| Variable | Default Value | Description |
|:----------|:-------------|:---------------|
| `create_template_name`     | `cloudinit-template` | Template name |
| `create_template_id`     | `9000` | Template Id |
| `create_template_memory`     | `8` | Amount of memory for template in GB |
| `create_template_cores`     | `2` | Number of cores to provision to the template |


### create-vm
Create one or more VMs for a given template.

#### Usage
```sh
ansible-playbook ansible/create-vm.yml -e number_of_instances=3 -e template_name=cloudinit-template
```

#### Variable Reference

| Variable | Default Value | Description |
|:----------|:-------------|:---------------|
| `number_of_instances`     | null | Number of instances to create |
| `template_name`     | null | Name of the template to clone |
| `create_vm_proxmox_api_url` | `https://host:8006/api2/json` | API endpoint to operate against |
| `create_vm_ssh_key`* | null | SSH Key to configure for the VM |
> *: `create_vm_ssh_key` is set in `secrets.yml`.
