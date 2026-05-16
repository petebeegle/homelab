# Architecture

<!-- GENERATED: do not edit by hand. Run `python3 tools/architecture/render.py --write`. -->

This document is generated for agentic repo navigation. It records relationships that must stay aligned with the Kubernetes, Flux, and Terraform source of truth.

## Cluster Entrypoints

### Production

- Root Kustomization: `kubernetes/clusters/production/kustomization.yaml`.
- Root resources: `flux-system`, `cluster-vars.yaml`, `infra`, `apps`.
- Infra activation list: `crds.yaml`, `cert-manager.yaml`, `grafana-operator.yaml`, `nfs-csi.yaml`, `cilium.yaml`, `certs.yaml`, `gateway.yaml`, `vpn.yaml`, `monitoring.yaml`, `loki.yaml`, `mimir.yaml`, `alloy.yaml`, `grafana.yaml`, `otel-collector.yaml`, `authentik.yaml`.
- App activation list: `external.yaml`, `pihole.yaml`, `whoami.yaml`, `renovate.yaml`, `cloudflare-tunnels.yaml`, `jellyfin.yaml`, `foundryvtt.yaml`, `valheim.yaml`, `synthetics.yaml`.

### Development

- Root Kustomization: `kubernetes/clusters/development/kustomization.yaml`.
- Root resources: `flux-system`, `cluster-vars.yaml`, `infra`, `apps`.
- Infra activation list: `crds.yaml`, `cert-manager.yaml`, `nfs-csi.yaml`, `cilium.yaml`, `certs.yaml`, `gateway.yaml`.
- App activation list: `whoami.yaml`, `foundry-bluegreen-fixture.yaml`.

- Branch environment templates: `whoami-template.yaml`, `jellyfin-template.yaml`.

### Flux Substitution Variables

| Cluster | Variable | Value |
| --- | --- | --- |
| `production` | `cilium_operator_replicas` | `3` |
| `production` | `cluster_domain` | `lab.petebeegle.com` |
| `production` | `cluster_env` | `production` |
| `production` | `gateway_external_ip` | `192.168.40.241` |
| `production` | `gateway_external_passthrough_ip` | `192.168.40.242` |
| `production` | `gateway_external_pool` | `192.168.40.240/28` |
| `production` | `gateway_internal_ip` | `192.168.30.241` |
| `production` | `gateway_internal_pool` | `192.168.30.240/28` |
| `production` | `gateway_passthrough_ip` | `192.168.30.242` |
| `production` | `letsencrypt_server` | `https://acme-v02.api.letsencrypt.org/directory` |
| `production` | `nfs_server` | `192.168.30.99` |
| `production` | `wildcard_cert_name` | `wildcard-lab-petebeegle-com` |
| `development` | `cilium_operator_replicas` | `1` |
| `development` | `cluster_domain` | `development.lab.petebeegle.com` |
| `development` | `cluster_env` | `development` |
| `development` | `gateway_external_ip` | `192.168.40.225` |
| `development` | `gateway_external_passthrough_ip` | `192.168.40.226` |
| `development` | `gateway_external_pool` | `192.168.40.224/28` |
| `development` | `gateway_internal_ip` | `192.168.30.225` |
| `development` | `gateway_internal_pool` | `192.168.30.224/28` |
| `development` | `gateway_passthrough_ip` | `192.168.30.226` |
| `development` | `letsencrypt_server` | `https://acme-staging-v02.api.letsencrypt.org/directory` |
| `development` | `nfs_server` | `192.168.30.99` |
| `development` | `wildcard_cert_name` | `wildcard-development-lab-petebeegle-com` |

## Flux Dependencies

### Infrastructure

| Cluster | Kustomization | Path | Depends on | Substitute from | SOPS |
| --- | --- | --- | --- | --- | --- |
| `production` | `alloy` | `./kubernetes/infra/monitoring/alloy` | `loki`, `mimir` | `cluster-vars` | `no` |
| `production` | `authentik` | `./kubernetes/infra/authentik` | `gateway`, `cert-manager` | `cluster-vars` | `sops` |
| `production` | `cert-manager` | `./kubernetes/infra/controllers/cert-manager` | `crds` | `cluster-vars` | `sops` |
| `production` | `certs` | `./kubernetes/infra/network/certs` | `cert-manager`, `cilium` | `cluster-vars` | `no` |
| `production` | `cilium` | `./kubernetes/infra/network/cilium` | `crds` | `cluster-vars` | `no` |
| `production` | `crds` | `./kubernetes/infra/crds` | (none) | `cluster-vars` | `no` |
| `production` | `gateway` | `./kubernetes/clusters/production/overlays/gateway` | `crds`, `cilium`, `certs` | `cluster-vars` | `no` |
| `production` | `grafana-operator` | `./kubernetes/infra/controllers/grafana-operator` | `crds` | `cluster-vars` | `no` |
| `production` | `grafana` | `./kubernetes/infra/monitoring/grafana` | `gateway`, `grafana-operator`, `loki`, `mimir` | `cluster-vars` | `sops` |
| `production` | `loki` | `./kubernetes/infra/monitoring/loki` | `crds` | `cluster-vars` | `no` |
| `production` | `mimir` | `./kubernetes/infra/monitoring/mimir` | `crds`, `nfs-csi` | `cluster-vars` | `no` |
| `production` | `monitoring` | `./kubernetes/infra/monitoring` | (none) | `cluster-vars` | `sops` |
| `production` | `nfs-csi` | `./kubernetes/infra/controllers/nfs-csi` | (none) | `cluster-vars` | `no` |
| `production` | `otel-collector` | `./kubernetes/infra/monitoring/otel-collector` | `crds`, `gateway` | `cluster-vars` | `no` |
| `production` | `vpn` | `./kubernetes/infra/network/vpn` | `cilium`, `nfs-csi`, `gateway` | `cluster-vars` | `sops` |
| `development` | `cert-manager` | `./kubernetes/infra/controllers/cert-manager` | `crds` | `cluster-vars` | `sops` |
| `development` | `certs` | `./kubernetes/infra/network/certs` | `cert-manager`, `cilium` | `cluster-vars` | `no` |
| `development` | `cilium` | `./kubernetes/infra/network/cilium` | `crds` | `cluster-vars` | `no` |
| `development` | `crds` | `./kubernetes/infra/crds` | (none) | `cluster-vars` | `no` |
| `development` | `gateway` | `./kubernetes/infra/network/gateway` | `crds`, `cilium`, `certs` | `cluster-vars` | `no` |
| `development` | `nfs-csi` | `./kubernetes/infra/controllers/nfs-csi` | (none) | `cluster-vars` | `no` |

### Applications

| Cluster | Kustomization | Path | Depends on | Substitute from | SOPS |
| --- | --- | --- | --- | --- | --- |
| `production` | `app-cloudflare-tunnels` | `./kubernetes/apps/cloudflare-tunnels` | `gateway` | `cluster-vars` | `sops` |
| `production` | `app-external` | `./kubernetes/apps/external` | `gateway` | `cluster-vars` | `no` |
| `production` | `app-foundryvtt` | `./kubernetes/apps/foundryvtt` | `gateway`, `nfs-csi` | `cluster-vars` | `sops` |
| `production` | `app-jellyfin` | `./kubernetes/apps/jellyfin` | `gateway`, `nfs-csi` | `cluster-vars` | `no` |
| `production` | `app-pihole` | `./kubernetes/apps/pihole` | `gateway` | `cluster-vars` | `sops` |
| `production` | `app-renovate` | `./kubernetes/apps/renovate` | `gateway` | `cluster-vars` | `sops` |
| `production` | `app-synthetics` | `./kubernetes/apps/synthetics` | `gateway`, `grafana`, `authentik`, `app-whoami`, `app-jellyfin`, `app-pihole`, `app-foundryvtt` | `cluster-vars` | `no` |
| `production` | `app-valheim` | `./kubernetes/apps/valheim` | `gateway`, `nfs-csi` | `cluster-vars` | `sops` |
| `production` | `app-whoami` | `./kubernetes/apps/whoami` | `gateway` | `cluster-vars` | `no` |
| `development` | `app-foundry-bluegreen-fixture` | `./kubernetes/apps/foundry-bluegreen-fixture` | `gateway`, `nfs-csi` | `cluster-vars` | `no` |
| `development` | `app-whoami` | `./kubernetes/apps/whoami` | `gateway` | `cluster-vars` | `no` |

## Kustomize Resource Relationships

| Component path | Listed resources |
| --- | --- |
| `kubernetes/infra/authentik` | `namespace.yaml`, `app.yaml`, `secret.yaml`, `httproute.yaml`, `blueprints` |
| `kubernetes/infra/controllers/cert-manager` | `app.yaml`, `secret.yaml` |
| `kubernetes/infra/controllers/grafana-operator` | `namespace.yaml`, `app.yaml` |
| `kubernetes/infra/controllers` | `./nfs-csi`, `./cert-manager`, `./grafana-operator` |
| `kubernetes/infra/controllers/nfs-csi` | `app.yaml`, `storageclass.yaml`, `volumesnapshotclass.yaml` |
| `kubernetes/infra/crds/grafana` | `app.yaml` |
| `kubernetes/infra/crds` | `https://github.com/kubernetes-csi/external-snapshotter//client/config/crd?ref=v8.5.0`, `https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/v1.5.1/config/crd/standard/gateway.networking.k8s.io_gatewayclasses.yaml`, `https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/v1.5.1/config/crd/experimental/gateway.networking.k8s.io_gateways.yaml`, `https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/v1.5.1/config/crd/standard/gateway.networking.k8s.io_httproutes.yaml`, `https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/v1.5.1/config/crd/standard/gateway.networking.k8s.io_referencegrants.yaml`, `https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/v1.5.1/config/crd/standard/gateway.networking.k8s.io_grpcroutes.yaml`, `https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/v1.5.1/config/crd/experimental/gateway.networking.k8s.io_tlsroutes.yaml`, `prometheus`, `grafana` |
| `kubernetes/infra/crds/prometheus` | `app.yaml` |
| `kubernetes/infra/monitoring/alloy` | `repositories.yaml`, `namespace.yaml`, `app.yaml` |
| `kubernetes/infra/monitoring/grafana/alerting` | `alert-rules-kubernetes.yaml`, `alert-rules-certificates.yaml`, `alert-rules-gateway-cilium.yaml`, `alert-rules-observability.yaml`, `alert-rules-apps.yaml`, `alert-rules-proxmox.yaml`, `alert-rules-flux.yaml`, `alert-rules-valheim.yaml`, `alert-rules-synthetics.yaml` |
| `kubernetes/infra/monitoring/grafana/dashboards` | `proxmox-dashboard.yaml`, `flux-dashboard.yaml`, `kubernetes-dashboard.yaml`, `authentik-dashboard.yaml`, `observability-health-dashboard.yaml`, `codex-operations-dashboard.yaml`, `synthetic-smoke-dashboard.yaml`, `monitoring-radar-dashboard.yaml` |
| `kubernetes/infra/monitoring/grafana` | `namespace.yaml`, `repositories.yaml`, `app.yaml`, `secret.yaml`, `grafana-env.yaml`, `gateway.yaml`, `grafana-instance.yaml`, `folders.yaml`, `dashboards`, `alerting` |
| `kubernetes/infra/monitoring/kube-state-metrics` | `repositories.yaml`, `app.yaml` |
| `kubernetes/infra/monitoring` | `namespace.yaml`, `kube-state-metrics`, `snmp-exporter`, `pretty-discord-alerts` |
| `kubernetes/infra/monitoring/loki` | `namespace.yaml`, `repositories.yaml`, `app.yaml` |
| `kubernetes/infra/monitoring/mimir` | `namespace.yaml`, `repositories.yaml`, `app.yaml` |
| `kubernetes/infra/monitoring/otel-collector` | `namespace.yaml`, `app.yaml`, `httproute.yaml` |
| `kubernetes/infra/monitoring/pretty-discord-alerts` | `grafana-env.yaml`, `deployment.yaml`, `service.yaml` |
| `kubernetes/infra/monitoring/snmp-exporter` | `repositories.yaml`, `deployment.yaml`, `service.yaml`, `servicemonitor.yaml` |
| `kubernetes/infra/network/certs` | `./issuer.yaml` |
| `kubernetes/infra/network/cilium` | `app.yaml`, `announcement.yaml`, `ip-pool.yaml` |
| `kubernetes/infra/network/gateway` | `./namespace.yaml`, `./certificate.yaml`, `./gateway-internal.yaml`, `./gateway-passthrough.yaml`, `./gateway-external.yaml`, `./gateway-external-passthrough.yaml`, `./https-redirect.yaml`, `./referencegrant.yaml` |
| `kubernetes/infra/network` | `./cilium`, `./certs`, `./vpn`, `./gateway` |
| `kubernetes/infra/network/vpn` | `./namespace.yaml`, `./global-config.yaml`, `./secret.yaml`, `./pvc.yaml`, `./deployment.yaml`, `./service.yaml`, `./vpn-dns.yaml`, `./httproute.yaml` |
| `kubernetes/apps/cloudflare-tunnels` | `namespace.yaml`, `secret.yaml`, `deployment.yaml`, `podmonitor.yaml` |
| `kubernetes/apps/external` | `namespace.yaml`, `synology.yaml` |
| `kubernetes/apps/foundry-bluegreen-fixture` | `namespace.yaml`, `pvc-blue.yaml`, `pvc-green.yaml`, `deployment-blue.yaml`, `deployment-green.yaml`, `service-blue.yaml`, `service-green.yaml`, `httproute-green-preview.yaml` |
| `kubernetes/apps/foundryvtt` | `namespace.yaml`, `pvc.yaml`, `secret.yaml`, `deployment.yaml`, `service.yaml`, `httproute.yaml`, `httproute-public.yaml` |
| `kubernetes/apps/jellyfin/branch` | `jellyfin.yaml` |
| `kubernetes/apps/jellyfin` | `./app.yaml`, `./pvc.yaml`, `./httproute.yaml` |
| `kubernetes/apps/pihole` | `app.yaml`, `secret.yaml`, `httproute.yaml` |
| `kubernetes/apps/renovate` | `app.yaml`, `secret.yaml` |
| `kubernetes/apps/synthetics` | `namespace.yaml`, `cronjob.yaml` |
| `kubernetes/apps/valheim` | `./app.yaml`, `./secret.yaml` |
| `kubernetes/apps/whoami/branch` | `whoami.yaml` |
| `kubernetes/apps/whoami` | `namespace.yaml`, `whoami.yaml` |

## Gateway Routes

| Kind | Route | Hostnames | Parent Gateway | Backend refs |
| --- | --- | --- | --- | --- |
| `HTTPRoute` | `authentik/authentik` | `authentik.${cluster_domain}` | `gateway/internal/https-gateway, gateway/external/https-gateway` | `authentik-server:80` |
| `HTTPRoute` | `external/synology-route` | `synology.petebeegle.com` | `gateway/internal/synology-https-gateway` | `synology-proxy:8080` |
| `HTTPRoute` | `foundry-bluegreen-fixture/foundry-fixture-green-preview` | `foundry-green-preview.development.lab.petebeegle.com` | `gateway/internal/https-gateway` | `foundry-fixture-green:80` |
| `HTTPRoute` | `foundryvtt/foundryvtt-public` | `foundry.petebeegle.com` | `gateway/public/http-gateway` | `foundryvtt:80` |
| `HTTPRoute` | `foundryvtt/foundryvtt` | `foundry.${cluster_domain}` | `gateway/internal/https-gateway` | `foundryvtt:80` |
| `HTTPRoute` | `gateway/https-redirect` | `*.${cluster_domain}, ${cluster_domain}` | `gateway/internal/http-gateway, gateway/external/http-gateway` | `(none)` |
| `HTTPRoute` | `grafana/monitoring` | `monitoring.${cluster_domain}` | `gateway/internal/https-gateway, gateway/external/https-gateway` | `grafana:80` |
| `HTTPRoute` | `jellyfin-${branch_slug}/jellyfin-${branch_slug}` | `jellyfin-${branch_slug}.${cluster_domain}` | `gateway/internal/https-gateway` | `jellyfin-${branch_slug}:8096` |
| `HTTPRoute` | `jellyfin/jellyfin` | `jellyfin.${cluster_domain}` | `gateway/internal/https-gateway, gateway/external/https-gateway` | `jellyfin:8096` |
| `HTTPRoute` | `otel-collector/otel-collector` | `otel.${cluster_domain}` | `gateway/internal/https-gateway` | `otel-collector-opentelemetry-collector:4318` |
| `HTTPRoute` | `pihole/pihole-httproute` | `pihole.${cluster_domain}` | `gateway/internal/https-gateway` | `pihole-web:80` |
| `HTTPRoute` | `whoami-${branch_slug}/whoami-${branch_slug}` | `whoami-${branch_slug}.${cluster_domain}` | `gateway/internal/https-gateway` | `whoami-${branch_slug}:80` |
| `HTTPRoute` | `whoami/whoami` | `whoami.${cluster_domain}` | `gateway/internal/https-gateway, gateway/external/https-gateway` | `whoami:80` |
| `HTTPRoute` | `wireguard/wireguard-ui` | `vpn.${cluster_domain}` | `gateway/internal/https-gateway` | `wireguard-http:51821` |
| `TLSRoute` | `external/pve01-route` | `pve01.petebeegle.com` | `gateway/passthrough` | `pve01:8006` |
| `TLSRoute` | `external/pve02-route` | `pve02.petebeegle.com` | `gateway/passthrough` | `pve02:8006` |
| `TLSRoute` | `external/pve03-route` | `pve03.petebeegle.com` | `gateway/passthrough` | `pve03:8006` |
| `TLSRoute` | `external/pve04-route` | `pve04.petebeegle.com` | `gateway/passthrough` | `pve04:8006` |
| `TLSRoute` | `external/unifi-route` | `unifi.petebeegle.com` | `gateway/passthrough` | `unifi:443` |

## Storage Relationships

| Source | Owner | StorageClass | Path |
| --- | --- | --- | --- |
| HelmRelease values | `jellyfin-${branch_slug}/jellyfin-${branch_slug}` | `nfs-csi-storage` | `kubernetes/apps/jellyfin/branch/jellyfin.yaml` |
| HelmRelease values | `valheim/valheim-server` | `nfs-csi-storage` | `kubernetes/apps/valheim/app.yaml` |
| PVC | `foundry-bluegreen-fixture/foundry-fixture-blue` | `nfs-csi-storage` | `kubernetes/apps/foundry-bluegreen-fixture/pvc-blue.yaml` |
| PVC | `foundry-bluegreen-fixture/foundry-fixture-green` | `nfs-csi-storage` | `kubernetes/apps/foundry-bluegreen-fixture/pvc-green.yaml` |
| PVC | `foundryvtt/foundryvtt-data-pvc` | `nfs-csi-storage` | `kubernetes/apps/foundryvtt/pvc.yaml` |
| PVC | `jellyfin-${branch_slug}/jellyfin-config-${branch_slug}` | `nfs-csi-storage` | `kubernetes/apps/jellyfin/branch/jellyfin.yaml` |
| PVC | `jellyfin/jellyfin-config-v2` | `nfs-csi-storage` | `kubernetes/apps/jellyfin/pvc.yaml` |
| PVC | `wireguard/wireguard-pvc` | `nfs-csi-storage` | `kubernetes/infra/network/vpn/pvc.yaml` |
| Values file | `authentik` | `nfs-csi-storage` | `kubernetes/infra/authentik/values.yaml` |
| Values file | `jellyfin` | `nfs-csi-storage` | `kubernetes/apps/jellyfin/values.yaml` |

## Secret Manifests

This lists secret manifest presence only. Secret values are not rendered.

| Component | Secret | SOPS encrypted | Path |
| --- | --- | --- | --- |
| `authentik` | `authentik/authentik-secrets` | `yes` | `kubernetes/infra/authentik/secret.yaml` |
| `cloudflare-tunnels` | `cloudflare/tunnel-credentials` | `yes` | `kubernetes/apps/cloudflare-tunnels/secret.yaml` |
| `controllers/cert-manager` | `cert-manager/cloudflare-api-token` | `yes` | `kubernetes/infra/controllers/cert-manager/secret.yaml` |
| `foundryvtt` | `foundryvtt/foundryvtt-secret` | `yes` | `kubernetes/apps/foundryvtt/secret.yaml` |
| `monitoring/grafana` | `grafana/grafana-credentials` | `yes` | `kubernetes/infra/monitoring/grafana/secret.yaml` |
| `monitoring/grafana` | `grafana/grafana-env` | `yes` | `kubernetes/infra/monitoring/grafana/grafana-env.yaml` |
| `monitoring/pretty-discord-alerts` | `monitoring/grafana-env` | `yes` | `kubernetes/infra/monitoring/pretty-discord-alerts/grafana-env.yaml` |
| `network/vpn` | `wireguard/wireguard-env` | `yes` | `kubernetes/infra/network/vpn/secret.yaml` |
| `pihole` | `pihole/pihole-admin-password` | `yes` | `kubernetes/apps/pihole/secret.yaml` |
| `renovate` | `renovate/renovate-secret` | `yes` | `kubernetes/apps/renovate/secret.yaml` |
| `valheim` | `valheim/valheim-secret` | `yes` | `kubernetes/apps/valheim/secret.yaml` |

## Terraform Substrate

| Root | Type | Name | Source | References |
| --- | --- | --- | --- | --- |
| `development` | Module | `kubernetes_nodes` | `../modules/vm` | `(none)` |
| `development` | Module | `talos_bootstrap` | `../modules/talos-bootstrap` | `kubernetes_nodes, talos_provision` |
| `development` | Module | `talos_provision` | `../modules/talos-provision` | `(none)` |
| `development` | Root resource | `proxmox_virtual_environment_file.talos_iso` | `(root)` | `talos_provision` |
| `development` | Root resource | `terraform_data.bootstrap_script` | `(root)` | `talos_bootstrap` |
| `production` | Module | `kubernetes_nodes` | `../modules/vm` | `(none)` |
| `production` | Module | `talos_bootstrap` | `../modules/talos-bootstrap` | `kubernetes_nodes, talos_provision` |
| `production` | Module | `talos_provision` | `../modules/talos-provision` | `(none)` |
| `production` | Root resource | `proxmox_virtual_environment_file.talos_iso` | `(root)` | `talos_provision` |
| `production` | Root resource | `terraform_data.bootstrap_script` | `(root)` | `talos_bootstrap` |
