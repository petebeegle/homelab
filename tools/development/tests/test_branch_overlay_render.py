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
    "home-assistant": "kubernetes/apps/home-assistant",
    "jellyfin": "kubernetes/apps/jellyfin",
}

# Services a HelmRelease renders at deploy time (so `kubectl kustomize` cannot show them).
HELM_RENDERED_SERVICES = {
    "jellyfin": {"jellyfin"},
}

# Pod volumes a branch overlay may swap for something development can provide, and why.
# Everything else in the pod spec must equal the real manifest.
SWAPPED_VOLUMES = {
    "home-assistant": {"home-assistant-secrets": "the SOPS Secret is production-only; placeholders come from a ConfigMap"},
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


def pod_block_at(doc: str, key: str, indent: int) -> str:
    """The lines of a top-level-ish block starting at `key` with the given indentation."""
    lines = doc.splitlines()
    try:
        start = lines.index(" " * indent + key)
    except ValueError:
        return ""
    block = [lines[start]]
    for line in lines[start + 1 :]:
        if line.strip() and len(line) - len(line.lstrip()) <= indent and not line.lstrip().startswith("- "):
            break
        block.append(line)
    return "\n".join(block)


def data_of(doc: str) -> str:
    return doc[doc.index("\ndata:\n") : doc.index("\nkind:")] if "\ndata:\n" in doc else ""


def without_volumes(block: str, names: set[str]) -> str:
    """A `volumes:` block with the named entries removed (each entry starts at "      - ")."""
    if not names or not block:
        return block
    header, *rest = block.splitlines()
    entries: list[list[str]] = []
    for line in rest:
        if line.startswith("      - ") or not entries:
            entries.append([line])
        else:
            entries[-1].append(line)
    kept = [entry for entry in entries if not any(re.fullmatch(rf"\s*(- )?name: {re.escape(n)}", l) for l in entry for n in names)]
    return "\n".join([header, *(line for entry in kept for line in entry)])


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
            if not real and any(kind_of(d) == "HelmRelease" for d in documents(kustomize(real_dir))):
                continue  # compared by test_helm_release_apps_deploy_productions_chart_values_and_patches
            self.assertTrue(real, f"{app}: no Deployment rendered from {real_dir}")
            self.assertEqual(sorted(real), sorted(branch), f"{app}: Deployments differ")
            swapped = set(SWAPPED_VOLUMES.get(app, {}))
            for name, real_doc in real.items():
                for key in POD_SPEC_KEYS:
                    self.assertEqual(
                        without_volumes(pod_block(real_doc, key), swapped),
                        without_volumes(pod_block(branch[name], key).replace(SUFFIX, ""), swapped),
                        f"{app}/{name}: {key.rstrip(':')} differ from the real manifest",
                    )

    def test_a_swapped_volume_keeps_its_name_and_is_still_mounted(self) -> None:
        for app, swapped in SWAPPED_VOLUMES.items():
            for doc in documents(kustomize(f"kubernetes/apps/{app}/branch")):
                if kind_of(doc) != "Deployment":
                    continue
                volumes = pod_block(doc, "volumes:")
                for name in swapped:
                    self.assertNotEqual(without_volumes(volumes, {name}), volumes, f"{app}: volume {name} is gone")

    def test_home_assistant_branch_has_no_secret_and_reaches_only_the_internal_gateway(self) -> None:
        docs = documents(kustomize("kubernetes/apps/home-assistant/branch"))
        self.assertEqual([d for d in docs if kind_of(d) == "Secret"], [], "development cannot decrypt the SOPS Secret")
        route = next(d for d in docs if kind_of(d) == "HTTPRoute")
        self.assertEqual(re.findall(r"(?m)^  - name: (internal|external)$", route), ["internal"])

    def test_helm_release_apps_deploy_productions_chart_values_and_patches(self) -> None:
        # The chart, its values and production's post-render patches must reach the branch
        # unchanged; a branch may only append post-render patches (for what development lacks).
        for app, real_dir in REAL_DIRS.items():
            real_docs = documents(kustomize(real_dir))
            real_releases = [d for d in real_docs if kind_of(d) == "HelmRelease"]
            if not real_releases:
                continue
            branch_docs = documents(kustomize(f"kubernetes/apps/{app}/branch"))
            branch_releases = {name_of(d).removesuffix(SUFFIX): d for d in branch_docs if kind_of(d) == "HelmRelease"}
            for real in real_releases:
                branch = branch_releases[name_of(real)]
                for pattern in (r"(?m)^      chart: (\S+)$", r"(?m)^      version: (\S+)$", r"(?m)^  releaseName: (\S+)$"):
                    self.assertEqual(field(real, pattern), field(branch, pattern), f"{app}: {pattern}")
                real_patches = pod_block_at(real, "postRenderers:", 2)
                branch_patches = pod_block_at(branch, "postRenderers:", 2)
                self.assertTrue(branch_patches.startswith(real_patches.rstrip()), f"{app}: production's post-render patches changed")
            real_values = [d for d in real_docs if kind_of(d) == "ConfigMap" and "values.yaml:" in d]
            branch_values = [d for d in branch_docs if kind_of(d) == "ConfigMap" and "values.yaml:" in d]
            self.assertEqual([data_of(d) for d in real_values], [data_of(d) for d in branch_values], f"{app}: values differ")

    def test_profile_checked_objects_are_rendered(self) -> None:
        for app in smoke_tested_apps():
            profile = json.loads((PROFILES / f"{app}.json").read_text(encoding="utf-8"))
            docs = documents(kustomize(f"kubernetes/apps/{app}/branch"))
            names = {kind: {name_of(d) for d in docs if kind_of(d) == kind} for kind in ("Namespace", "Service", "HTTPRoute")}
            self.assertIn(profile["namespace"], names["Namespace"], app)
            for service in profile["checks"].get("services", []):
                self.assertIn(service, names["Service"] | HELM_RENDERED_SERVICES.get(app, set()), app)
            for route in profile["checks"].get("httpRoutes", []):
                self.assertIn(route, names["HTTPRoute"], app)

    def test_every_route_backend_is_a_service_in_the_branch_environment(self) -> None:
        # kustomize renames Services but does not follow names inside Gateway API routes, so an
        # overlay can render a route that points at a Service that does not exist.
        for app in smoke_tested_apps():
            docs = documents(kustomize(f"kubernetes/apps/{app}/branch"))
            services = {name_of(d) for d in docs if kind_of(d) == "Service"} | HELM_RENDERED_SERVICES.get(app, set())
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

    def test_homepage_allows_the_hosts_the_smoke_probe_and_route_send(self) -> None:
        # Since homepage v2 the HOMEPAGE_ALLOWED_HOSTS check covers pages, not only /api, so the
        # in-cluster probe (Host: <service>.<namespace>.svc.cluster.local) gets HTTP 400 unless
        # that host is allowed alongside the route hostname.
        profile = json.loads((PROFILES / "homepage.json").read_text(encoding="utf-8"))
        docs = documents(kustomize("kubernetes/apps/homepage/branch"))
        deployment = next(d for d in docs if kind_of(d) == "Deployment")
        allowed = field(deployment, r"name: HOMEPAGE_ALLOWED_HOSTS\n\s+value: (\S+)$")
        self.assertIsNotNone(allowed, "homepage Deployment does not set HOMEPAGE_ALLOWED_HOSTS")
        allowed_hosts = set(allowed.split(","))
        for probe in profile["checks"]["httpProbes"]:
            host = f"{probe['service']}.{profile['namespace']}.svc.cluster.local"
            if probe["port"] != 80:
                host = f"{host}:{probe['port']}"
            self.assertIn(host, allowed_hosts, "the dev-smoke HTTP probe would get HTTP 400")
        for doc in docs:
            if kind_of(doc) == "HTTPRoute":
                for hostname in re.findall(r"(?m)^  hostnames:\n((?:  - \S+\n)+)", doc + "\n"):
                    for name in re.findall(r"- (\S+)", hostname):
                        self.assertIn(name, allowed_hosts, f"route hostname {name} would get HTTP 400")

    def test_homepage_probe_checks_the_merged_services_config(self) -> None:
        # The merge-config init container (mikefarah/yq) writes services.yaml. A probe of "/"
        # only matches page chrome, so a yq bump that emptied the config would still pass.
        # One probe must read /api/services and expect a service the branch config defines.
        profile = json.loads((PROFILES / "homepage.json").read_text(encoding="utf-8"))
        api_probes = [p for p in profile["checks"]["httpProbes"] if p["path"] == "/api/services"]
        self.assertTrue(api_probes, "no dev-smoke probe reads /api/services")
        docs = documents(kustomize("kubernetes/apps/homepage/branch"))
        services_config = "\n".join(
            d for d in docs if kind_of(d) == "ConfigMap" and "services.yaml:" in d
        )
        self.assertTrue(services_config, "branch environment renders no services.yaml")
        for probe in api_probes:
            expected = re.search(probe["bodyRegex"], services_config)
            self.assertIsNotNone(
                expected, f"/api/services probe expects {probe['bodyRegex']!r}, which services.yaml lacks"
            )
            self.assertNotRegex("Home Lab Homepage Branch", probe["bodyRegex"], "regex must not match page chrome")


if __name__ == "__main__":
    unittest.main()
