# Graph Report - .  (2026-04-19)

## Corpus Check
- Corpus is ~2,438 words - fits in a single context window. You may not need a graph.

## Summary
- 58 nodes · 69 edges · 8 communities detected
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 5 edges (avg confidence: 0.83)
- Token cost: 4,200 input · 2,800 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Homelab Overview & NFS|Homelab Overview & NFS]]
- [[_COMMUNITY_Terraform External Services|Terraform External Services]]
- [[_COMMUNITY_Kubernetes Network Stack|Kubernetes Network Stack]]
- [[_COMMUNITY_Terraform Cluster Provisioning|Terraform Cluster Provisioning]]
- [[_COMMUNITY_TLS Certificate Management|TLS Certificate Management]]
- [[_COMMUNITY_Claude MCP Dev Environment|Claude MCP Dev Environment]]
- [[_COMMUNITY_Persistent Storage (CSI)|Persistent Storage (CSI)]]
- [[_COMMUNITY_Cloudflare Tunnel|Cloudflare Tunnel]]

## God Nodes (most connected - your core abstractions)
1. `Homelab Project` - 10 edges
2. `Synology NAS (DSM)` - 9 edges
3. `Terraform Cluster Module (README)` - 7 edges
4. `Homelab Stack Overview` - 6 edges
5. `GitOps Dependency Chain` - 6 edges
6. `Gateway API` - 5 edges
7. `Proxmox Hypervisor` - 4 edges
8. `SOPS Secret Encryption` - 4 edges
9. `Cilium CNI` - 4 edges
10. `Terraform External Workspaces` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Synology NAS (DSM)` --semantically_similar_to--> `NFS Storage (Proxmox ISO store)`  [INFERRED] [semantically similar]
  scripts/SYNOLOGY.md → README.md
- `Terraform External (Nexus)` --semantically_similar_to--> `Terraform External Workspaces`  [INFERRED] [semantically similar]
  scripts/NEXUS.md → CLAUDE.md
- `Homelab Project` --references--> `Runbook: Resize PVC`  [EXTRACTED]
  README.md → runbooks/resize_pvc.md
- `Homelab Project` --references--> `Runbook: Cloudflare Tunnels`  [EXTRACTED]
  README.md → runbooks/cloudflare_tunnels.md
- `Terraform Provider: bpg/proxmox 0.97.1` --manages--> `Proxmox Hypervisor`  [EXTRACTED]
  terraform/cluster/README.md → README.md

## Hyperedges (group relationships)
- **GitOps Bootstrap Dependency Chain: crds → controllers → network → apps** — claude_gitops_dep_chain, claude_gateway_api, claude_cilium, claude_certmanager, claude_synology_csi, claude_authentik, claude_monitoring_stack [EXTRACTED 1.00]
- **Certificate provisioning: Cloudflare token + certadmin user + Let's Encrypt → TLS certs on NAS/Unifi** — synology_cloudflare_token, synology_certadmin_user, synology_cert_renewal, unifi_certificate, unifi_cloudflare_token [INFERRED 0.80]
- **Cluster provisioning: Terraform modules provision Proxmox VMs with Talos OS and bootstrap FluxCD** — tfcluster_kubernetes_nodes_module, tfcluster_talos_bootstrap_module, tfcluster_talos_provision_module, readme_proxmox, readme_talos_os, readme_fluxcd [INFERRED 0.85]

## Communities

### Community 0 - "Homelab Overview & NFS"
Cohesion: 0.19
Nodes (14): .sops.yaml Config, Homelab Stack Overview, Runbook: Cloudflare Tunnels, Proxmox nfsuser account, Runbook: Configure NFS with Proxmox, Age Encryption Key, FluxCD GitOps Controller, GitHub Personal Access Token (+6 more)

### Community 1 - "Terraform External Services"
Cohesion: 0.22
Nodes (11): Terraform External Workspaces, Docker Registry (Nexus proxy), Nexus Repository Server, Synology Dependency for Nexus, Terraform External (Nexus), NAS IP 192.168.30.100 (Proxmox NFS), Synology NFS Export Config, NFS Storage (Proxmox ISO store) (+3 more)

### Community 2 - "Kubernetes Network Stack"
Cohesion: 0.36
Nodes (8): Authentik SSO/IdP, Cert-manager, Cilium CNI, Gateway API, GitOps Dependency Chain, Monitoring Stack (Grafana/Loki/Mimir/Alloy), Rationale: No traditional Ingress resources, Unifi External Service (Cilium Gateway)

### Community 3 - "Terraform Cluster Provisioning"
Cohesion: 0.29
Nodes (7): Terraform Provider: bpg/proxmox 0.97.1, Terraform Module: kubernetes_nodes (vm), Terraform Output: kubeconfig, Terraform Output: talosconfig, Terraform Cluster Module (README), Terraform Module: talos_bootstrap, Terraform Module: talos_provision

### Community 4 - "TLS Certificate Management"
Cohesion: 0.33
Nodes (6): Synology Certificate Auto-Renewal Task, Synology certadmin User, Cloudflare API Token (Synology DNS), Unifi TLS Certificate (Let's Encrypt), Cloudflare API Token (DNS Edit), Terraform Environment (Cloudflare DNS)

### Community 5 - "Claude MCP Dev Environment"
Cohesion: 0.4
Nodes (5): MCP Tool Priority Policy, Rationale: kubernetes vs grafana MCP separation, Dev Container Environment, Grafana MCP Service Account, Kubernetes MCP Server

### Community 6 - "Persistent Storage (CSI)"
Cohesion: 0.5
Nodes (4): StorageClass nfs-csi-storage, Synology CSI Driver, Runbook: Resize PVC, StorageClass volume expansion requirement

### Community 7 - "Cloudflare Tunnel"
Cohesion: 0.67
Nodes (3): cloudflared Tunnel Daemon, ConfigMap/cloudflared tunnel config, Secret/tunnel-credentials (cloudflared)

## Knowledge Gaps
- **26 isolated node(s):** `Age Encryption Key`, `GitHub Personal Access Token`, `Renovate Dependency Updater`, `Kubernetes MCP Server`, `Dev Container Environment` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Homelab Project` connect `Homelab Overview & NFS` to `Terraform External Services`, `Persistent Storage (CSI)`?**
  _High betweenness centrality (0.496) - this node is a cross-community bridge._
- **Why does `Synology NAS (DSM)` connect `Terraform External Services` to `Homelab Overview & NFS`, `TLS Certificate Management`?**
  _High betweenness centrality (0.494) - this node is a cross-community bridge._
- **Why does `Runbook: Configure NFS with Proxmox` connect `Homelab Overview & NFS` to `Terraform External Services`?**
  _High betweenness centrality (0.232) - this node is a cross-community bridge._
- **What connects `Age Encryption Key`, `GitHub Personal Access Token`, `Renovate Dependency Updater` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._
