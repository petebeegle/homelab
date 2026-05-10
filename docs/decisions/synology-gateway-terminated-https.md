# Synology Gateway-Terminated HTTPS

## Status

Accepted.

## Decision

Expose Synology DSM at `synology.petebeegle.com` through the Cilium internal Gateway with Gateway-terminated HTTPS. The Gateway presents a cert-manager certificate for `synology.petebeegle.com` and proxies DSM over HTTPS to the NAS on port 5001.

## Rationale

- DSM's built-in certificate for `192.168.30.99:5001` is not trusted for `synology.petebeegle.com`.
- Gateway termination lets cert-manager issue and renew the public hostname certificate.
- Users should access DSM without a visible backend port.
- Authentik and DSM SSO should use the same public URL.

## Consequences

- DNS for `synology.petebeegle.com` must point at the internal Gateway IP, not directly at the NAS.
- Synology uses an `HTTPRoute` to the internal Gateway instead of a `TLSRoute` to the passthrough Gateway.
- The Synology Service advertises `appProtocol: https` so Cilium uses HTTPS to reach DSM and avoids DSM's HTTP-to-HTTPS redirect to `:5001`.
- Use `HTTPRoute` for external services when the cluster should provide the trusted certificate or hide backend ports.
- Use `TLSRoute` passthrough only when the external target should terminate TLS itself and presents an acceptable certificate for the hostname.
