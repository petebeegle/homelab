"""Gateway API route extraction for the architecture renderer."""

from __future__ import annotations

from .kubernetes import Manifest, list_maps, list_scalars


def gateway_routes(manifests: list[Manifest]) -> list[str]:
    rows: list[str] = []
    for item in manifests:
        if item.kind not in {"HTTPRoute", "TLSRoute"}:
            continue
        parents = list_maps(item.text, "parentRefs")
        parent = ", ".join(
            "/".join(
                part
                for part in [
                    ref.get("namespace") or item.namespace or "default",
                    ref.get("name", ""),
                    ref.get("sectionName", ""),
                ]
                if part
            )
            for ref in parents
        )
        hosts = ", ".join(list_scalars(item.text, "hostnames")) or "(none)"
        backends = ", ".join(
            f"{ref.get('name', '?')}:{ref.get('port', '?')}" for ref in list_maps(item.text, "backendRefs")
        )
        rows.append(
            f"| `{item.kind}` | `{item.namespace}/{item.name}` | `{hosts}` | `{parent or '(none)'}` | `{backends or '(none)'}` |"
        )
    return sorted(rows)
