# Homepage Dashboard Production Links Expansion

## Summary

Expand the public Homepage dashboard so production shows all public,
non-private launchable services and important platform status cards, while the
development Homepage instance links to production service URLs.

## Requirements

- Production and development cluster substitutions define
  `homepage_target_domain: lab.petebeegle.com`.
- Public Homepage service and bookmark `href` targets use
  `${homepage_target_domain}` when pointing at lab services.
- Homepage's own HTTPRoute hostnames and `HOMEPAGE_ALLOWED_HOSTS` continue to
  use `${cluster_domain}` so development remains hosted at its development
  hostname.
- Public Homepage includes non-private launchable production URLs from the
  public repository.
- Public Homepage includes status-only Kubernetes cards for important platform
  workloads that do not have user-facing web launch URLs.
- Public Homepage does not include private media/download service names or
  private configuration owned by `homelab-private`.
- Private Homepage config remains in `homelab-private` and uses
  `${homepage_target_domain}` for its private service hrefs.
- Dormant external manifests are not activated.

## References

- `AGENTS.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/runbooks/development-cluster.md`
- `docs/decisions/cilium-gateway-api-ingress.md`

## Acceptance Criteria

- Local render of public production and development cluster kustomizations
  succeeds.
- Rendered development Homepage HTTPRoute remains development-scoped.
- Rendered development Homepage service/bookmark hrefs target
  `lab.petebeegle.com` rather than the development domain.
- Local render of private production apps succeeds.
- Architecture generation check passes or generated docs are updated.
- Development validation is attempted if available, otherwise an unavailable
  infrastructure exception and substitute checks are recorded.
