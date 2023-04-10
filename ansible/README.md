1. Create a vault:
```sh
# create a vault (all or specific group)
ansible-vault create group_vars/all/vault.yml

# run playbook
ansible-playbook playbooks/swarm.yml --ask-vault-pass
```