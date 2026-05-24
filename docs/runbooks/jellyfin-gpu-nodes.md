---
status: current
scope:
  - jellyfin
  - gpu
  - talos
  - terraform
last_verified: 2026-05-24
---

# Jellyfin GPU Nodes

Jellyfin hardware transcoding nodes are prepared by Terraform before any Jellyfin workload scheduling change. The Proxmox VM layer attaches a cluster-specific PCI hardware mapping, and the Talos bootstrap layer applies stable Kubernetes node labels through `machine.nodeLabels`.

Proxmox PCI hardware mappings are cluster-scoped, so each Terraform root must own a distinct mapping name. Production owns `jellyfin-igpu` with only the pve01 and pve02 entries. Development owns `jellyfin-igpu-dev` with only the pve04 entry.

Expected Jellyfin-capable nodes:

| Cluster | Mapping | Proxmox host | VMID | Address |
| --- | --- | --- | --- | --- |
| production | `jellyfin-igpu` | `pve01` | `160` | `192.168.30.160` |
| production | `jellyfin-igpu` | `pve02` | `161` | `192.168.30.161` |
| development | `jellyfin-igpu-dev` | `pve04` | `170` | `192.168.30.170` |

Each Talos node should have these stable labels:

- `homelab.petebeegle.com/proxmox-host`
- `homelab.petebeegle.com/vm-id`
- `homelab.petebeegle.com/machine-type`
- `homelab.petebeegle.com/jellyfin-igpu=true` on the Jellyfin-capable nodes only

## Readiness Checks

Confirm the labels without depending on generated Kubernetes node names:

```sh
kubectl get nodes --show-labels | grep 'homelab.petebeegle.com/jellyfin-igpu=true'
kubectl get nodes -l homelab.petebeegle.com/jellyfin-igpu=true -o wide
```

Confirm Talos can see the passed-through render devices before scheduling Jellyfin onto GPU nodes:

```sh
talosctl --nodes 192.168.30.160 ls /dev/dri
talosctl --nodes 192.168.30.161 ls /dev/dri
```

For development validation, check the single development VM:

```sh
talosctl --nodes 192.168.30.170 ls /dev/dri
kubectl get nodes -l homelab.petebeegle.com/jellyfin-igpu=true -o wide
```

If `/dev/dri` is missing after the VM has the `hostpci` mapping, verify the Proxmox host has IOMMU enabled, the VM has been fully stopped and started, and the mapping entry matches the VM's current Proxmox host.

## Rollout Notes

Production rollout should be one worker at a time. Do not rely on generated Talos/Kubernetes node names; select nodes by the stable VMID label:

```sh
NODE=$(kubectl get node -l homelab.petebeegle.com/vm-id=160 -o jsonpath='{.items[0].metadata.name}')
kubectl drain "$NODE" --ignore-daemonsets --delete-emptydir-data
```

Apply the Terraform change, then fully stop and start the VM through Proxmox if the PCI device was added while the VM was running. A guest-only reboot may not be enough for new PCI passthrough hardware. After the node returns:

```sh
talosctl health --nodes 192.168.30.160
talosctl --nodes 192.168.30.160 ls /dev/dri
kubectl wait node "$NODE" --for=condition=Ready --timeout=10m
kubectl uncordon "$NODE"
```

Repeat the same sequence for VMID `161` and address `192.168.30.161`. Run the development VMID `170` sequence first when validating this path in the development cluster; if development credentials or an approved VM restart window are unavailable, record that exception with `terraform validate`, `terraform plan`, and local render evidence instead of making production live changes.
