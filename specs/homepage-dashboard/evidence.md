# Evidence

## Workflow

- PASS: `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- PASS: `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- PASS: `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"`
- SKIP: `python3 tools/codex-harness/validate_sdd_context.py ...` could not run because `tools/codex-harness/validate_sdd_context.py` is not present in this branch. Substitute: `spec.md`, `plan.md`, `tasks.md`, and `evidence.md` are present and non-empty under `specs/homepage-dashboard/`.

## Local Checks

- PASS: `kubectl kustomize kubernetes/clusters/production >/tmp/homepage-dashboard-public-production.yaml`
- PASS: `kubectl kustomize kubernetes/clusters/development >/tmp/homepage-dashboard-public-development.yaml`
- PASS: `export cluster_domain=lab.petebeegle.com homepage_target_domain=lab.petebeegle.com; kubectl kustomize kubernetes/apps/homepage | flux envsubst --strict >/tmp/homepage-dashboard-public-homepage-production.yaml`
- PASS: `export cluster_domain=development.lab.petebeegle.com homepage_target_domain=lab.petebeegle.com; kubectl kustomize kubernetes/apps/homepage/development | flux envsubst --strict >/tmp/homepage-dashboard-public-homepage-development.yaml`
- PASS: rendered development Homepage hrefs target `lab.petebeegle.com` and no rendered Homepage href targets `development.lab` or `dev.lab`.
- PASS: rendered development Homepage `HOMEPAGE_ALLOWED_HOSTS` and `HTTPRoute` use `homepage.development.lab.petebeegle.com` from the checked-in `cluster_domain`.
- FAIL: exact assertion for `homepage.dev.lab.petebeegle.com` did not match the local render because the current development `cluster_domain` is `development.lab.petebeegle.com`. This implementation did not change `cluster_domain`.
- PASS: public Homepage ConfigMap contains no private download/media automation names: `transfer`, `sabnzbd`, `radarr`, `sonarr`, `prowlarr`, or `qbittorrent`.
- PASS: `kubectl kustomize kubernetes/clusters/production/apps >/tmp/homepage-private-production-apps.yaml` in `homelab-private`.
- PASS: `export cluster_domain=lab.petebeegle.com homepage_target_domain=lab.petebeegle.com; kubectl kustomize kubernetes/apps/homepage | flux envsubst --strict >/tmp/homepage-private-homepage-production.yaml` in `homelab-private`.
- PASS: rendered private Homepage hrefs target `transfer.lab.petebeegle.com`, `sabnzbd.lab.petebeegle.com`, and `radarr.lab.petebeegle.com`.
- PASS: `git diff --check` in the public repository.
- PASS: `git diff --check` in `homelab-private`.
- FAIL then PASS: `python3 tools/architecture/render.py --check` initially reported `docs/architecture.md` stale for `homepage_target_domain`; `python3 tools/architecture/render.py --write` updated it; rerun of `--check` passed.

## Development Validation

- EXCEPTION: live development validation was not run because `kubectl config current-context` failed with `error: current-context is not set`.
- Substitute checks: public production/development cluster renders, strict Homepage envsubst renders, route/allowed-host assertions, production-target href assertions, private production app render, private Homepage strict envsubst render, architecture check, and whitespace checks.

## Commits

- Private `homelab-private` commit: `cf24f4442d04177de457c6f0ef7ba0bbc8ecd3f2` (`feat(homepage): target production private links`).
- Public commit is created after this evidence update so the commit includes the final SDD artifacts.
