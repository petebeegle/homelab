# Evidence

## Workflow

- PASS: `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- PASS: `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- PASS: `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"`
- SKIP: `python3 tools/codex-harness/validate_sdd_context.py ...` could not run because `tools/codex-harness/validate_sdd_context.py` is not present in this branch. Substitute: `spec.md`, `plan.md`, `tasks.md`, and `evidence.md` are present and non-empty under `specs/homepage-dashboard/`.

## Local Checks

- EMERGENCY LIVE FINDING: After app-homepage reconciled development to
  `252b487`, live `ConfigMap/homepage-public-config` rendered development
  service hrefs such as `https://authentik.` because the app Kustomization
  reads live base-cluster `cluster-vars` through `postBuild.substituteFrom`.
  That live ConfigMap did not include `homepage_target_domain`, so the
  development app overlay could not rely on the branch's cluster-vars change.
- PASS emergency fix: `kubernetes/apps/homepage/development/kustomization.yaml`
  now uses literal production service hrefs in the development link-only
  `services.yaml` patch (`lab.petebeegle.com` service hosts and
  `synology.petebeegle.com`) while production base config still uses
  `${homepage_target_domain}`.
- PASS emergency fix: development route and `HOMEPAGE_ALLOWED_HOSTS` still use
  `${cluster_domain}`, and development services still omit `namespace:` and
  `app:` metadata.
- PASS emergency render: `env -i PATH="$PATH" HOME="$HOME" cluster_domain=dev.lab.petebeegle.com bash -c 'kubectl kustomize kubernetes/apps/homepage/development | flux envsubst --strict > /tmp/homepage-dashboard-dev-missing-target.yaml'`
- PASS emergency render: `env -i PATH="$PATH" HOME="$HOME" cluster_domain=lab.petebeegle.com homepage_target_domain=lab.petebeegle.com bash -c 'kubectl kustomize kubernetes/apps/homepage | flux envsubst --strict > /tmp/homepage-dashboard-prod-strict.yaml'`
- PASS emergency assertion: dependency-free rendered YAML checks confirmed
  development services contain no `${homepage_target_domain}`, no `https://.`
  hrefs, no trailing-dot or double-dot hosts, no `dev.lab.petebeegle.com` hrefs,
  exactly the expected production service hrefs, and no `namespace:`/`app:`
  entries; development route and `HOMEPAGE_ALLOWED_HOSTS` render
  `homepage.dev.lab.petebeegle.com`.
- PASS emergency assertion: rendered production services contain no dev hrefs,
  retain Kubernetes metadata, render production service hrefs from
  `${homepage_target_domain}`, and route/`HOMEPAGE_ALLOWED_HOSTS` render
  `lab.petebeegle.com` through `https-domain-gateway`.
- PASS emergency render: `kubectl kustomize kubernetes/clusters/development >/tmp/homepage-dashboard-cluster-development.yaml`
- PASS emergency render: `kubectl kustomize kubernetes/clusters/production >/tmp/homepage-dashboard-cluster-production.yaml`
- PASS emergency check: `python3 tools/architecture/render.py --check`
- PASS emergency check: `git diff --check`
- FOLLOW-UP FINDING: Playwright against live `https://homepage.dev.lab.petebeegle.com` showed the live dashboard is stale. Branch review also found the development Homepage overlay still rendered production service `namespace`/`app` metadata, so Homepage dev would call `/api/kubernetes/status/...` for prod-only services and show them missing/offline even after hrefs target production.
- PASS follow-up fix: development `ConfigMap/homepage-public-config` now patches `services.yaml` to include launchable public production links for Homepage, Authentik, Pi-hole, WireGuard, Home Assistant, Synology, Jellyfin, Foundry VTT, Grafana, and Whoami without `namespace` or `app` metadata.
- PASS follow-up fix: rendered development services omit status-only platform cards and prod-only Kubernetes status metadata, avoiding prod-only `/api/kubernetes/status/...` service-card calls from the development dashboard.
- PASS: `kubectl kustomize kubernetes/clusters/production >/tmp/homepage-dashboard-public-production.yaml`
- PASS: `kubectl kustomize kubernetes/clusters/development >/tmp/homepage-dashboard-public-development.yaml`
- PASS: `export cluster_domain=lab.petebeegle.com homepage_target_domain=lab.petebeegle.com; kubectl kustomize kubernetes/apps/homepage | flux envsubst --strict >/tmp/homepage-dashboard-public-homepage-production.yaml`
- PASS: `export cluster_domain=dev.lab.petebeegle.com homepage_target_domain=lab.petebeegle.com; kubectl kustomize kubernetes/apps/homepage/development | flux envsubst --strict >/tmp/homepage-dashboard-public-homepage-development.yaml`
- PASS: rendered development Homepage hrefs target `lab.petebeegle.com` and no rendered Homepage href targets `dev.lab.petebeegle.com`.
- PASS: rendered development Homepage `HOMEPAGE_ALLOWED_HOSTS` and `HTTPRoute` use `homepage.dev.lab.petebeegle.com` from the checked-in `cluster_domain`.
- PASS: public Homepage ConfigMap contains no private download/media automation names: `transfer`, `sabnzbd`, `radarr`, `sonarr`, `prowlarr`, or `qbittorrent`.
- PASS: `kubectl kustomize kubernetes/clusters/production/apps >/tmp/homepage-private-production-apps.yaml` in `homelab-private`.
- PASS: `export cluster_domain=lab.petebeegle.com homepage_target_domain=lab.petebeegle.com; kubectl kustomize kubernetes/apps/homepage | flux envsubst --strict >/tmp/homepage-private-homepage-production.yaml` in `homelab-private`.
- PASS: rendered private Homepage hrefs target `transfer.lab.petebeegle.com`, `sabnzbd.lab.petebeegle.com`, and `radarr.lab.petebeegle.com`.
- PASS: `git diff --check` in the public repository.
- PASS: `git diff --check` in `homelab-private`.
- FAIL then PASS: `python3 tools/architecture/render.py --check` initially reported `docs/architecture.md` stale for `homepage_target_domain`; `python3 tools/architecture/render.py --write` updated it; rerun of `--check` passed.
- PASS follow-up: `kubectl kustomize kubernetes/clusters/production >/tmp/homepage-dashboard-public-production.yaml`
- PASS follow-up: `kubectl kustomize kubernetes/clusters/development >/tmp/homepage-dashboard-public-development.yaml`
- PASS follow-up: exact assertion found rendered `value: homepage.dev.lab.petebeegle.com` and `- homepage.dev.lab.petebeegle.com`.
- PASS follow-up: rendered development Homepage hrefs target `*.lab.petebeegle.com` and no href targets `*.dev.lab.petebeegle.com`.
- PASS follow-up after `python3 tools/architecture/render.py --write`: `python3 tools/architecture/render.py --check`.
- PASS second follow-up: `kubectl kustomize kubernetes/clusters/production >/tmp/homepage-dashboard-public-production.yaml`
- PASS second follow-up: `kubectl kustomize kubernetes/clusters/development >/tmp/homepage-dashboard-public-development.yaml`
- PASS second follow-up: `export cluster_domain=lab.petebeegle.com homepage_target_domain=lab.petebeegle.com; kubectl kustomize kubernetes/apps/homepage | flux envsubst --strict >/tmp/homepage-dashboard-public-homepage-production.yaml`
- PASS second follow-up: `export cluster_domain=dev.lab.petebeegle.com homepage_target_domain=lab.petebeegle.com; kubectl kustomize kubernetes/apps/homepage/development | flux envsubst --strict >/tmp/homepage-dashboard-public-homepage-development.yaml`
- PASS second follow-up: exact assertion found rendered `value: homepage.dev.lab.petebeegle.com` and `- homepage.dev.lab.petebeegle.com`.
- PASS second follow-up: rendered development Homepage hrefs target `*.lab.petebeegle.com` and `synology.petebeegle.com`, with no href targets `*.dev.lab.petebeegle.com`.
- PASS second follow-up: rendered production Homepage includes Home Assistant at `https://homeassistant.lab.petebeegle.com` with `namespace: home-assistant` and `app: home-assistant`.
- PASS second follow-up: rendered production Homepage includes Synology at `https://synology.petebeegle.com` with `namespace: external` and `app: synology-proxy`.
- PASS second follow-up: public Homepage ConfigMap still contains no private download/media automation names: `transfer`, `sabnzbd`, `radarr`, `sonarr`, `prowlarr`, or `qbittorrent`.
- PASS second follow-up: `python3 tools/architecture/render.py --check`
- PASS second follow-up: `git diff --check`
- PASS metadata follow-up: `kubectl kustomize kubernetes/clusters/production >/tmp/homepage-dashboard-public-production.yaml`
- PASS metadata follow-up: `kubectl kustomize kubernetes/clusters/development >/tmp/homepage-dashboard-public-development.yaml`
- PASS metadata follow-up: `export cluster_domain=lab.petebeegle.com homepage_target_domain=lab.petebeegle.com; kubectl kustomize kubernetes/apps/homepage | flux envsubst --strict >/tmp/homepage-dashboard-public-homepage-production.yaml`
- PASS metadata follow-up: `export cluster_domain=dev.lab.petebeegle.com homepage_target_domain=lab.petebeegle.com; kubectl kustomize kubernetes/apps/homepage/development | flux envsubst --strict >/tmp/homepage-dashboard-public-homepage-development.yaml`
- PASS metadata follow-up: dependency-free rendered YAML assertion confirmed development services are exactly the ten non-private launchable public services, all hrefs target production `lab.petebeegle.com` or `synology.petebeegle.com`, no href targets `dev.lab.petebeegle.com`, development `HOMEPAGE_ALLOWED_HOSTS` and `HTTPRoute` use `homepage.dev.lab.petebeegle.com`, public config excludes private media/download names, development services contain no `namespace:` or `app:`, and production services retain Kubernetes metadata.
- PASS metadata follow-up: `python3 tools/architecture/render.py --check`
- PASS metadata follow-up: `git diff --check`

## Development Validation

- EXCEPTION: live development validation was not run because `kubectl config current-context` failed with `error: current-context is not set`.
- Substitute checks: public production/development cluster renders, strict Homepage envsubst renders, route/allowed-host assertions, production-target href assertions, private production app render, private Homepage strict envsubst render, architecture check, and whitespace checks.

## Commits

- Private `homelab-private` commit: `cf24f4442d04177de457c6f0ef7ba0bbc8ecd3f2` (`feat(homepage): target production private links`).
- Public follow-up commit is created after this evidence update so the commit includes the final SDD artifacts.
