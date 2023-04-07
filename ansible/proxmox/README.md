## Example 

```sh
# upgrade node
ansible-playbook -i hosts -v upgrade.yml --ask-pass

# provision users/ssh keys on node
ansible-playbook -i hosts -v provision.yml --ask-pass
```
