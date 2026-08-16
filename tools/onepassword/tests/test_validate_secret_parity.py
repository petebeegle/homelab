from __future__ import annotations

import base64
import contextlib
import importlib.util
import io
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "tools/onepassword/validate_secret_parity.py"


class ValidateSecretParityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("validate_secret_parity", MODULE_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError("could not load parity validator")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    @staticmethod
    def secret(values: dict[str, bytes], secret_type: str = "Opaque") -> dict:
        return {
            "type": secret_type,
            "data": {
                key: base64.b64encode(value).decode("ascii")
                for key, value in values.items()
            },
        }

    def test_exact_type_keys_and_bytes_pass(self) -> None:
        legacy = self.secret({"password": b"same\nbytes"})
        generated = self.secret({"password": b"same\nbytes"})
        self.module.compare_pair(legacy, generated, {"password"}, "Opaque")

    def test_byte_mismatch_names_neither_key_nor_values(self) -> None:
        legacy_value = "legacy-secret-sentinel"
        generated_value = "generated-secret-sentinel"
        with self.assertRaisesRegex(ValueError, "byte mismatch") as raised:
            self.module.compare_pair(
                self.secret({"sensitive-key-name": legacy_value.encode()}),
                self.secret({"sensitive-key-name": generated_value.encode()}),
                {"sensitive-key-name"},
                "Opaque",
            )
        message = str(raised.exception)
        self.assertNotIn("sensitive-key-name", message)
        self.assertNotIn(legacy_value, message)
        self.assertNotIn(generated_value, message)

    def test_key_set_mismatch_reports_count_only(self) -> None:
        with self.assertRaisesRegex(ValueError, "key set mismatch") as raised:
            self.module.compare_pair(
                self.secret({"legacy-key": b"value"}),
                self.secret({"generated-key": b"value"}),
                {"legacy-key"},
                "Opaque",
            )
        self.assertNotIn("legacy-key", str(raised.exception))
        self.assertNotIn("generated-key", str(raised.exception))

    def test_namespace_overrides_are_strict_and_repeatable(self) -> None:
        self.assertEqual(
            {"immich": "immich-feature", "cert-manager": "cert-manager"},
            self.module.parse_namespace_overrides(
                ["immich=immich-feature", "cert-manager=cert-manager"]
            ),
        )
        for invalid in ["immich", "=target", "source=", "UPPER=target"]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.module.parse_namespace_overrides([invalid])

    def test_live_validation_uses_target_namespace_without_printing_values(self) -> None:
        inventory = {
            "items": [
                {
                    "namespace": "immich",
                    "legacy_name": "legacy",
                    "generated_name": "generated",
                    "keys": ["password"],
                    "type": "Opaque",
                }
            ]
        }
        secret = self.secret({"password": b"secret-sentinel"})
        ready = {"status": {"conditions": [{"type": "Ready", "status": "True"}]}}
        output = io.StringIO()
        with mock.patch.object(
            self.module, "run_json", side_effect=[ready, secret, secret]
        ) as run_json, contextlib.redirect_stdout(output):
            self.module.validate_live(
                Path("/tmp/dev.config"), inventory, {"immich": "immich-feature"}
            )
        self.assertTrue(
            all("immich-feature" in call.args[0] for call in run_json.call_args_list)
        )
        self.assertNotIn("secret-sentinel", output.getvalue())
        self.assertIn("Secret parity passed: 1/1", output.getvalue())


if __name__ == "__main__":
    unittest.main()
