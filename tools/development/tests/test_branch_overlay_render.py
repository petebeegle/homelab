from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PROFILES = REPO_ROOT / "tools" / "development" / "smoke-profiles"
SUFFIX = "-${branch_slug}"
WORKLOAD_KIND = re.compile(r"(?m)^kind: (Deployment|StatefulSet|DaemonSet|Job|CronJob)\s*$")
POD_SPEC_KEYS = ("initContainers:", "containers:", "volumes:")

# The directory the development cluster itself deploys for each smoke-tested app.
REAL_DIRS = {
    "whoami": "kubernetes/apps/whoami",
    "homepage": "kubernetes/apps/homepage/development",
}


def smoke_tested_apps() -> list[str]:
    apps = []
    for path in sorted(PROFILES.glob("*.json")):
        profile = json.loads(path.read_text(encoding="utf-8"))
        if profile.get("prSmoke") is True:
            apps.append(profile["app"])
    return apps


def kustomize(relative: str) -> str:
    if shutil.which("kubectl") is None:
        if os.environ.get("GITHUB_ACTIONS"):
            raise AssertionError("kubectl is required in CI to render the branch overlays")
        raise unittest.SkipTest("kubectl not installed")
    result = subprocess.run(["kubectl", "kustomize", relative], cwd=REPO_ROOT, capture_output=True, text=True)
    assert result.returncode == 0, f"kubectl kustomize {relative} failed: {result.stderr}"
    return result.stdout


def documents(text: str) -> list[str]:
    return [doc for doc in text.split("\n---\n") if doc.strip()]


def field(doc: str, pattern: str) -> str | None:
    match = re.search(pattern, doc, re.M)
    return match.group(1) if match else None


def kind_of(doc: str) -> str | None:
    return field(doc, r"^kind: (\S+)$")


def name_of(doc: str) -> str | None:
    return field(doc, r"^  name: (\S+)$")


def pod_block(doc: str, key: str) -> str:
    """The text of a pod-spec section (kubectl kustomize output is sorted and uses fixed indentation)."""
    lines = doc.splitlines()
    try:
        start = lines.index("      " + key)
    except ValueError:
        return ""
    block = [lines[start]]
    for line in lines[start + 1 :]:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            if indent < 6 or (indent == 6 and not line.lstrip().startswith("- ")):
                break
        block.append(line)
    return "\n".join(block)


class BranchOverlayRenderTest(unittest.TestCase):
    """The PR smoke test deploys kubernetes/apps/<app>/branch/. It must be the real app, renamed,
    so a green dev-smoke means the change in the real manifests was exercised."""

    def test_every_smoke_tested_app_has_a_real_directory_to_compare_against(self) -> None:
        self.assertEqual(sorted(REAL_DIRS), smoke_tested_apps())

    def test_branch_directory_holds_no_copy_of_a_workload(self) -> None:
        for app in smoke_tested_apps():
            for path in sorted((REPO_ROOT / "kubernetes" / "apps" / app / "branch").rglob("*.yaml")):
                self.assertIsNone(
                    WORKLOAD_KIND.search(path.read_text(encoding="utf-8")),
                    f"{path.relative_to(REPO_ROOT)} defines a workload; build the branch overlay on the real manifests instead",
                )

    def test_container_specs_equal_the_real_manifest_apart_from_the_slug_suffix(self) -> None:
        for app, real_dir in REAL_DIRS.items():
            real = {name_of(d): d for d in documents(kustomize(real_dir)) if kind_of(d) == "Deployment"}
            branch = {
                name_of(d).removesuffix(SUFFIX): d
                for d in documents(kustomize(f"kubernetes/apps/{app}/branch"))
                if kind_of(d) == "Deployment"
            }
            self.assertTrue(real, f"{app}: no Deployment rendered from {real_dir}")
            self.assertEqual(sorted(real), sorted(branch), f"{app}: Deployments differ")
            for name, real_doc in real.items():
                for key in POD_SPEC_KEYS:
                    self.assertEqual(
                        pod_block(real_doc, key),
                        pod_block(branch[name], key).replace(SUFFIX, ""),
                        f"{app}/{name}: {key.rstrip(':')} differ from the real manifest",
                    )

    def test_profile_checked_objects_are_rendered(self) -> None:
        for app in smoke_tested_apps():
            profile = json.loads((PROFILES / f"{app}.json").read_text(encoding="utf-8"))
            docs = documents(kustomize(f"kubernetes/apps/{app}/branch"))
            names = {kind: {name_of(d) for d in docs if kind_of(d) == kind} for kind in ("Namespace", "Service", "HTTPRoute")}
            self.assertIn(profile["namespace"], names["Namespace"], app)
            for service in profile["checks"].get("services", []):
                self.assertIn(service, names["Service"], app)
            for route in profile["checks"].get("httpRoutes", []):
                self.assertIn(route, names["HTTPRoute"], app)

    def test_every_route_backend_is_a_service_in_the_branch_environment(self) -> None:
        # kustomize renames Services but does not follow names inside Gateway API routes, so an
        # overlay can render a route that points at a Service that does not exist.
        for app in smoke_tested_apps():
            docs = documents(kustomize(f"kubernetes/apps/{app}/branch"))
            services = {name_of(d) for d in docs if kind_of(d) == "Service"}
            for doc in docs:
                if kind_of(doc) != "HTTPRoute":
                    continue
                backends = re.findall(r"(?m)^\s+- name: (\S+)\n\s+port: ", doc)
                self.assertTrue(backends, f"{app}: route {name_of(doc)} has no backendRefs")
                for backend in backends:
                    self.assertIn(backend, services, f"{app}: route {name_of(doc)} sends traffic to missing Service {backend}")

    def test_branch_objects_never_collide_with_the_real_ones(self) -> None:
        for app in smoke_tested_apps():
            docs = documents(kustomize(f"kubernetes/apps/{app}/branch"))
            for doc in docs:
                kind, name = kind_of(doc), name_of(doc)
                if kind in ("ClusterRole", "ClusterRoleBinding", "Namespace"):
                    self.assertTrue(name.endswith(SUFFIX), f"{app}: cluster-scoped {kind}/{name} would clobber the real one")
                namespace = field(doc, r"^  namespace: (\S+)$")
                if namespace is not None:
                    self.assertIn(namespace, (f"{app}{SUFFIX}", "gateway"), f"{app}: {kind}/{name} is in namespace {namespace}")


if __name__ == "__main__":
    unittest.main()
