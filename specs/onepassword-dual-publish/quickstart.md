# Quickstart: onepassword-dual-publish

1. Review `tools/onepassword/production_items.json`; create all 17 empty-note Secure Notes in `cluster production` with exactly the listed populated fields.
2. Use live Secret bytes, including live-only recovery for `grafana/grafana-credentials`; never paste values into chat or command arguments.
3. Run `render_production_items.py --check-only` from an authenticated user session.
4. Run the resolver without `--check-only` to write ID-only manifests.
5. Complete local validation and merge the gated PR without consumer changes.
6. Reconcile exact main, wait for 17 Ready items, and run `validate_secret_parity.py` for 17/17 PASS.

Stop on any mismatch. Do not delete a durable item resource as a retry mechanism.
