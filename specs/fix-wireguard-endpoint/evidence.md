# Evidence: fix-wireguard-endpoint

## Authorization and workflow
User explicitly requested the config correction after the endpoint diagnosis.
Combined bounded-change authorization is recorded rather than asking again.
Lightweight process exception: separate clarify/checklist/analyze review gates
are consolidated into the scoped requirements, plan, and tests. No architecture
change is proposed. Converge will compare these requirements with final results.

## Initial observations
Both ipify and Cloudflare report 69.180.24.212 from the running WireGuard pod.
SOPS WG_HOST, running WG_HOST, and user_configs_table.host remain 67.191.221.64.
The stored and service ports are 30000. Only non-secret DB columns were queried.
No production mutations have been performed.

## Workspace
Default /workspaces/homelab-worktrees parent denied writes. Allowed fallback:
/home/vscode/homelab-worktrees/fix-wireguard-endpoint. Existing user edits in the
main checkout are preserved. Home-level Age/kubeconfig files need no staging.

## Validation
- Red: `TMPDIR="$PWD/.codex/tmp" WG_TEST_LIBSQL="$PWD/.codex/tmp/wireguard-tests/node_modules/@libsql/client/lib-esm/node.js" node tools/vpn/test_defaults.mjs`
  failed against the old script: expected new.example.net, got old.example.net.
- Green: same command passed all six cases with the updated script.
- Development: Job `default/wireguard-endpoint-smoke` on k8s-premium-martin,
  image ghcr.io/wg-easy/wg-easy:15.3.0, ran the same six cases using the actual
  image dependency. All passed; Job Complete. Disposable DB only, no peer data.
  Job and ConfigMap deleted after completion. No production writes.
- `kubectl kustomize kubernetes/infra/network/vpn`: pass; rendered host env
  reference matches wireguard-env/WG_HOST in the defaults initContainer.
- Decrypted semantic comparison: only WG_HOST changed. Port and all other
  plaintext values preserved. All stringData values remain SOPS ciphertext;
  new public address is absent from the encrypted manifest's plaintext.
- `python3 tools/architecture/render.py --check`: pass; generated architecture
  needs no update for these env/script changes.
- `git diff --check`: pass.
- `pre-commit run --files <all nine changed files>`: pass for YAML, whitespace,
  conflict, large-file, Kubernetes schema, and generated architecture checks.
- `python3 tools/codex-harness/validate_sdd_context.py --root "$PWD" --branch codex/fix-wireguard-endpoint --require-plan-artifacts`: pass.

## Validation environment notes
The default Python lacks PyYAML. An isolated validation venv under .codex/tmp
uses installed Python 3.12; uv could not resolve the repository's pinned 3.14.7.
Only YAML utilities ran there. Actual reconciler tests ran with libsql 0.17.3
locally and then inside the exact wg-easy image in development. The development
namespace emitted advisory restricted PodSecurity warnings for the disposable
Job; it ran without privileged mode or host networking. Test resources removed.

## User-path limits and deployment state
The development smoke proves the changed database reconciliation in the actual
runtime, including idempotency and peer preservation. It does not prove WAN UDP
forwarding or cellular browsing. The production-only public endpoint cannot be
accepted through the development network. Acceptance still requires merging,
Flux reconciliation, checking the stored host, and an off-Wi-Fi client handshake
and browsing. Existing downloaded profiles need a one-time endpoint edit.

The encrypted production 1Password shadow item is not the active wireguard-env
consumer and was not migrated or modified by this fix.

## Documentation and convergence
Updated docs/runbooks/wireguard.md with endpoint source, v15 stored-host behavior,
rollout/restart sequencing, and installed-profile limitations. Static IP only;
dynamic DNS is outside this correction. FR-001 through FR-004 are implemented
and verified at the config/reconciler layers. Production acceptance remains
explicitly unverified. Upstream setup reference:
https://wg-easy.github.io/wg-easy/v15.0/advanced/config/unattended-setup/

## Review and handoff
Independent reviewer found an inert INIT_HOST addition: wg-easy 15.3.0 requires
all unattended setup fields before using it. Removed that addition and corrected
the documentation to retain normal fresh setup. The existing-DB reconciliation
remains the intended correction. Plan and evidence record this review lane. Reviewer reported no further
functional or safety findings after correction. Final pre-commit checks passed.
Branch codex/fix-wireguard-endpoint is proposed through a PR; no production
merge or deployment is claimed.
