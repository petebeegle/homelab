# Graph Report - ./{terraform,kubernetes}  (2026-05-02)

## Corpus Check
- Corpus is ~332 words - fits in a single context window. You may not need a graph.

## Summary
- 237 nodes · 356 edges · 16 communities detected
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 37 edges (avg confidence: 0.83)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Flux App Kustomizations|Flux App Kustomizations]]
- [[_COMMUNITY_Grafana Alerting Rules|Grafana Alerting Rules]]
- [[_COMMUNITY_Application HelmReleases|Application HelmReleases]]
- [[_COMMUNITY_cert-manager Controller|cert-manager Controller]]
- [[_COMMUNITY_Cilium CNI & L2 LB|Cilium CNI & L2 LB]]
- [[_COMMUNITY_CRD Bootstrap Layer|CRD Bootstrap Layer]]
- [[_COMMUNITY_Cloudflare Tunnel|Cloudflare Tunnel]]
- [[_COMMUNITY_Authentik SSO|Authentik SSO]]
- [[_COMMUNITY_OpenTelemetry Collector|OpenTelemetry Collector]]
- [[_COMMUNITY_Jellyfin Media Server|Jellyfin Media Server]]
- [[_COMMUNITY_External TLS Passthrough|External TLS Passthrough]]
- [[_COMMUNITY_Alloy Metrics Collector|Alloy Metrics Collector]]
- [[_COMMUNITY_Mimir Metrics Storage|Mimir Metrics Storage]]
- [[_COMMUNITY_Discord Alert Notifier|Discord Alert Notifier]]
- [[_COMMUNITY_Terraform Cluster Bootstrap|Terraform Cluster Bootstrap]]
- [[_COMMUNITY_NFS CSI Storage|NFS CSI Storage]]

## God Nodes (most connected - your core abstractions)
1. `Gateway: internal (namespace: gateway, section: https-gateway)` - 20 edges
2. `ConfigMap: cluster-vars (postBuild substituteFrom source)` - 16 edges
3. `infra kustomization.yaml (lists all infra resources)` - 14 edges
4. `gateway (Flux Kustomization)` - 12 edges
5. `Gateway: passthrough (namespace: gateway)` - 11 edges
6. `GitRepository: flux-system (ssh://git@github.com/petebeegle/homelab)` - 9 edges
7. `crds (Flux Kustomization)` - 9 edges
8. `Grafana Datasource: prometheus (Mimir)` - 8 edges
9. `Namespace: external` - 7 edges
10. `cluster-vars ConfigMap (production)` - 7 edges

## Surprising Connections (you probably didn't know these)
- `cert-manager Helm values (Gateway API enabled)` --enables_gateway_api--> `Gateway: internal (namespace: gateway, section: https-gateway)`  [INFERRED]
  kubernetes/infra/controllers/cert-manager/values.yaml → kubernetes/apps/foundryvtt/httproute.yaml
- `Service+TLSRoute: synology (${nfs_server}:5001)` --references--> `StorageClass: nfs-csi-storage`  [INFERRED]
  kubernetes/apps/external/synology.yaml → kubernetes/apps/foundryvtt/pvc.yaml
- `Gateway: passthrough (namespace: gateway)` --requests_ip_from_pool--> `CiliumLoadBalancerIPPool 192.168.30.240/28`  [INFERRED]
  kubernetes/apps/external/pve01.yaml → kubernetes/infra/network/cilium/ip-pool.yaml
- `Gateway: passthrough (namespace: gateway)` --sibling_gateway_in_namespace--> `Gateway: internal (namespace: gateway, section: https-gateway)`  [INFERRED]
  kubernetes/apps/external/pve01.yaml → kubernetes/apps/foundryvtt/httproute.yaml
- `authentik HTTPRoute` --parentRef--> `Gateway: internal (namespace: gateway, section: https-gateway)`  [EXTRACTED]
  kubernetes/infra/authentik/httproute.yaml → kubernetes/apps/foundryvtt/httproute.yaml

## Hyperedges (group relationships)
- **TLS Passthrough pattern: Proxmox nodes (pve01-pve04) exposed via Gateway passthrough in external namespace** — pve01_service, pve02_service, pve03_service, pve04_service, gateway_passthrough [EXTRACTED 1.00]
- **FoundryVTT dual ingress: internal HTTPRoute + external Cloudflare tunnel** — foundryvtt_service, foundryvtt_httproute, cloudflared_configmap [EXTRACTED 1.00]
- **FoundryVTT persistent storage stack: PVC backed by nfs-csi-storage mounted in deployment** — foundryvtt_deployment, foundryvtt_pvc, nfs_csi_storage [EXTRACTED 1.00]
- **All production app Flux Kustomizations share gateway dependency + cluster-vars substitution pattern** — flux_kustomization_app_pihole, flux_kustomization_app_foundryvtt, flux_kustomization_app_renovate, flux_kustomization_app_external, gateway_internal, production_cluster_vars [EXTRACTED 1.00]
- **jellyfin and valheim both use nfs-csi-storage StorageClass with NFS server variable** — jellyfin_helmrelease, valheim_helmrelease, nfs_csi_storage, production_nfs_server [EXTRACTED 1.00]
- **pihole and whoami HTTPRoutes both attach to internal Gateway using cluster_domain variable substitution** — pihole_httproute, whoami_httproute, gateway_internal, production_cluster_domain [EXTRACTED 1.00]
- **Observability stack: alloy forwards metrics/logs to loki+mimir, grafana visualizes** — infra_alloy, infra_loki, infra_mimir, infra_grafana [EXTRACTED 1.00]
- **NFS-dependent apps: jellyfin and valheim both depend on nfs-csi for storage** — infra_nfs_csi, app_jellyfin, app_valheim [EXTRACTED 1.00]
- **Gateway dependency chain: crds -> cilium + certs -> gateway; all apps depend on gateway** — infra_crds, infra_cilium, infra_certs, infra_gateway [EXTRACTED 1.00]
- **Authentik SSO OAuth2 integration for Grafana and Synology via blueprints** — authentik_app, grafana_oauth_blueprint, synology_oauth_blueprint [EXTRACTED 1.00]
- **Core controllers managed together as Flux infra bundle: nfs-csi, cert-manager, grafana-operator** — controllers_kustomization, nfs_csi_kustomization, certmanager_kustomization, grafana_operator_kustomization_infra [EXTRACTED 1.00]
- **certs Flux Kustomization depends on both cert-manager and cilium before applying** — certs_kustomization, certmanager_app, cluster_vars_configmap [EXTRACTED 1.00]
- **CRDs Bundle: external-snapshotter + gateway-api + grafana-operator-crds + prometheus-crds** — crds_kustomization, crds_grafana_app, crds_prometheus_app, crds_external_snapshotter, crds_gateway_api [EXTRACTED 1.00]
- **Alloy config pipeline: kustomization generates ConfigMap mounted by HelmRelease** — alloy_kustomization, alloy_configmap, alloy_app [EXTRACTED 1.00]
- **Grafana operator pattern: Grafana CR + GrafanaFolders managed via instanceSelector label** — grafana_instance, grafana_folders, crds_grafana_app [EXTRACTED 0.95]
- **Flux Observability Pipeline: ksm CRD metrics -> Mimir -> Grafana alert rules** — ksm_app_helmrelease, ksm_gotk_resource_info_metric, alerting_flux_alert_rule_group, app_grafana_datasource_prometheus, app_grafana_contactpoint_discord [INFERRED 0.85]
- **Grafana Operator dashboard provisioning pattern: GrafanaDashboard CRDs loaded from ConfigMap JSON** — dashboards_kustomization_dashboards, dashboards_flux_dashboard, dashboards_kubernetes_dashboard, dashboards_proxmox_dashboard, dashboards_authentik_dashboard [EXTRACTED 1.00]
- **Loki SimpleScalable deployment: backend+read+write replicas + minio storage** — loki_app_helmrelease, loki_simple_scalable_mode, loki_minio_storage, loki_namespace [EXTRACTED 0.95]
- **SNMP Monitoring Pipeline for Synology NAS** — snmp_exporter_deployment, snmp_exporter_service, snmp_exporter_servicemonitor, synology_nas_target [EXTRACTED 0.95]
- **Cloudflare DNS-01 Certificate Issuers (prod + staging)** — certs_issuer_cloudflare, certs_issuer_cloudflare_staging, cloudflare_api_token_secret [EXTRACTED 1.00]
- **Mimir Distributed with Minio Storage** — mimir_app_helmrelease, mimir_chart_mimir_distributed, mimir_namespace [EXTRACTED 0.95]
- **Cilium L2 LoadBalancer IP advertisement stack** — cilium_l2_announcement_feature, cilium_announcement, cilium_ip_pool [EXTRACTED 1.00]
- **Gateway API TLS termination: internal gateway + wildcard cert + cloudflare issuer** — gateway_internal, gateway_certificate, cloudflare_clusterissuer [EXTRACTED 1.00]
- **WireGuard VPN deployment: wg-easy pod + NFS PVC + LB service** — vpn_deployment, vpn_pvc, vpn_service_lb [EXTRACTED 0.95]

## Communities

### Community 0 - "Flux App Kustomizations"
Cohesion: 0.08
Nodes (37): ClusterIssuer cloudflare (cert-manager), app-external Flux Kustomization, app-foundryvtt Flux Kustomization, app-pihole Flux Kustomization, app-renovate Flux Kustomization, flux-system GitRepository, Certificate wildcard TLS, HTTPRoute https-redirect (+29 more)

### Community 1 - "Grafana Alerting Rules"
Cohesion: 0.08
Nodes (34): GrafanaAlertRuleGroup: flux, Alert Rule: Flux Resources Failing, Alert Rule: Flux Reconciliation Rate Low, Alert Rule: Flux Resources Stale, Alert Rule: Flux Resources Suspended, Kustomization: grafana/alerting, GrafanaAlertRuleGroup: mimir, Alert Rule: Mimir Ingester Unhealthy (+26 more)

### Community 2 - "Application HelmReleases"
Cohesion: 0.22
Nodes (26): app-cloudflare-tunnels (Flux Kustomization), app-jellyfin (Flux Kustomization), app-valheim (Flux Kustomization), app-whoami (Flux Kustomization), ConfigMap: cluster-vars (postBuild substituteFrom source), flux-system Kustomization (kustomize overlay), flux-system root Kustomization (path: ./kubernetes/clusters/production), GitRepository: flux-system (ssh://git@github.com/petebeegle/homelab) (+18 more)

### Community 3 - "cert-manager Controller"
Cohesion: 0.14
Nodes (18): cert-manager HelmRelease + HelmRepository (jetstack), cert-manager kustomization (base), cert-manager kustomizeconfig (nameReference for ConfigMap), cert-manager Helm values (Gateway API enabled), ClusterIssuer: cloudflare, ClusterIssuer: cloudflare-staging, certs (Flux Kustomization), Secret: cloudflare-api-token (+10 more)

### Community 4 - "Cilium CNI & L2 LB"
Cohesion: 0.16
Nodes (18): CiliumL2AnnouncementPolicy, cilium HelmRelease, Cilium Gateway API integration, cilium HelmRepository, Cilium Hubble observability, CiliumLoadBalancerIPPool 192.168.30.240/28, cilium Kustomization, cilium kustomizeconfig (+10 more)

### Community 5 - "CRD Bootstrap Layer"
Cohesion: 0.16
Nodes (15): CRD: external-snapshotter v8.5.0, CRD: Gateway API v1.5.1, HelmRelease: grafana-operator-crds, HelmRepository: grafana (kube-system), Kustomization: infra/crds/grafana, Kustomization: infra/crds, HelmRelease: prometheus-crds, HelmRepository: prometheus-community (kube-system) (+7 more)

### Community 6 - "Cloudflare Tunnel"
Cohesion: 0.23
Nodes (14): Namespace: cloudflare, Kustomization: cloudflare-tunnels, ConfigMap: cloudflared (tunnel config), Deployment: cloudflared, PodMonitor: cloudflared, Cloudflare Tunnel: foundry-k8s-tunnel, Deployment: foundryvtt (felddy/foundryvtt:14.360), HTTPRoute: foundryvtt (foundry.${cluster_domain}) (+6 more)

### Community 7 - "Authentik SSO"
Cohesion: 0.18
Nodes (14): authentik HelmRelease + HelmRepository, authentik blueprints kustomization, authentik HTTPRoute, authentik kustomization (base), authentik kustomizeconfig (nameReference for ConfigMap), authentik Namespace, Secret: authentik-secrets, authentik Helm values (+6 more)

### Community 8 - "OpenTelemetry Collector"
Cohesion: 0.19
Nodes (13): HelmRelease: otel-collector, Helm Chart: opentelemetry-collector v0.144.0, HelmRepository: opentelemetry, Kustomization: otel-collector, Namespace: otel-collector, ConfigMap: snmp-exporter-config, Deployment: snmp-exporter, HelmRepository: prometheus-community (+5 more)

### Community 9 - "Jellyfin Media Server"
Cohesion: 0.17
Nodes (12): jellyfin HelmRelease, jellyfin HelmRepository, jellyfin Kustomization, jellyfin Namespace, jellyfin values.yaml, StorageClass: nfs-csi-storage, nfs_server: 192.168.30.99, valheim-server HelmRelease (+4 more)

### Community 10 - "External TLS Passthrough"
Cohesion: 0.33
Nodes (10): Kustomization: external, Namespace: external, Gateway: passthrough (namespace: gateway), ReferenceGrant external-to-passthrough-gateway, Service+TLSRoute: pve01 (Proxmox 192.168.3.11:8006), Service+TLSRoute: pve02 (Proxmox 192.168.3.12:8006), Service+TLSRoute: pve03 (Proxmox 192.168.3.13:8006), Service+TLSRoute: pve04 (Proxmox 192.168.3.14:8006) (+2 more)

### Community 11 - "Alloy Metrics Collector"
Cohesion: 0.36
Nodes (8): HelmRelease: alloy, ConfigMap: alloy-config, Kustomization: infra/monitoring/alloy, KustomizeConfig: alloy nameReference ConfigMap, Namespace: alloy, HelmRepository: grafana (flux-system), Kustomization: infra/monitoring, Namespace: monitoring

### Community 12 - "Mimir Metrics Storage"
Cohesion: 0.47
Nodes (6): HelmRelease: mimir, Helm Chart: mimir-distributed v5.8.0, Kustomization: mimir, Namespace: mimir, HelmRepository: grafana (loki), HelmRepository: grafana (mimir)

### Community 13 - "Discord Alert Notifier"
Cohesion: 0.5
Nodes (5): Deployment: pretty-discord-alerts, Container Image: ghcr.io/petebeegle/pretty-discord-alerts:1.2.0, Kustomization: pretty-discord-alerts, Service: pretty-discord-alerts, Secret: grafana-env

### Community 14 - "Terraform Cluster Bootstrap"
Cohesion: 0.5
Nodes (4): Terraform module talos_bootstrap, Terraform module talos_provision, Terraform module kubernetes_nodes (vm), terraform cluster README

### Community 15 - "NFS CSI Storage"
Cohesion: 1.0
Nodes (3): HelmRelease: csi-driver-nfs, HelmRepository: csi-driver-nfs (kube-system), StorageClass: nfs-csi-storage

## Knowledge Gaps
- **61 isolated node(s):** `Cloudflare Tunnel: foundry-k8s-tunnel`, `KustomizeConfig: jellyfin (nameReference ConfigMap->HelmRelease)`, `jellyfin Kustomization`, `jellyfin HelmRepository`, `jellyfin Namespace` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Gateway: internal (namespace: gateway, section: https-gateway)` connect `Flux App Kustomizations` to `cert-manager Controller`, `Cilium CNI & L2 LB`, `CRD Bootstrap Layer`, `Cloudflare Tunnel`, `Authentik SSO`, `External TLS Passthrough`?**
  _High betweenness centrality (0.363) - this node is a cross-community bridge._
- **Why does `HTTPRoute: monitoring (grafana ns)` connect `CRD Bootstrap Layer` to `Flux App Kustomizations`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Why does `Kustomization: infra/monitoring/grafana` connect `CRD Bootstrap Layer` to `Alloy Metrics Collector`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Gateway: internal (namespace: gateway, section: https-gateway)` (e.g. with `cert-manager Helm values (Gateway API enabled)` and `CiliumLoadBalancerIPPool 192.168.30.240/28`) actually correct?**
  _`Gateway: internal (namespace: gateway, section: https-gateway)` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `gateway (Flux Kustomization)` (e.g. with `app-cloudflare-tunnels (Flux Kustomization)` and `app-valheim (Flux Kustomization)`) actually correct?**
  _`gateway (Flux Kustomization)` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Gateway: passthrough (namespace: gateway)` (e.g. with `CiliumLoadBalancerIPPool 192.168.30.240/28` and `Gateway: internal (namespace: gateway, section: https-gateway)`) actually correct?**
  _`Gateway: passthrough (namespace: gateway)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Cloudflare Tunnel: foundry-k8s-tunnel`, `KustomizeConfig: jellyfin (nameReference ConfigMap->HelmRelease)`, `jellyfin Kustomization` to the rest of the system?**
  _61 weakly-connected nodes found - possible documentation gaps or missing edges._
