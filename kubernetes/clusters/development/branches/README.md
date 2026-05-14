# Development Branch Environments

This directory is a template library, not part of the live development cluster entrypoint.

To test an app branch, copy the relevant template into `kubernetes/clusters/development/apps/branches/` or another reviewed cluster-layer path, replace `branch_name` and `branch_slug`, set `spec.suspend: false`, and commit the activation. Branch app hostnames should follow `<app>-${branch_slug}.development.lab.petebeegle.com`.

Keep cluster-scoped changes out of branch environments. Test those sequentially against the development base so CRDs, controllers, Gateway API objects, and shared storage changes are applied in one ordered reconciliation path.
