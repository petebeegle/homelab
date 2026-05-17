from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_SOURCE = REPO_ROOT / ".codex" / "scripts" / "create_implementation_pr.sh"
ACTIVE_VALIDATOR = REPO_ROOT / "tools" / "codex-harness" / "validate_active_implementation.py"
PLAN_VALIDATOR = REPO_ROOT / "tools" / "codex-harness" / "validate_implementation_plan.py"
ATTESTATION_VALIDATOR = REPO_ROOT / "tools" / "codex-harness" / "validate_workflow_attestations.py"
VALIDATION_COMMON = REPO_ROOT / "tools" / "codex-harness" / "validation_common.py"
TOOLS_LIB_SOURCE = REPO_ROOT / "tools" / "lib"


class CreateImplementationPrTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_parent = tempfile.TemporaryDirectory(prefix="pr-root-")
        self.sibling_root = Path(self.temp_parent.name) / "homelab-ideas"
        self.sibling_root.mkdir()
        self.tmpdir = tempfile.TemporaryDirectory(dir=self.sibling_root, prefix="pr-test-")
        self.root = Path(self.tmpdir.name)
        self.implementation = self.root.name
        self.branch = f"codex/{self.implementation}"
        _init_repo(self.root)
        _install_harness_files(self.root, self.sibling_root)
        subprocess.run(["git", "switch", "-c", self.branch], cwd=self.root, check=True, stdout=subprocess.DEVNULL)
        _write_marker(self.root, self.implementation)
        _write_owner_attestation(self.root, self.implementation)
        self.head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        self.temp_parent.cleanup()

    def test_blocks_without_verifier_attestation(self) -> None:
        _write_verifier_approval(self.root, self.head)

        result = _run_script(self.root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("verifier attestation is missing", result.stderr)

    def test_blocks_with_wrong_head_verifier_attestation(self) -> None:
        _write_verifier_approval(self.root, self.head)
        _write_verifier_attestation(self.root, self.implementation, "0" * 40)

        result = _run_script(self.root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("verifier attestation validation failed", result.stderr)


def _init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "codex@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Codex"], cwd=root, check=True)
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/petebeegle/homelab.git"], cwd=root, check=True)
    (root / "README.md").write_text("# test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "test: initialize"], cwd=root, check=True, stdout=subprocess.DEVNULL)


def _install_harness_files(root: Path, sibling_root: Path) -> None:
    script_path = root / ".codex" / "scripts" / "create_implementation_pr.sh"
    tool_dir = root / "tools" / "codex-harness"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    tool_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SCRIPT_SOURCE, script_path)
    shutil.copy2(ACTIVE_VALIDATOR, tool_dir / "validate_active_implementation.py")
    shutil.copy2(PLAN_VALIDATOR, tool_dir / "validate_implementation_plan.py")
    shutil.copy2(ATTESTATION_VALIDATOR, tool_dir / "validate_workflow_attestations.py")
    shutil.copy2(VALIDATION_COMMON, tool_dir / "validation_common.py")
    shutil.copytree(TOOLS_LIB_SOURCE, root / "tools" / "lib")
    _patch_sibling_root(
        sibling_root,
        script_path,
        tool_dir / "validate_active_implementation.py",
        tool_dir / "validate_implementation_plan.py",
    )
    script_path.chmod(0o755)


def _patch_sibling_root(sibling_root: Path, *paths: Path) -> None:
    for path in paths:
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "/workspaces/homelab-ideas",
                str(sibling_root),
            ),
            encoding="utf-8",
        )


def _write_marker(root: Path, implementation: str) -> None:
    tmp = root / ".codex" / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "active-implementation").write_text(
        "\n".join(
            [
                f"implementation={implementation}",
                f"branch=codex/{implementation}",
                "base=origin/main",
                "role=implementation",
                f"clone_path={root}",
                "owner_role=implementation-agent",
                "owner_agent=implementation-agent-deterministic-role-enforcement",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_owner_attestation(root: Path, implementation: str) -> None:
    tmp = root / ".codex" / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    _write_delegation_token(
        root,
        token_name="implementation-token-deterministic-role-enforcement",
        implementation=implementation,
        role="implementation-agent",
        agent_id="implementation-agent-deterministic-role-enforcement",
    )
    (tmp / "implementation-owner-attestation.yaml").write_text(
        "\n".join(
            [
                f"implementation: {implementation}",
                f"branch: codex/{implementation}",
                "base: origin/main",
                "role: implementation-agent",
                "agent_id: implementation-agent-deterministic-role-enforcement",
                f"clone_path: {root}",
                "created_at: 2026-05-11T00:00:00Z",
                "delegation_token: implementation-token-deterministic-role-enforcement",
                "delegation_token_path: .codex/tmp/delegation-tokens/implementation-agent-deterministic-role-enforcement.token",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_verifier_approval(root: Path, head: str) -> None:
    tmp = root / ".codex" / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "verifier-approved").write_text(head + "\n", encoding="utf-8")


def _write_verifier_attestation(root: Path, implementation: str, head: str) -> None:
    tmp = root / ".codex" / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    _write_delegation_token(
        root,
        token_name="verifier-token-deterministic-role-enforcement",
        implementation=implementation,
        role="verifier-agent",
        agent_id="verifier-agent-deterministic-role-enforcement",
    )
    (tmp / "verifier-attestation.yaml").write_text(
        "\n".join(
            [
                f"implementation: {implementation}",
                f"branch: codex/{implementation}",
                "base: origin/main",
                "role: verifier-agent",
                "agent_id: verifier-agent-deterministic-role-enforcement",
                f"clone_path: {root}",
                "created_at: 2026-05-11T00:00:00Z",
                f"approved_head: {head}",
                "delegation_token: verifier-token-deterministic-role-enforcement",
                "delegation_token_path: .codex/tmp/delegation-tokens/verifier-agent-deterministic-role-enforcement.token",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_delegation_token(
    root: Path,
    *,
    token_name: str,
    implementation: str,
    role: str,
    agent_id: str,
) -> None:
    token_path = root / ".codex" / "tmp" / "delegation-tokens" / f"{agent_id}.token"
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(
        "\n".join(
            [
                f"delegation_token: {token_name}",
                f"implementation: {implementation}",
                f"role: {role}",
                f"agent_id: {agent_id}",
                "created_at: 2026-05-11T00:00:00Z",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _run_script(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", ".codex/scripts/create_implementation_pr.sh"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


if __name__ == "__main__":
    unittest.main()
