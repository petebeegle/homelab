# Decisions

The choices that shape this repo and are not obvious from reading it. Each
entry says what was chosen, why, and what it rules out. If a decision changes,
edit its entry; git history keeps the old wording.

Earlier versions of this page were sixteen separate records numbered ADR-0001
to ADR-0016. They are in git history up to commit `850c034`.

## Changes go through pull requests, and the check is the evidence

- Nothing is committed to `main`. One change, one branch, one pull request. Git
  is the source of truth; Flux applies what is on `main`.
- Manual cluster edits are temporary break-glass actions and get backfilled into
  Git if they should stay.
- Required checks gate the merge (`Pre-commit`, `Verification / harness`).
  `dev-smoke` deploys a PR's change to the development cluster and tests it. It
  is informational today and becomes required once it has run stably (issue
  #477).
- Anything `dev-smoke` does not cover (Terraform, Flux wiring, infrastructure,
  Gateway routes, storage, secret references, apps without a smoke profile) is
  validated in the development cluster by hand, and the PR description says what
  was run and what it showed.
- Automatic merging is limited to Renovate, non-major updates, and files that
  development deploys, so `dev-smoke` tests them: the smoke-tested apps and the
  infrastructure development runs. Production-only infrastructure, Terraform,
  workflows and Flux itself never auto-merge. It starts before `dev-smoke` is
  required because Renovate merges itself only once every check on the PR is
  green, `dev-smoke` included (`platformAutomerge: false`; GitHub auto-merge
  would wait for the required checks only). A Renovate PR inside those paths
  that `dev-smoke` could not test (two apps at once, say) fails rather than
  passing as "not smoke-tested". The details are in
  [the Renovate runbook](runbooks/renovate.md#auto-merge).
- Tests come first where the change has testable behaviour. Review enforces it.
- Two local guards stay on for agents: no unencrypted secret manifests, and no
  `terraform apply` without a plan.
- The development cluster's only alert is `dev-heartbeat`, and it does not rely
  on GitHub's cron. GitHub fires scheduled workflows on this repo only every few
  hours (a 10h40m gap between `*/30` runs was seen in November 2026), so the
  heartbeat counts a success of any job on the `homelab-dev` runner (`dev-cleanup`
  or `dev-smoke`'s `smoke` job) and allows 12 hours, longer than any gap seen.
  For the same reason every smoke run also sweeps stale `pr-*` environments
  rather than leaving that to `dev-cleanup` alone.
- The CI runner (`homelab-dev`) runs in **production**, not in the development
  cluster it tests. A test harness inside the system under test dies with it:
  a PR that breaks development's networking would kill the runner before it
  could restore development or report the failure (#522). In production it
  holds no production credentials (no ServiceAccount token, no RBAC), reaches
  development only as the narrow `dev-runner` account through a kubeconfig in
  the "cluster production" vault, and a default-deny `CiliumNetworkPolicy`
  lets it reach only DNS, GitHub, npm, and development's API server and
  internal gateway. Requests to production's gateways get Cilium's `403 Access
  denied`. The cost is that CI depends on production being up.

**Why.** A per-change paper trail (spec, plan, tasks, evidence files) grew to
about 9,000 lines of tooling and 325 committed files, and the evidence was
hand-written. A check that deploys the change and tests it is stronger evidence
than a file saying someone did.

**Rules out.** Per-PR process artifacts, hooks that require them, and hard
smoke gates for apps that have no smoke profile.

Procedure: [runbooks/change-workflow.md](./runbooks/change-workflow.md).

## Ingress is Gateway API, never `Ingress`

- Routes are `HTTPRoute` or `TLSRoute`. There are five gateways in namespace
  `gateway`: `internal` (LAN), `external` (WireGuard service plane, not the
  internet), `public` (reached through Cloudflare Tunnel, needs a cloudflared
  ingress rule too), and `passthrough` and `external-passthrough` for TLS that
  ends at the target (LAN and WireGuard respectively).
- Use `HTTPRoute` when the cluster should present the trusted certificate or hide
  a backend port. Use `TLSRoute` passthrough only when the target terminates TLS
  itself with a certificate that is valid for the hostname.
- Hostnames use `${cluster_domain}` in shared manifests.

**Why.** Cilium already provides Gateway API, L2 address announcement and
kube-proxy replacement in one layer, and Gateway API separates shared listeners
from app-owned routes. `kubeProxyReplacement: true` and L2 announcements are
ingress-critical settings.

**Synology DSM is the exception that explains the rule.** DSM's own certificate
is not trusted for `synology.petebeegle.com`, Cilium does not originate HTTPS
upstream because a Service says `appProtocol: https`, and DSM's HTTP port
redirects browsers to `:5001`. So the gateway terminates HTTPS with a
cert-manager certificate and sends HTTP to an in-cluster nginx proxy
(`synology-proxy`), which talks HTTPS to the NAS on 5001 and rewrites redirects
that would expose the backend port. DNS for that name points at the internal
gateway, not the NAS.

## Storage is NFS on the Synology, except Jellyfin's config

- `nfs-csi-storage` (default, `/volume2/Homelab`) is for app data.
  `nfs-csi-media-storage` (`/volume1/Media`) is opt-in for media and downloads.
  Both use `reclaimPolicy: Retain`: deleting a claim leaves the data on the NAS.
  The exception is development's branch environments: their cleanup switches the
  Released volumes of a removed `<app>-<slug>` namespace to `Delete`, so smoke runs
  do not leave a copy of the app's data on the NAS each time.
- Use Btrfs volumes on the NAS (the CSI driver's quota support needs them), and
  NFS v4.1 for volumes shared by several pods.
- NFS-backed apps depend on the `nfs-csi` Kustomization. Nothing PVC-backed
  schedules while the CSI driver is unhealthy.

**Exception: Jellyfin's `/config` is on `local-path`.** Jellyfin does
latency-sensitive SQLite and plugin I/O under `/config`, which competed with
media reads and Sonarr/Radarr imports on the NAS. Media stays on NFS. The cost:
the config volume is tied to one iGPU worker node, Jellyfin cannot move if that
node is lost, and nothing in this repo backs the volume up. The old NFS copy
used for the migration was removed in November 2026.

## Secrets: SOPS today, moving to 1Password

- Committed Kubernetes secrets are SOPS-encrypted with Age. Flux decrypts them
  with the `sops-age` Secret. Files must be named `secret.yaml` or
  `grafana-env.yaml` so `.sops.yaml` matches them.
- Production also runs the 1Password operator with 17 mirrored items.
  Development reads only from its own 1Password vault and holds no SOPS key:
  every SOPS file is encrypted to the same Age key, so a cluster holding it can
  read every production secret. Development's bootstrap uses the `onepassword`
  mode, and `tools/tests/test_development_has_no_sops_key.py` fails if anything
  development applies needs decryption. Finishing the move and removing SOPS is tracked in
  issue #490. Until then a secret change has to be made in both places.
- Terraform's own sensitive inputs live in ignored local `*.tfvars` files, not in
  Git and not in SOPS. They are operator inputs, not cluster state.

## Talos and Proxmox are managed through their own tools

- Talos nodes have no SSH. Everything goes through `talosctl`, aimed at direct
  control-plane IPs, never the Kubernetes API VIP (workers cannot forward Talos
  API calls). Diagnose in order: etcd, kubelet, controller runtime, workloads.
- The Proxmox hosts are Proxmox VE 9 on Debian Trixie. They use the
  no-subscription repository because they have no enterprise subscription. That
  is a homelab choice, not a general production recommendation.

## Observability is in Git

- Grafana, Mimir, Loki, Alloy, dashboards, alert rules and Discord alert routing
  are changed in this repo and reconciled by Flux. Live edits are for
  investigation only.
- Dashboards and alert rules refer to the datasource UIDs `prometheus` (Mimir)
  and `loki`, never display names.
- Metrics scraping is opt-in: a Service or pod needs `prometheus.io/scrape:
  "true"` (plus `prometheus.io/port` and `prometheus.io/path` when they differ
  from the defaults). Pod logs are collected regardless.
- Alert delivery goes Grafana, then `pretty-discord-alerts`, then Discord. When
  alert state and Discord disagree, check both ends.
