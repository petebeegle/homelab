# Production Bootstrap Contract

- Production Terraform invokes the shared bootstrap with `FLUX_BOOTSTRAP_SECRET_PROVIDER=dual`.
- `OP_SERVICE_ACCOUNT_TOKEN_REF` is a validated `op://` reference and is not sensitive data.
- The token value is obtained only by `op read --no-newline` redirected to a mode-0600 temporary file.
- The helper creates/updates `flux-system/sops-age` and `onepassword-system/onepassword-service-account-token` without value output.
- Failures occur before applying an empty/unreadable token.
- Repeated execution is idempotent.
