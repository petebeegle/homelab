---
name: storage
description: Synology CSI storage reference for this homelab. Invoke when troubleshooting PVCs, stuck Pending volumes, NFS mount failures, StorageClass issues, or when adding persistent storage to an application. Also invoke for NFS export permission questions.
---

## Troubleshooting

Use the `kubernetes` MCP for pod logs and resource inspection, fall back to CLI when needed:
```bash
# Check StorageClass
kubectl get storageclass

# Describe stuck PVC
kubectl describe pvc <name> -n <namespace>
```

**Common issues:**
- "Couldn't find any host available": Subfolder bug in some versions - CSI volumes must be at volume root
- PVC stuck Pending: Check NFS export permissions, ensure CIDR covers all worker node IPs
- Mount failures: Verify NFS v4.1 connectivity from nodes to NAS (192.168.30.99)
- UID/GID mismatch: Container user doesn't match NFS export permissions
- ext4 volumes lack quota support - use Btrfs volumes

**NFS export requirements:**
- Allow homelab VLAN (192.168.30.0/24)
- Allow devcontainer subnet (172.17.0.0/16) if developing locally
- Use Btrfs volumes for quota/shared folder support

## Research Resources

1. **GitHub:** https://github.com/SynologyOpenSource/synology-csi
2. **Requirements:** DSM 7.0+, Btrfs volume (ext4 lacks quota support)
3. **Protocol:** NFS v4.1 recommended for multi-pod access (RWX)
