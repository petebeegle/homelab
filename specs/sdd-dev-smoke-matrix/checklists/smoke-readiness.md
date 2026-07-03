# Smoke Readiness Checklist

- [x] Owner workflow marker, plan, attestation, and delegation token exist.
- [x] Owner workflow validators passed before tracked edits.
- [x] SDD spec, plan, tasks, and evidence files exist.
- [x] Existing `whoami`, `jellyfin`, and `home-assistant` behavior remains
      covered by tests or profile parsing.
- [x] Flux Kustomization readiness is profile-driven.
- [x] TLSRoute readiness is profile-driven.
- [x] Secret reference checks are name-only and do not inspect secret contents.
- [x] Route URL or Playwright handoff is documented.
- [x] `pihole` and `foundryvtt` coverage is added or explicitly deferred with
      reasons.
- [x] `authentik` and `monitoring` gaps are documented.
- [x] Synthetic smoke mirroring is enforced or explicitly deferred with a
      follow-up.
- [x] Required local checks and development validation exception/evidence are
      recorded.
