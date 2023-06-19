```sh
# create a vault (all or specific group)
ansible-vault create inventories/swarm/group_vars/all/vault.yml --vault-pass-file vault.pwd
```

### Manage Proxmox Nodes
```sh
# upgrade proxmox os and apt source list
ansible-playbook proxmox_manage.yml
```

### Manage a user and ssh keys
```sh
# create working user
ansible-playbook user_manage.yml

# delete working user
ansible-playbook user_manage.yml -e "manage=delete"
```
