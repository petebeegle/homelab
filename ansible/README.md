```sh
# create a vault (all or specific group)
ansible-vault create inventories/swarm/group_vars/all/vault.yml

# run playbook
ansible-playbook site.yml --ask-vault-pass
```
