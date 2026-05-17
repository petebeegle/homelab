"""Markdown rendering for the generated architecture document."""

from __future__ import annotations

from pathlib import Path

from .flux import cluster_flux_kustomizations, flux_table, kustomize_table
from .gateway import gateway_routes
from .kubernetes import Manifest, cluster_vars, kustomize_resources, manifests_under, relative, secret_relationships
from .storage import storage_relationships
from .terraform import terraform_relationships


def render(
    *,
    root: Path,
    clusters: dict[str, Path],
    terraform_roots: dict[str, Path],
) -> str:
    manifests = manifests_under(root / "kubernetes", repo_root=root)
    flux_items: list[tuple[str, Manifest]] = []
    for cluster, cluster_root in clusters.items():
        flux_items.extend(
            (cluster, item)
            for item in cluster_flux_kustomizations(cluster_root, repo_root=root)
        )
    app_flux = [(cluster, item) for cluster, item in flux_items if "/apps/" in item.relpath]
    infra_flux = [(cluster, item) for cluster, item in flux_items if "/infra/" in item.relpath]

    lines: list[str] = [
        "# Architecture",
        "",
        "<!-- GENERATED: do not edit by hand. Run `python3 tools/architecture/render.py --write`. -->",
        "",
        "This document is generated for agentic repo navigation. It records relationships that must stay aligned with the Kubernetes, Flux, and Terraform source of truth.",
        "",
        "## Cluster Entrypoints",
        "",
    ]
    for cluster, cluster_root in clusters.items():
        lines.extend(
            [
                f"### {cluster.title()}",
                "",
                f"- Root Kustomization: `{relative(cluster_root / 'kustomization.yaml', root=root)}`.",
                f"- Root resources: {', '.join(f'`{item}`' for item in kustomize_resources(cluster_root / 'kustomization.yaml'))}.",
                f"- Infra activation list: {', '.join(f'`{item}`' for item in kustomize_resources(cluster_root / 'infra' / 'kustomization.yaml'))}.",
                f"- App activation list: {', '.join(f'`{item}`' for item in kustomize_resources(cluster_root / 'apps' / 'kustomization.yaml'))}.",
                "",
            ]
        )
        branch_templates = cluster_root / "branches" / "kustomization.yaml"
        if branch_templates.exists():
            lines.append(
                f"- Branch environment templates: {', '.join(f'`{item}`' for item in kustomize_resources(branch_templates))}."
            )
            lines.append("")

    lines.extend(
        [
            "### Flux Substitution Variables",
            "",
            "| Cluster | Variable | Value |",
            "| --- | --- | --- |",
        ]
    )
    for cluster, cluster_root in clusters.items():
        lines.extend(f"| `{cluster}` | `{key}` | `{value}` |" for key, value in cluster_vars(cluster_root))

    lines.extend(
        [
            "",
            "## Flux Dependencies",
            "",
            "### Infrastructure",
            "",
            "| Cluster | Kustomization | Path | Depends on | Substitute from | SOPS |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(flux_table(infra_flux))
    lines.extend(
        [
            "",
            "### Applications",
            "",
            "| Cluster | Kustomization | Path | Depends on | Substitute from | SOPS |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(flux_table(app_flux))

    lines.extend(
        [
            "",
            "## Kustomize Resource Relationships",
            "",
            "| Component path | Listed resources |",
            "| --- | --- |",
        ]
    )
    lines.extend(kustomize_table(root / "kubernetes" / "infra", repo_root=root))
    lines.extend(kustomize_table(root / "kubernetes" / "apps", repo_root=root))

    lines.extend(
        [
            "",
            "## Gateway Routes",
            "",
            "| Kind | Route | Hostnames | Parent Gateway | Backend refs |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(gateway_routes(manifests))

    lines.extend(
        [
            "",
            "## Storage Relationships",
            "",
            "| Source | Owner | StorageClass | Path |",
            "| --- | --- | --- | --- |",
        ]
    )
    lines.extend(storage_relationships(manifests, root=root))

    lines.extend(
        [
            "",
            "## Secret Manifests",
            "",
            "This lists secret manifest presence only. Secret values are not rendered.",
            "",
            "| Component | Secret | SOPS encrypted | Path |",
            "| --- | --- | --- | --- |",
        ]
    )
    lines.extend(secret_relationships(manifests, root=root))

    lines.extend(
        [
            "",
            "## Terraform Substrate",
            "",
            "| Root | Type | Name | Source | References |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(terraform_relationships(terraform_roots))
    lines.append("")
    return "\n".join(lines)
