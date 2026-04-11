# Storage — Synology CSI / NFS

## Key constraints

- **StorageClass:** Always `nfs-csi-storage`
- **Volume type:** Use Btrfs volumes on the NAS — ext4 lacks quota support
- **NFS version:** v4.1 recommended for RWX (multi-pod) volumes
- **NAS IP:** `192.168.30.99`
- **Synology CSI** runs in `dataplane` ns and must be healthy before any PVC workload can schedule

## PVC troubleshooting

```bash
kubectl get storageclass
kubectl describe pvc <name> -n <namespace>
kubectl logs -n dataplane -l app=synology-csi-node
```

## Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Couldn't find any host available" | Subfolder bug in older CSI versions | Ensure volumes are at root, not in subfolders |
| PVC stuck `Pending` | NFS export permissions wrong | Add worker node CIDR to NFS export allow-list |
| Mount failures | NFS v4.1 unreachable | Verify `192.168.30.99` accessible from node subnet |
| UID/GID mismatch | Container user ≠ NFS permissions | Set `securityContext.fsGroup` to match NFS export |
| ext4 quota errors | Wrong volume type | Recreate volume as Btrfs on DSM |

## NFS export requirements

- Allow homelab VLAN: `192.168.30.0/24`
- Allow devcontainer subnet: `172.17.0.0/16` (if developing locally)
- Btrfs volume required for quota and shared folder support
