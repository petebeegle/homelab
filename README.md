# Homelab

## Prerequisites
1. an ansible user provisioned in proxmox
2. an api token provisioned in proxmox

## Creating the cluster

### Create talos vms

First provision your VMs
```sh
cd ansible
ansible-playbook -i inventory/hosts provision-vm.yml --ask-vault-pass
```

Next, decide which of the above VMs should be the control and which should be the workers.

Then run
```sh
cd ansible
ansible-playbook -i inventory/hosts create-k8s-cluster.yml -e "control_plane_ip=<foo>" -e "worker_ips=<bar>,<quz>"
```

Once this script finishes, wait a few minutes and the cluster should come up!