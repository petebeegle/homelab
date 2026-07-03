from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[3]
TOOLS_DEVELOPMENT = REPO_ROOT / "tools" / "development"
SHIM_PATH = TOOLS_DEVELOPMENT / "verify_branch_deploy.py"
if str(TOOLS_DEVELOPMENT) not in sys.path:
    sys.path.insert(0, str(TOOLS_DEVELOPMENT))

import devverify as verify


READY_HTTPROUTE = """{
  "status": {
    "parents": [
      {
        "conditions": [
          {"type": "Accepted", "status": "True"},
          {"type": "ResolvedRefs", "status": "True"}
        ]
      }
    ]
  }
}"""

READY_TLSROUTE = READY_HTTPROUTE

READY_PODS = json.dumps(
    {
        "items": [
            {
                "metadata": {"name": "whoami-example-change-7d9c4", "namespace": "whoami-example-change"},
                "status": {"phase": "Running", "conditions": [{"type": "Ready", "status": "True"}]},
            }
        ]
    }
)

READY_JELLYFIN_PODS = json.dumps(
    {
        "items": [
            {
                "metadata": {"name": "jellyfin-example-change-75f8d", "namespace": "jellyfin-example-change"},
                "status": {"phase": "Running", "conditions": [{"type": "Ready", "status": "True"}]},
            }
        ]
    }
)

READY_HOME_ASSISTANT_PODS = json.dumps(
    {
        "items": [
            {
                "metadata": {"name": "home-assistant-example-change-6f7d8", "namespace": "home-assistant-example-change"},
                "status": {"phase": "Running", "conditions": [{"type": "Ready", "status": "True"}]},
            }
        ]
    }
)

READY_PVC = json.dumps(
    {
        "metadata": {"name": "jellyfin-config-example-change", "namespace": "jellyfin-example-change"},
        "spec": {"storageClassName": "nfs-csi-storage"},
        "status": {"phase": "Bound"},
    }
)

READY_HOME_ASSISTANT_PVC = json.dumps(
    {
        "metadata": {"name": "home-assistant-config-example-change", "namespace": "home-assistant-example-change"},
        "spec": {"storageClassName": "nfs-csi-storage"},
        "status": {"phase": "Bound"},
    }
)

PENDING_PVC = json.dumps(
    {
        "metadata": {"name": "jellyfin-config-example-change", "namespace": "jellyfin-example-change"},
        "spec": {"storageClassName": "nfs-csi-storage"},
        "status": {"phase": "Pending"},
    }
)

MIXED_PODS = json.dumps(
    {
        "items": [
            {
                "metadata": {"name": "complete", "namespace": "whoami-example-change"},
                "status": {"phase": "Succeeded", "conditions": [{"type": "Ready", "status": "False"}]},
            },
            {
                "metadata": {
                    "name": "deleting",
                    "namespace": "whoami-example-change",
                    "deletionTimestamp": "2026-05-15T00:00:00Z",
                },
                "status": {"phase": "Running", "conditions": [{"type": "Ready", "status": "False"}]},
            },
            {
                "metadata": {"name": "active", "namespace": "whoami-example-change"},
                "status": {"phase": "Running", "conditions": [{"type": "Ready", "status": "True"}]},
            },
        ]
    }
)

NO_ACTIVE_PODS = json.dumps(
    {
        "items": [
            {
                "metadata": {"name": "complete", "namespace": "whoami-example-change"},
                "status": {"phase": "Succeeded"},
            }
        ]
    }
)


TEMPLATE = """---
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: branch-${branch_slug}
  namespace: flux-system
spec:
  suspend: true
  ref:
    branch: ${branch_name}
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: branch-whoami-${branch_slug}
  namespace: flux-system
spec:
  suspend: true
  sourceRef:
    name: branch-${branch_slug}
"""


class FakeRunner:
    quiet = True

    def __init__(
        self,
        *,
        plan_returncode: int = 0,
        fail_on: str | None = None,
        timeout_on: str | None = None,
        pods_json: str = READY_PODS,
        cluster_pods_json: str = READY_PODS,
        pvc_json: str = READY_PVC,
    ) -> None:
        self.plan_returncode = plan_returncode
        self.fail_on = fail_on
        self.timeout_on = timeout_on
        self.pods_json = pods_json
        self.cluster_pods_json = cluster_pods_json
        self.pvc_json = pvc_json
        self.calls: list[tuple[list[str], dict[str, object]]] = []

    def __call__(self, args: list[str], **kwargs: object) -> SimpleNamespace:
        self.calls.append((args, kwargs))
        command = " ".join(args)
        if self.timeout_on and self.timeout_on in command:
            raise subprocess.TimeoutExpired(args, kwargs.get("timeout"))
        if self.fail_on and self.fail_on in command:
            return SimpleNamespace(returncode=1, stdout="")
        if args[0] == "terraform" and "plan" in args:
            return SimpleNamespace(returncode=self.plan_returncode, stdout="")
        if args[-5:] == ["get", "pods", "--all-namespaces", "-o", "json"]:
            return SimpleNamespace(returncode=0, stdout=self.cluster_pods_json)
        if args[-4:] == ["get", "pods", "-o", "json"]:
            return SimpleNamespace(returncode=0, stdout=self.pods_json)
        if "get" in args and "httproute" in args and args[-2:] == ["-o", "json"]:
            return SimpleNamespace(returncode=0, stdout=READY_HTTPROUTE)
        if "get" in args and "tlsroute" in args and args[-2:] == ["-o", "json"]:
            return SimpleNamespace(returncode=0, stdout=READY_TLSROUTE)
        if "get" in args and "pvc" in args and args[-2:] == ["-o", "json"]:
            return SimpleNamespace(returncode=0, stdout=self.pvc_json)
        return SimpleNamespace(returncode=0, stdout="")

    @property
    def commands(self) -> list[list[str]]:
        return [call[0] for call in self.calls]


class VerifyBranchDeployTest(unittest.TestCase):
    def test_cli_shim_remains_executable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SHIM_PATH), "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Verify an app branch environment", result.stdout)

    def test_profile_loading_discovers_current_supported_apps(self) -> None:
        profiles = verify.load_smoke_profiles()

        self.assertEqual(set(profiles), {"home-assistant", "jellyfin", "whoami"})
        self.assertEqual(profiles["whoami"].activation_template, "kubernetes/clusters/development/branches/whoami-template.yaml")
        self.assertEqual(profiles["whoami"].git_repository, "branch-${branch_slug}")
        self.assertEqual(profiles["whoami"].kustomizations, ("branch-whoami-${branch_slug}",))
        self.assertEqual(profiles["whoami"].route_urls, ("https://whoami-${branch_slug}.dev.lab.petebeegle.com",))
        self.assertEqual(profiles["jellyfin"].git_repository, "branch-jellyfin-${branch_slug}")
        self.assertEqual(profiles["jellyfin"].kustomizations, ("branch-jellyfin-${branch_slug}",))
        self.assertEqual(profiles["jellyfin"].pvcs[0].name, "jellyfin-config-${branch_slug}")
        self.assertEqual(profiles["home-assistant"].git_repository, "branch-home-assistant-${branch_slug}")
        self.assertEqual(profiles["home-assistant"].kustomizations, ("branch-home-assistant-${branch_slug}",))
        self.assertEqual(profiles["home-assistant"].pvcs[0].name, "home-assistant-config-${branch_slug}")

    def test_supported_apps_are_loaded_from_profile_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            profile_dir = Path(tmp)
            (profile_dir / "custom.json").write_text(
                json.dumps(
                    {
                        "app": "custom",
                        "activationTemplate": "template.yaml",
                        "namespace": "custom-${branch_slug}",
                        "routeUrls": ["https://custom-${branch_slug}.dev.lab.petebeegle.com"],
                        "checks": {
                            "kustomizations": ["branch-custom-${branch_slug}"],
                            "services": ["custom-${branch_slug}"],
                            "tlsRoutes": ["custom-${branch_slug}"],
                            "secretRefs": ["custom-secret-${branch_slug}"],
                        },
                    }
                ),
                encoding="utf-8",
            )

            profiles = verify.load_smoke_profiles(profile_dir)

            self.assertEqual(verify.supported_apps(profile_dir), frozenset({"custom"}))
            self.assertEqual(profiles["custom"].kustomizations, ("branch-custom-${branch_slug}",))
            self.assertEqual(profiles["custom"].tls_routes, ("custom-${branch_slug}",))
            self.assertEqual(profiles["custom"].secret_refs, ("custom-secret-${branch_slug}",))
            self.assertEqual(profiles["custom"].route_urls, ("https://custom-${branch_slug}.dev.lab.petebeegle.com",))

    def test_branch_validation_accepts_common_git_branch_name(self) -> None:
        self.assertEqual(verify.validate_branch("codex/example-change"), "codex/example-change")

    def test_branch_validation_rejects_git_invalid_patterns(self) -> None:
        for branch in (
            "bad..branch",
            ".bad",
            "good/.bad",
            "bad.",
            "good/bad.",
            "good/bad.lock",
            "bad//branch",
            "bad@{branch",
            "bad branch",
            "-bad",
        ):
            with self.subTest(branch=branch):
                with self.assertRaises(argparse.ArgumentTypeError):
                    verify.validate_branch(branch)

    def test_slug_validation_accepts_dns_safe_slug(self) -> None:
        self.assertEqual(verify.validate_slug("example-change"), "example-change")
        self.assertEqual(verify.validate_slug("a1"), "a1")

    def test_slug_validation_rejects_non_deterministic_or_dns_unsafe_slug(self) -> None:
        for slug in ("Example", "-example", "example-", "example_change", "a" * 57):
            with self.subTest(slug=slug):
                with self.assertRaises(argparse.ArgumentTypeError):
                    verify.validate_slug(slug)

    def test_template_rendering_substitutes_branch_and_unsuspends_flux_objects(self) -> None:
        rendered = verify.render_activation_template(TEMPLATE, branch="codex/example-change", slug="example-change")

        self.assertIn("name: branch-example-change", rendered)
        self.assertIn("branch: codex/example-change", rendered)
        self.assertEqual(rendered.count("suspend: false"), 2)
        self.assertNotIn("${", rendered)

    def test_timeout_parsing_supports_seconds_minutes_and_composites(self) -> None:
        self.assertEqual(verify.parse_duration("300").raw, "300s")
        self.assertEqual(verify.parse_duration("10m").seconds, 600)
        self.assertEqual(verify.parse_duration("1h30m5s").seconds, 5405)
        with self.assertRaises(argparse.ArgumentTypeError):
            verify.parse_duration("soon")

    def test_print_route_urls_renders_profile_urls_without_cluster_access(self) -> None:
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            result = verify.main(
                [
                    "--app",
                    "whoami",
                    "--branch",
                    "codex/example-change",
                    "--slug",
                    "example-change",
                    "--print-route-urls",
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(stdout.getvalue().strip(), "https://whoami-example-change.dev.lab.petebeegle.com")

    def test_run_command_wraps_subprocess_timeout(self) -> None:
        config = self._config()
        runner = FakeRunner(timeout_on="rollout")

        with self.assertRaisesRegex(verify.VerificationError, "timed out"):
            verify.run_command(
                verify.kubectl(config, "-n", config.namespace, "rollout", "status", f"deployment/{config.namespace}"),
                runner=runner,
                timeout=config.timeout,
            )

    def test_acceptance_command_sequence_uses_push_terraform_apply_reconcile_assert_and_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "terraform" / "development").mkdir(parents=True)
            runner = FakeRunner(plan_returncode=2)
            config = self._config(push=True, terraform_apply=True)

            verify.run_acceptance(config, runner=runner, repo_root=root, template_text=TEMPLATE)

        commands = [" ".join(command) for command in runner.commands]
        self.assertIn("git push origin HEAD:refs/heads/codex/example-change", commands[0])
        self.assertTrue(any("terraform -chdir=" in command and " init -input=false -no-color" in command for command in commands))
        self.assertTrue(
            any("terraform -chdir=" in command and " plan -detailed-exitcode -input=false -no-color" in command for command in commands)
        )
        self.assertTrue(any("terraform -chdir=" in command and " apply -input=false -no-color -auto-approve" in command for command in commands))
        self.assertTrue(any("flux --kubeconfig /tmp/kubeconfig reconcile source git branch-example-change" in command for command in commands))
        self.assertTrue(any("get pods -o json" in command for command in commands))
        self.assertTrue(any("wait pod/whoami-example-change-7d9c4 --for=condition=Ready" in command for command in commands))
        self.assertTrue(any("get service whoami-example-change" in command for command in commands))
        self.assertTrue(any("get httproute whoami-example-change -o json" in command for command in commands))
        self.assertTrue(any("delete kustomization.kustomize.toolkit.fluxcd.io/branch-whoami-example-change" in command for command in commands))
        self.assertTrue(any("wait namespace/whoami-example-change --for=delete" in command for command in commands))
        self.assertTrue(any("delete gitrepository.source.toolkit.fluxcd.io/branch-example-change" in command for command in commands))

    def test_apply_uses_rendered_activation_stdin(self) -> None:
        runner = FakeRunner()
        config = self._config()
        rendered = verify.render_activation_template(TEMPLATE, branch=config.branch, slug=config.slug)

        verify.apply_activation(config, rendered, runner=runner)

        command, kwargs = runner.calls[0]
        self.assertEqual(command, ["kubectl", "--kubeconfig", "/tmp/kubeconfig", "apply", "-f", "-"])
        self.assertEqual(kwargs["input"], rendered)

    def test_httproute_assert_requires_accepted_and_resolved_refs_on_one_parent(self) -> None:
        missing_resolved_refs = """{
          "status": {
            "parents": [
              {"conditions": [{"type": "Accepted", "status": "True"}]},
              {"conditions": [{"type": "ResolvedRefs", "status": "True"}]}
            ]
          }
        }"""

        with self.assertRaisesRegex(verify.VerificationError, "Accepted and ResolvedRefs"):
            verify.assert_httproute_ready(missing_resolved_refs, route_name="whoami-example-change")

    def test_tlsroute_assert_requires_accepted_and_resolved_refs_on_one_parent(self) -> None:
        missing_resolved_refs = """{
          "status": {
            "parents": [
              {"conditions": [{"type": "Accepted", "status": "True"}]},
              {"conditions": [{"type": "ResolvedRefs", "status": "True"}]}
            ]
          }
        }"""

        with self.assertRaisesRegex(verify.VerificationError, "Accepted and ResolvedRefs"):
            verify.assert_tlsroute_ready(missing_resolved_refs, route_name="whoami-example-change")

    def test_pod_readiness_waits_for_active_pods(self) -> None:
        runner = FakeRunner()
        config = self._config()

        verify.wait_for_active_pods_ready(
            config,
            runner=runner,
            namespace=config.namespace,
            require_non_terminated=True,
            context=f"namespace {config.namespace}",
        )

        commands = [" ".join(command) for command in runner.commands]
        self.assertEqual(commands[0], "kubectl --kubeconfig /tmp/kubeconfig -n whoami-example-change get pods -o json")
        self.assertTrue(any("wait pod/whoami-example-change-7d9c4 --for=condition=Ready" in command for command in commands))

    def test_pod_readiness_ignores_completed_and_deleting_pods(self) -> None:
        runner = FakeRunner(pods_json=MIXED_PODS)
        config = self._config()

        verify.wait_for_active_pods_ready(
            config,
            runner=runner,
            namespace=config.namespace,
            require_non_terminated=True,
            context=f"namespace {config.namespace}",
        )

        commands = [" ".join(command) for command in runner.commands]
        self.assertTrue(any("wait pod/active --for=condition=Ready" in command for command in commands))
        self.assertFalse(any("wait pod/complete" in command for command in commands))
        self.assertFalse(any("wait pod/deleting" in command for command in commands))

    def test_branch_app_pods_require_at_least_one_non_terminated_pod(self) -> None:
        runner = FakeRunner(pods_json=NO_ACTIVE_PODS)

        with self.assertRaisesRegex(verify.VerificationError, "no non-terminated pods"):
            verify.assert_whoami(self._config(), runner=runner)

    def test_whoami_assert_preserves_service_and_route_checks(self) -> None:
        runner = FakeRunner()
        config = self._config()

        verify.assert_whoami(config, runner=runner)

        commands = [" ".join(command) for command in runner.commands]
        self.assertTrue(any("wait kustomization.kustomize.toolkit.fluxcd.io/branch-whoami-example-change" in command for command in commands))
        self.assertTrue(any("get service whoami-example-change" in command for command in commands))
        self.assertTrue(any("get httproute whoami-example-change -o json" in command for command in commands))

    def test_profile_checks_flux_kustomization_secret_reference_tlsroute_and_keeps_secret_data_unread(self) -> None:
        runner = FakeRunner()
        config = self._config()
        profile = verify.SmokeProfile(
            app="whoami",
            git_repository="branch-${branch_slug}",
            activation_template="template.yaml",
            namespace="whoami-${branch_slug}",
            kustomizations=("branch-whoami-${branch_slug}",),
            helm_releases=(),
            services=("whoami-${branch_slug}",),
            http_routes=(),
            tls_routes=("whoami-tls-${branch_slug}",),
            secret_refs=("whoami-secret-${branch_slug}",),
            pvcs=(),
            http_probes=(),
            route_urls=("https://whoami-${branch_slug}.dev.lab.petebeegle.com",),
        )

        verify.assert_smoke_profile(config, profile, runner=runner)

        commands = [" ".join(command) for command in runner.commands]
        kustomization_index = self._index_containing(
            commands,
            "wait kustomization.kustomize.toolkit.fluxcd.io/branch-whoami-example-change",
        )
        secret_index = self._index_containing(commands, "get secret whoami-secret-example-change")
        pods_index = self._index_containing(commands, "get pods -o json")
        tlsroute_index = self._index_containing(commands, "get tlsroute whoami-tls-example-change -o json")
        self.assertLess(kustomization_index, secret_index)
        self.assertLess(secret_index, pods_index)
        self.assertLess(pods_index, tlsroute_index)
        self.assertFalse(any("secret whoami-secret-example-change -o json" in command for command in commands))

    def test_jellyfin_profile_checks_helm_pvc_service_route_and_http_probe(self) -> None:
        runner = FakeRunner(pods_json=READY_JELLYFIN_PODS)
        config = self._config(app="jellyfin")

        verify.assert_smoke_profile(config, verify.load_smoke_profile("jellyfin"), runner=runner)

        commands = [" ".join(command) for command in runner.commands]
        self.assertTrue(any("get namespace jellyfin-example-change" in command for command in commands))
        self.assertTrue(any("wait helmrelease.helm.toolkit.fluxcd.io/jellyfin-example-change" in command for command in commands))
        self.assertTrue(any("get pvc jellyfin-config-example-change -o json" in command for command in commands))
        self.assertTrue(any("get service jellyfin-example-change" in command for command in commands))
        self.assertTrue(any("get httproute jellyfin-example-change -o json" in command for command in commands))
        self.assertTrue(any("run probe-example-change" in command and "curlimages/curl:8.16.0" in command for command in commands))

    def test_home_assistant_profile_checks_pvc_service_route_and_http_probe(self) -> None:
        runner = FakeRunner(pods_json=READY_HOME_ASSISTANT_PODS, pvc_json=READY_HOME_ASSISTANT_PVC)
        config = self._config(app="home-assistant")

        verify.assert_smoke_profile(config, verify.load_smoke_profile("home-assistant"), runner=runner)

        commands = [" ".join(command) for command in runner.commands]
        self.assertTrue(any("get namespace home-assistant-example-change" in command for command in commands))
        self.assertTrue(any("get pvc home-assistant-config-example-change -o json" in command for command in commands))
        self.assertTrue(any("get service home-assistant-example-change" in command for command in commands))
        self.assertTrue(any("get httproute home-assistant-example-change -o json" in command for command in commands))
        self.assertTrue(any("run probe-example-change" in command and "curlimages/curl:8.16.0" in command for command in commands))

    def test_pvc_assert_requires_bound_phase_and_expected_storage_class(self) -> None:
        verify.assert_pvc_bound(READY_PVC, pvc_name="jellyfin-config-example-change", storage_class="nfs-csi-storage")

        with self.assertRaisesRegex(verify.VerificationError, "not Bound"):
            verify.assert_pvc_bound(PENDING_PVC, pvc_name="jellyfin-config-example-change", storage_class="nfs-csi-storage")

        with self.assertRaisesRegex(verify.VerificationError, "storageClassName"):
            verify.assert_pvc_bound(READY_PVC, pvc_name="jellyfin-config-example-change", storage_class="other")

    def test_jellyfin_http_probe_command_targets_service_and_matches_web_shell(self) -> None:
        config = self._config(app="jellyfin")

        command = verify.build_http_probe_command(
            config,
            namespace=config.namespace,
            probe=verify.HttpProbe(
                service="jellyfin-${branch_slug}",
                port=8096,
                path="/",
                body_regex="Jellyfin|Please sign in|Wizard|Login",
            ),
            probe_index=0,
            total_probes=1,
        )

        self.assertIn("probe-example-change", command)
        self.assertIn("--image=curlimages/curl:8.16.0", command)
        self.assertIn("--overrides", command)
        overrides = json.loads(command[command.index("--overrides") + 1])
        self.assertEqual(overrides["spec"]["containers"][0]["command"], ["sh", "-ec"])
        script = overrides["spec"]["containers"][0]["args"][0]
        self.assertIn("http://jellyfin-example-change.jellyfin-example-change.svc.cluster.local:8096/", script)
        self.assertIn("curl -LfsS", script)
        self.assertIn("Jellyfin|Please sign in|Wizard|Login", script)
        self.assertIn("seq 1 60", script)

    def test_home_assistant_http_probe_command_targets_service_and_matches_web_shell(self) -> None:
        config = self._config(app="home-assistant")

        command = verify.build_http_probe_command(
            config,
            namespace=config.namespace,
            probe=verify.HttpProbe(
                service="home-assistant-${branch_slug}",
                port=80,
                path="/",
                body_regex="Home Assistant|Create my smart home|Sign in|Login",
            ),
            probe_index=0,
            total_probes=1,
        )

        self.assertIn("probe-example-change", command)
        self.assertIn("--image=curlimages/curl:8.16.0", command)
        self.assertIn("--overrides", command)
        overrides = json.loads(command[command.index("--overrides") + 1])
        self.assertEqual(overrides["spec"]["containers"][0]["command"], ["sh", "-ec"])
        script = overrides["spec"]["containers"][0]["args"][0]
        self.assertIn("http://home-assistant-example-change.home-assistant-example-change.svc.cluster.local:80/", script)
        self.assertIn("curl -LfsS", script)
        self.assertIn("Home Assistant|Create my smart home|Sign in|Login", script)
        self.assertIn("seq 1 60", script)

    def test_probe_pod_overrides_use_restricted_security_context(self) -> None:
        overrides = json.loads(verify.probe_pod_overrides("probe-example-change"))

        self.assertTrue(overrides["spec"]["securityContext"]["runAsNonRoot"])
        self.assertEqual(overrides["spec"]["securityContext"]["runAsUser"], 1000)
        self.assertEqual(overrides["spec"]["securityContext"]["seccompProfile"]["type"], "RuntimeDefault")
        self.assertEqual(overrides["spec"]["containers"][0]["image"], "curlimages/curl:8.16.0")
        self.assertFalse(overrides["spec"]["containers"][0]["securityContext"]["allowPrivilegeEscalation"])
        self.assertEqual(overrides["spec"]["containers"][0]["securityContext"]["capabilities"]["drop"], ["ALL"])
        self.assertEqual(overrides["spec"]["containers"][0]["securityContext"]["runAsUser"], 1000)

    def test_jellyfin_fresh_start_values_do_not_use_flaky_health_for_pod_readiness(self) -> None:
        production_values = (REPO_ROOT / "kubernetes/apps/jellyfin/values.yaml").read_text(encoding="utf-8")
        branch_values = (REPO_ROOT / "kubernetes/apps/jellyfin/branch/jellyfin.yaml").read_text(encoding="utf-8")

        for text in (production_values, branch_values):
            self.assertIn("startupProbe:", text)
            self.assertIn("tcpSocket:", text)
            self.assertIn("httpGet: null", text)
            self.assertIn("failureThreshold: 60", text)

    def test_cluster_base_reconciles_in_order_and_restores_main_on_success(self) -> None:
        runner = FakeRunner(cluster_pods_json=READY_PODS)

        verify.verify_cluster_base(self._config(include_cluster_base=True), runner=runner)

        commands = [" ".join(command) for command in runner.commands]
        branch_patch_indices = [
            index
            for index, command in enumerate(commands)
            if "patch gitrepository.source.toolkit.fluxcd.io/flux-system" in command and '"branch": "codex/example-change"' in command
        ]
        self.assertEqual(len(branch_patch_indices), 2)
        root_index = self._index_containing(commands, "reconcile kustomization flux-system")
        child_indices = [
            self._index_containing(commands, f"reconcile kustomization {name}")
            for name in verify.DEVELOPMENT_BASE_KUSTOMIZATIONS
        ]
        self.assertLess(branch_patch_indices[0], root_index)
        self.assertLess(root_index, branch_patch_indices[1])
        self.assertEqual(child_indices, sorted(child_indices))
        self.assertTrue(any("get pods --all-namespaces -o json" in command for command in commands))
        self.assertTrue(any("wait pod/whoami-example-change-7d9c4 --for=condition=Ready" in command for command in commands))
        self.assertTrue(any('"branch": "main"' in command for command in commands))
        self.assertGreater(commands[-2].find("reconcile kustomization flux-system"), -1)

    def test_cluster_base_restores_main_on_failure(self) -> None:
        runner = FakeRunner(fail_on="reconcile kustomization gateway")

        with self.assertRaisesRegex(verify.VerificationError, "command failed"):
            verify.verify_cluster_base(self._config(include_cluster_base=True), runner=runner)

        commands = [" ".join(command) for command in runner.commands]
        self.assertTrue(any('"branch": "main"' in command for command in commands))
        self.assertTrue(any("reconcile kustomization flux-system" in command for command in commands[-2:]))

    def test_cleanup_is_attempted_after_activation_failure_unless_keep_is_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "terraform" / "development").mkdir(parents=True)
            runner = FakeRunner(fail_on="wait pod/whoami-example-change-7d9c4")

            with self.assertRaises(verify.VerificationError):
                verify.run_acceptance(self._config(), runner=runner, repo_root=root, template_text=TEMPLATE)

        commands = [" ".join(command) for command in runner.commands]
        self.assertTrue(any("delete kustomization.kustomize.toolkit.fluxcd.io/branch-whoami-example-change" in command for command in commands))
        self.assertTrue(any("delete gitrepository.source.toolkit.fluxcd.io/branch-example-change" in command for command in commands))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "terraform" / "development").mkdir(parents=True)
            runner = FakeRunner(fail_on="wait pod/whoami-example-change-7d9c4")

            with self.assertRaises(verify.VerificationError):
                verify.run_acceptance(self._config(keep=True), runner=runner, repo_root=root, template_text=TEMPLATE)

        commands = [" ".join(command) for command in runner.commands]
        self.assertFalse(any("delete kustomization.kustomize.toolkit.fluxcd.io" in command for command in commands))

    def test_readme_and_runbook_examples_reference_real_cli_flags(self) -> None:
        parser = verify.build_parser()
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }
        text = (REPO_ROOT / "tools/development/README.md").read_text(encoding="utf-8")
        text += "\n"
        text += (REPO_ROOT / "docs/runbooks/development-cluster.md").read_text(encoding="utf-8")

        for flag in (
            "--app",
            "--branch",
            "--slug",
            "--push",
            "--terraform-apply",
            "--include-cluster-base",
            "--print-route-urls",
            "--kubeconfig",
            "--timeout",
            "--keep",
        ):
            self.assertIn(flag, text)
            self.assertIn(flag, option_strings)

    def _index_containing(self, commands: list[str], needle: str) -> int:
        for index, command in enumerate(commands):
            if needle in command:
                return index
        self.fail(f"missing command containing {needle!r}")

    def _config(
        self,
        *,
        app: str = "whoami",
        push: bool = False,
        terraform_apply: bool = False,
        include_cluster_base: bool = False,
        keep: bool = False,
    ) -> verify.AppConfig:
        return verify.AppConfig(
            app=app,
            branch="codex/example-change",
            slug="example-change",
            kubeconfig=Path("/tmp/kubeconfig"),
            timeout=verify.parse_duration("2m"),
            push=push,
            terraform_apply=terraform_apply,
            include_cluster_base=include_cluster_base,
            keep=keep,
        )


if __name__ == "__main__":
    unittest.main()
