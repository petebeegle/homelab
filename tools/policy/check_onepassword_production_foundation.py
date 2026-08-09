#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


def read(root: Path, relative: str) -> str:
    path = root / relative
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def require(text: str, pattern: str, message: str) -> list[str]:
    return [] if re.search(pattern, text, re.MULTILINE) else [message]


def check_item_metric_safety(root: Path) -> list[str]:
    metrics = read(
        root, "kubernetes/infra/monitoring/kube-state-metrics/config/metrics.yaml"
    )
    item_block = re.search(
        r"(?ms)^\s*- groupVersionKind:\n\s+group: onepassword\.com\b.*?(?=^\s*- groupVersionKind:|\Z)",
        metrics,
    )
    if item_block is None:
        return []
    if re.search(
        r"(?:path|value|valueFrom|labelsFromPath):[^\n]*(?:secret|password|credential|token)",
        item_block.group(0),
        re.IGNORECASE,
    ):
        return ["Secret data path is forbidden in the OnePasswordItem metric configuration"]
    return []


def check_repository(root: Path) -> list[str]:
    errors: list[str] = []
    prod_kustomization = read(root, "kubernetes/clusters/production/infra/kustomization.yaml")
    prod_operator = read(root, "kubernetes/clusters/production/infra/onepassword-operator.yaml")
    terraform_main = read(root, "terraform/production/main.tf")
    terraform_variables = read(root, "terraform/production/variables.tf")
    metrics = read(root, "kubernetes/infra/monitoring/kube-state-metrics/config/metrics.yaml")
    alert_kustomization = read(root, "kubernetes/infra/monitoring/grafana/alerting/kustomization.yaml")
    alerts = read(root, "kubernetes/infra/monitoring/grafana/alerting/alert-rules-onepassword.yaml")

    errors += require(prod_kustomization, r"(?m)^  - onepassword-operator\.yaml$", "production must activate onepassword-operator")
    errors += require(prod_operator, r"path: \./kubernetes/infra/controllers/onepassword-operator", "production must reuse the shared operator")
    errors += require(prod_operator, r"(?s)dependsOn:.*- name: crds", "operator must depend on CRDs")
    errors += require(terraform_main, r'FLUX_BOOTSTRAP_SECRET_PROVIDER\s*=\s*"dual"', "production bootstrap must use dual mode")
    errors += require(terraform_main, r"OP_SERVICE_ACCOUNT_TOKEN_REF\s*=\s*var\.onepassword_service_account_token_ref", "production must pass only the token reference")
    errors += require(terraform_variables, r'op://cluster bootstrap/onepassword-production-operator/credential', "production token reference is missing")
    errors += require(metrics, r"(?s)group: onepassword\.com.*kind: OnePasswordItem.*name: \"item_info\"", "OnePasswordItem readiness metric is missing")
    errors += require(metrics, r"(?s)apiGroups:.*- onepassword\.com.*resources:.*- onepassworditems.*verbs: \[\"list\", \"watch\", \"get\"\]", "OnePasswordItem least-privilege RBAC is missing")
    errors += check_item_metric_safety(root)
    errors += require(alert_kustomization, r"alert-rules-onepassword\.yaml", "1Password alert rules are not activated")
    errors += require(alerts, r"uid: onepassword-operator-unavailable", "operator-unavailable alert is missing")
    errors += require(alerts, r"absent\(kube_deployment_spec_replicas", "operator alert must detect a missing Deployment")
    errors += require(alerts, r"uid: onepassword-item-unready", "item-unready alert is missing")
    errors += require(alerts, r'onepassword_item_info\{ready!="True"\}', "item alert must detect every non-True Ready state")
    if alerts.count("for: 10m") != 2:
        errors.append("both 1Password alerts must use a ten-minute pending duration")
    if alerts.count("execErrState: Error") != 2:
        errors.append("both 1Password alerts must surface evaluation errors")

    production_tree = root / "kubernetes/clusters/production"
    sops_age_references = sum(
        path.read_text(encoding="utf-8").count("name: sops-age")
        for path in production_tree.rglob("*.yaml")
    )
    if sops_age_references < 1:
        errors.append("production must retain the sops-age trust root and consumers")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    errors = check_repository(root)
    if errors:
        for error in errors:
            print(f"onepassword production policy: {error}", file=sys.stderr)
        return 1
    print("1Password production foundation policy passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
