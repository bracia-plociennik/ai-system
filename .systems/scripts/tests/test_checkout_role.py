"""Synthetic bootstrap regressions; never touch real configuration or contracts."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("checkout_role", SCRIPTS / "checkout_role.py")
role = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(role)
MANAGEMENT = "# AGENTS.md\nThis is the generated local root agent contract for AI System management.\n"
WORKFLOW = "# AGENTS.md\nThis file is the root AI Workflow entrypoint for this target repository.\n"


class CheckoutRoleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="checkout-role-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "arbitrary-repo-name"
        self.root.mkdir()
        self.template = self.root / role.TEMPLATE
        self.template.parent.mkdir(parents=True)
        self.template.write_text(MANAGEMENT)

    def config(self, value):
        (self.root / role.CONFIG).write_text(json.dumps(value))

    def assert_no_config(self):
        self.assertFalse((self.root / role.CONFIG).exists())

    def test_first_bootstrap_requires_explicit_role(self):
        with self.assertRaisesRegex(ValueError, "Unconfigured"):
            role.bootstrap(self.root)
        self.assert_no_config()
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_read_only_unconfigured_status(self):
        self.assertEqual(role.status(self.root)["role"], "unconfigured")
        self.assertFalse(role.status(self.root)["ready"])
        self.assert_no_config()

    def test_management_creates_config_and_agents(self):
        result = role.bootstrap(self.root, "management")
        self.assertTrue(result["ready"])
        self.assertEqual((self.root / "AGENTS.md").read_text(), MANAGEMENT)
        self.assertEqual(role.configuration(self.root), {"schema_version": 1, "role": "management"})
        self.assertEqual((self.root / role.CONFIG).stat().st_mode & 0o777, 0o600)

    def test_repeat_bootstrap_preserves_files_and_mtime(self):
        role.bootstrap(self.root, "management")
        paths = [self.root / role.CONFIG, self.root / "AGENTS.md"]
        before = [(p.read_bytes(), p.stat().st_mtime_ns) for p in paths]
        self.assertEqual(role.bootstrap(self.root)["agents_action"], "preserved")
        self.assertEqual(before, [(p.read_bytes(), p.stat().st_mtime_ns) for p in paths])

    def test_refresh_requires_explicit_flag(self):
        role.bootstrap(self.root, "management")
        self.template.write_text(MANAGEMENT + "New clause.\n")
        role.bootstrap(self.root)
        self.assertEqual((self.root / "AGENTS.md").read_text(), MANAGEMENT)
        self.assertEqual(role.bootstrap(self.root, refresh=True)["agents_action"], "refreshed")
        self.assertEqual((self.root / "AGENTS.md").read_bytes(), self.template.read_bytes())

    def test_management_preserves_legacy_generated_agents(self):
        old = MANAGEMENT.replace("AI System management", "the `ai-system` branch")
        (self.root / "AGENTS.md").write_text(old)
        role.bootstrap(self.root, "management")
        self.assertEqual((self.root / "AGENTS.md").read_text(), old)

    def test_development_preserves_workflow_shim(self):
        path = self.root / "AGENTS.md"
        path.write_bytes(WORKFLOW.encode() + b"\r\nCustom local clause.\r\n")
        before = (path.read_bytes(), path.stat().st_mtime_ns)
        self.assertTrue(role.bootstrap(self.root, "development")["ready"])
        self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)
        self.assertFalse((self.root / "ai-workflow").exists())

    def test_development_preserves_custom_contract(self):
        (self.root / "AGENTS.md").write_text("# Project rules\nUse the local development process.\n")
        self.assertTrue(role.bootstrap(self.root, "development")["ready"])

    def test_development_missing_contract_is_not_ready(self):
        result = role.bootstrap(self.root, "development")
        self.assertFalse(result["ready"])
        self.assertEqual(result["agents"], "missing")
        self.assertFalse((self.root / "AGENTS.md").exists())
        self.assertFalse((self.root / "ai-system-workspace").exists())

    def test_development_rejects_refresh_before_writes(self):
        with self.assertRaisesRegex(ValueError, "forbidden"):
            role.bootstrap(self.root, "development", refresh=True)
        self.assert_no_config()

    def test_development_rejects_management_contract(self):
        (self.root / "AGENTS.md").write_text(MANAGEMENT)
        with self.assertRaisesRegex(ValueError, "AGENTS role conflict"):
            role.bootstrap(self.root, "development")
        self.assert_no_config()

    def test_management_rejects_workflow_shim_even_with_refresh(self):
        path = self.root / "AGENTS.md"
        path.write_text(WORKFLOW)
        for refresh in (False, True):
            with self.assertRaisesRegex(ValueError, "AGENTS role conflict"):
                role.bootstrap(self.root, "management", refresh=refresh)
            self.assert_no_config()
            self.assertEqual(path.read_text(), WORKFLOW)

    def test_management_rejects_unrecognized_contract(self):
        (self.root / "AGENTS.md").write_text("# Unknown owner contract\n")
        with self.assertRaises(ValueError):
            role.bootstrap(self.root, "management", refresh=True)
        self.assert_no_config()

    def test_conflicting_role_does_not_change_files(self):
        role.bootstrap(self.root, "management")
        before = (self.root / role.CONFIG).read_bytes()
        with self.assertRaisesRegex(ValueError, "role conflict"):
            role.bootstrap(self.root, "development")
        self.assertEqual((self.root / role.CONFIG).read_bytes(), before)

    def test_configured_role_contract_conflict_is_reported(self):
        self.config({"schema_version": 1, "role": "development"})
        (self.root / "AGENTS.md").write_text(MANAGEMENT)
        self.assertTrue(role.status(self.root)["conflict"])
        self.assertFalse(role.status(self.root)["ready"])
        with self.assertRaises(ValueError):
            role.bootstrap(self.root)

    def test_invalid_config_records_fail(self):
        cases = [[], {}, {"role": "management"}, {"schema_version": True, "role": "management"},
                 {"schema_version": 2, "role": "management"}, {"schema_version": 1, "role": "MANAGEMENT"},
                 {"schema_version": 1, "role": ["development"]},
                 {"schema_version": 1, "role": "management", "extra": "ignored?"}]
        for value in cases:
            with self.subTest(value=value):
                self.config(value)
                with self.assertRaises(ValueError):
                    role.bootstrap(self.root, "management")
                self.assertFalse((self.root / "AGENTS.md").exists())

    def test_duplicate_config_key_fails(self):
        (self.root / role.CONFIG).write_text('{"schema_version":1,"role":"management","role":"development"}')
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            role.status(self.root)

    def test_malformed_config_is_not_repaired(self):
        path = self.root / role.CONFIG
        path.write_text("not json")
        with self.assertRaises(ValueError):
            role.bootstrap(self.root, "management")
        self.assertEqual(path.read_text(), "not json")

    def test_missing_template_no_partial_files(self):
        self.template.unlink()
        with self.assertRaisesRegex(ValueError, "template"):
            role.bootstrap(self.root, "management")
        self.assert_no_config()
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_development_does_not_require_management_template(self):
        self.template.unlink()
        self.assertFalse(role.bootstrap(self.root, "development")["ready"])

    def test_linked_config_and_agents_rejected(self):
        target = Path(self.temp.name) / "outside"
        target.write_text(WORKFLOW)
        for name in (role.CONFIG, "AGENTS.md"):
            with self.subTest(name=name):
                link = self.root / name
                link.symlink_to(target)
                with self.assertRaisesRegex(ValueError, "Linked"):
                    role.bootstrap(self.root, "development")
                link.unlink()
        self.assertEqual(target.read_text(), WORKFLOW)
        self.assert_no_config()

    def test_linked_template_rejected_before_write(self):
        target = Path(self.temp.name) / "template-source"
        target.write_text(MANAGEMENT)
        self.template.unlink()
        self.template.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "Linked"):
            role.bootstrap(self.root, "management")
        self.assert_no_config()

    def test_linked_template_directory_rejected(self):
        directory = self.template.parent
        outside = Path(self.temp.name) / "root-templates"
        directory.rename(outside)
        directory.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Linked"):
            role.bootstrap(self.root, "management")
        self.assert_no_config()

    def test_dangling_linked_output_rejected(self):
        (self.root / "AGENTS.md").symlink_to(Path(self.temp.name) / "missing")
        with self.assertRaisesRegex(ValueError, "Linked"):
            role.bootstrap(self.root, "management")
        self.assert_no_config()

    def test_directory_instead_of_configuration_rejected(self):
        (self.root / role.CONFIG).mkdir()
        with self.assertRaisesRegex(ValueError, "regular file"):
            role.bootstrap(self.root, "management")
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_cli_config_conflict_returns_nonzero(self):
        scripts = self.root / ".systems/scripts"
        scripts.mkdir()
        for name in ("init-ai-system", "checkout_role.py"):
            shutil.copy2(SCRIPTS / name, scripts / name)
        self.config({"schema_version": 1, "role": "development"})
        (self.root / "AGENTS.md").write_text(MANAGEMENT)
        result = subprocess.run([str(scripts / "init-ai-system"), "--status"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(json.loads(result.stdout)["conflict"])

    def test_empty_contract_rejected(self):
        (self.root / "AGENTS.md").write_text("\n")
        with self.assertRaises(ValueError):
            role.bootstrap(self.root, "development")
        self.assert_no_config()

    def test_no_inference_from_git_branch_or_basename(self):
        subprocess.run(["git", "init", "-q", "--initial-branch=development", str(self.root)], check=True)
        self.assertEqual(role.status(self.root)["role"], "unconfigured")
        role.bootstrap(self.root, "management")
        self.assertEqual(role.status(self.root)["role"], "management")

    def test_cli_read_only_and_invalid_options(self):
        scripts = self.root / ".systems/scripts"
        scripts.mkdir()
        for name in ("init-ai-system", "checkout_role.py"):
            shutil.copy2(SCRIPTS / name, scripts / name)
        command = [str(scripts / "init-ai-system")]
        before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*"))
        result = subprocess.run(command + ["--status"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["role"], "unconfigured")
        self.assertEqual(before, sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*")))
        for options in ([], ["--role", "invalid"], ["--status", "--role", "management"]):
            self.assertNotEqual(subprocess.run(command + options, capture_output=True).returncode, 0)
            self.assert_no_config()
        result = subprocess.run(command + ["--role", "management"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["ready"])


if __name__ == "__main__":
    unittest.main()
