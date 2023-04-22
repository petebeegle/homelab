```sh
cd ansible

# install collections
ansible-galaxy collection install --upgrade -r content/collections/requirements.yml

# create a vault (all or specific group)
ansible-vault create inventories/swarm/group_vars/all/vault.yml --vault-pass-file vault.pwd

# bootstrap entire homelab
ansible-playbook site.yml

# create swarm with glusterfs
ansible-playbook swarm_setup.yml

# deploy to existing swarm
ansible-playbook swarm_deploy.yml
```
