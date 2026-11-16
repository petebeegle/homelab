# Development Branch Environments

This directory is a template library, not part of the live development cluster entrypoint.

The manifests here are cluster-layer activation templates: they create a branch-specific Flux `GitRepository` and `Kustomization` that point the development cluster at a Git branch. The app payload they activate lives under app directories such as `kubernetes/apps/whoami/branch/`, where resource names, namespaces, and hostnames are parameterized with `${branch_slug}`.

For apps that the PR smoke test covers (`prSmoke: true` in their smoke profile: `whoami` and `homepage`), that `branch/` directory is a kustomize overlay on the real manifests, not a copy: `branch/app/kustomization.yaml` renames and re-hosts what the app already deploys (`../../base` for whoami, `../../development` for homepage). Change the real manifests and the branch environment picks the change up. `tools/development/tests/test_branch_overlay_render.py` enforces this (no workload manifests under `branch/`, container specs equal the real ones). The remaining apps (`home-assistant`, `immich`, `jellyfin`) still keep hand-written copies; convert each before turning `prSmoke` on for it.

To test an app branch, copy the relevant template into `kubernetes/clusters/development/apps/branches/` or another reviewed cluster-layer path, replace `branch_name` and `branch_slug`, set `spec.suspend: false`, and commit the activation. Branch app hostnames should follow `<app>-${branch_slug}.dev.lab.petebeegle.com`.

## Local Verification

Local verification without pushing is supported for manifest shape checks:

```sh
export branch_slug=example
export cluster_domain=dev.lab.petebeegle.com
kubectl kustomize kubernetes/apps/whoami/branch | flux envsubst --strict
kubectl kustomize kubernetes/clusters/development

cp kubernetes/clusters/development/branches/whoami-template.yaml /tmp/whoami-branch.yaml
perl -0pi -e 's/\$\{branch_name\}/my-branch/g; s/\$\{branch_slug\}/example/g' /tmp/whoami-branch.yaml
flux build kustomization branch-whoami-example \
  --path=./kubernetes/apps/whoami/branch \
  --kustomization-file=/tmp/whoami-branch.yaml \
  --dry-run
```

Live branch environments use Flux `GitRepository` sources, so controller reconciliation requires the referenced branch to exist on origin unless you are intentionally using a temporary local apply or dry-run workflow.

Keep cluster-scoped changes out of branch environments. Test those sequentially against the development base so CRDs, controllers, Gateway API objects, and shared storage changes are applied in one ordered reconciliation path.
