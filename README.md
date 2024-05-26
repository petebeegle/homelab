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
