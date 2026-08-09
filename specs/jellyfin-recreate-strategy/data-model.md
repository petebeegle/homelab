# Data Model: Deployment Strategy Transition

## Existing live strategy

- Type: `RollingUpdate`
- Rolling-update settings: present
- Workload: healthy pre-migration Jellyfin deployment

## Desired transition payload

- Type: `Recreate`
- Rolling-update settings: explicit null/clear
- Invariant: no other Jellyfin values change

## Accepted live strategy

- Type: `Recreate`
- Rolling-update settings: absent after API processing
- Workload: migration init runs before SSO bootstrap and application startup

## Rollback state

- The old NFS config PVC remains declared and retained.
- Helm rollback may restore the old Deployment if a later stage fails.
