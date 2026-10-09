"""Offline release projection tests; no real remote, workspace or credentials."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("product_publication", SCRIPTS / "product_publication.py")
pub = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pub)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="publication-test-")
        self.addCleanup(self.temp.cleanup)
        self.temp_root = Path(self.temp.name).resolve()
        self.root = self.temp_root / "repo"
        self.root.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        for name in pub.PRODUCT_FILES:
            (self.root / name).write_text("fixture\n")
        self.file(".systems/tool.sh", "old\n").chmod(0o755)
        self.file(".systems/obsolete.md", "old\n")
        self.save("main fixture")
        self.base = self.git("rev-parse", "HEAD").strip()
        self.git("switch", "-q", "-c", "dev")
        self.file(".systems/tool.sh", "new\n")
        self.file(".systems/new.md", "new\n")
        (self.root / ".systems/obsolete.md").unlink()
        self.file("ai-workflow-workspace/quality/report.md", "private fixture\n")
        self.save("development fixture")
        self.source = self.git("rev-parse", "HEAD").strip()
        self.destination = self.temp_root / "release"

    def git(self, *args, cwd=None):
        return pub.git(cwd or self.root, *args).decode()

    def file(self, name, body):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
        return path

    def save(self, title):
        self.git("add", "-A")
        self.git("commit", "-qm", title)

    def prepare(self):
        report, expected = pub.plan(self.root, "dev", "main")
        result = pub.prepare(self.root, self.destination, "codex/publish/fixture", report, expected)
        return report, expected, result

    def test_read_only_plan_classifies_complete_projection(self):
        before = self.git("status", "--porcelain"), self.git("show-ref")
        report, expected = pub.plan(self.root, "dev", "main")
        self.assertEqual(report["excluded_runtime_file_count"], 1)
        self.assertEqual({x["change"] for x in report["changes"]}, {"A", "M", "D"})
        self.assertEqual(before, (self.git("status", "--porcelain"), self.git("show-ref")))
        self.assertNotIn("ai-workflow-workspace/quality/report.md", expected)

    def test_prepared_snapshot_preserves_source_and_modes(self):
        before = self.git("status", "--porcelain"), self.git("rev-parse", "HEAD")
        report, expected, result = self.prepare()
        self.assertEqual(before, (self.git("status", "--porcelain"), self.git("rev-parse", "HEAD")))
        self.assertFalse((self.destination / "ai-workflow-workspace").exists())
        self.assertFalse((self.destination / ".systems/obsolete.md").exists())
        self.assertTrue((self.destination / ".systems/tool.sh").stat().st_mode & 0o111)
        self.assertFalse(result["commit_created"] or result["push_performed"])
        self.assertEqual(report["target_commit"], self.git("rev-parse", "HEAD", cwd=self.destination).strip())
        pub.verify_candidate(self.root, self.destination, report, expected)

    def test_commit_has_only_main_parent_and_no_runtime_ancestry(self):
        report, expected, _ = self.prepare()
        self.git("commit", "-qm", "product publication", cwd=self.destination)
        pub.verify_candidate(self.root, self.destination, report, expected)
        self.assertEqual(self.git("show", "-s", "--format=%P", "HEAD", cwd=self.destination).strip(), self.base)
        proc = subprocess.run(["git", "-C", str(self.destination), "merge-base", "--is-ancestor",
                               self.source, "HEAD"], capture_output=True)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(pub.product(pub.tree(self.destination, "HEAD")), expected)

    def test_unknown_source_paths_stop_before_worktree(self):
        self.file("unexpected/data.md", "fixture\n")
        self.save("unknown path")
        with self.assertRaisesRegex(ValueError, "Unknown tracked"):
            pub.plan(self.root, "dev", "main")
        self.assertFalse(self.destination.exists())

    def test_local_config_and_agent_contract_are_not_publishable(self):
        for name in ("AGENTS.md", "ai-system.local.json", ".env"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    pub.path_kind(name)

    def test_forbidden_nested_paths_and_traversal(self):
        for name in (".systems/.env", ".systems/private.key", ".systems/node_modules/a",
                     ".systems/../outside", "/.systems/a", ".systems//a", ".systems/./a",
                     ".systems/a\nb", ".systems/a\\b"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    pub.path_kind(name)

    def test_linked_product_is_rejected(self):
        (self.root / ".systems/link").symlink_to("tool.sh")
        self.save("linked fixture")
        with self.assertRaisesRegex(ValueError, "Linked"):
            pub.plan(self.root, "dev", "main")

    def test_main_advance_requires_development_sync(self):
        self.git("switch", "-q", "main")
        self.file(".systems/main-only.md", "new main\n")
        self.save("advanced main")
        with self.assertRaises(ValueError):
            pub.plan(self.root, "dev", "main")

    def test_target_runtime_requires_explicit_reconciliation(self):
        with self.assertRaisesRegex(ValueError, "Target already tracks runtime"):
            pub.plan(self.root, "dev", "dev")

    def test_empty_projection_creates_nothing(self):
        report, expected = pub.plan(self.root, "main", "main")
        with self.assertRaisesRegex(ValueError, "No product changes"):
            pub.prepare(self.root, self.destination, "codex/publish/empty", report, expected)
        self.assertFalse(self.destination.exists())

    def test_existing_or_linked_destinations_are_preserved(self):
        self.destination.mkdir()
        (self.destination / "keep").write_text("keep\n")
        report, expected = pub.plan(self.root, "dev", "main")
        with self.assertRaisesRegex(ValueError, "must not exist"):
            pub.prepare(self.root, self.destination, "codex/publish/fixture", report, expected)
        self.assertEqual((self.destination / "keep").read_text(), "keep\n")
        link = self.temp_root / "link"
        link.symlink_to(self.destination, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Linked"):
            pub.destination(self.root, link / "release")

    def test_branch_collision_and_bad_branch_do_not_create_destination(self):
        report, expected = pub.plan(self.root, "dev", "main")
        for branch in ("main", "codex/publish/../bad"):
            with self.assertRaises(ValueError):
                pub.prepare(self.root, self.destination, branch, report, expected)
        self.git("branch", "codex/publish/existing")
        with self.assertRaisesRegex(ValueError, "already exists"):
            pub.prepare(self.root, self.destination, "codex/publish/existing", report, expected)
        self.assertFalse(self.destination.exists())

    def test_dirty_live_files_cannot_be_verified_even_with_assume_unchanged(self):
        report, expected, _ = self.prepare()
        self.git("update-index", "--assume-unchanged", ".systems/new.md", cwd=self.destination)
        (self.destination / ".systems/new.md").write_text("tampered\n")
        with self.assertRaisesRegex(ValueError, "live product differs"):
            pub.verify_candidate(self.root, self.destination, report, expected)

    def test_executable_mode_drift_is_rejected_with_filemode_disabled(self):
        report, expected, _ = self.prepare()
        self.git("config", "core.filemode", "false")
        (self.destination / ".systems/tool.sh").chmod(0o644)
        with self.assertRaisesRegex(ValueError, "live product differs"):
            pub.verify_candidate(self.root, self.destination, report, expected)

    def test_linked_live_file_and_untracked_files_are_rejected(self):
        report, expected, _ = self.prepare()
        (self.destination / "untracked.md").write_text("fixture\n")
        with self.assertRaisesRegex(ValueError, "untracked"):
            pub.verify_candidate(self.root, self.destination, report, expected)
        (self.destination / "untracked.md").unlink()
        path = self.destination / ".systems/new.md"
        path.unlink()
        path.symlink_to("tool.sh")
        with self.assertRaisesRegex(ValueError, "linked"):
            pub.verify_candidate(self.root, self.destination, report, expected)

    def test_uncommitted_source_changes_do_not_enter_projection(self):
        self.file(".systems/new.md", "uncommitted\n")
        _, _, _ = self.prepare()
        self.assertEqual((self.destination / ".systems/new.md").read_text(), "new\n")
        self.assertEqual((self.root / ".systems/new.md").read_text(), "uncommitted\n")

    def test_cli_requires_approval_and_keeps_json_clean(self):
        args = ["python3", "-B", str(SCRIPTS / "prepare-product-release"), "--repo", str(self.root),
                "--source", "dev", "--target", "main"]
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["source_commit"], self.source)
        result = subprocess.run(args + ["--prepare", str(self.destination), "--branch", "codex/publish/cli"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("owner approval", result.stderr)
        self.assertFalse(self.destination.exists())

    def test_invalid_reference_and_foreign_candidate_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid"):
            pub.plan(self.root, "--all", "main")
        report, expected = pub.plan(self.root, "dev", "main")
        other = self.temp_root / "other"
        subprocess.run(["git", "clone", "-q", str(self.root), str(other)], check=True)
        with self.assertRaisesRegex(ValueError, "another repository"):
            pub.verify_candidate(self.root, other, report, expected)

    def test_committed_runtime_cannot_be_hidden_by_staged_deletion(self):
        report, expected, _ = self.prepare()
        self.git("add", "-A", cwd=self.destination)
        runtime = self.destination / "ai-workflow-workspace/report.md"
        runtime.parent.mkdir()
        runtime.write_text("fixture\n")
        self.git("add", "-f", str(runtime), cwd=self.destination)
        self.git("commit", "-qm", "invalid runtime publication", cwd=self.destination)
        self.git("rm", str(runtime), cwd=self.destination)
        with self.assertRaisesRegex(ValueError, "product-only commit"):
            pub.verify_candidate(self.root, self.destination, report, expected)

    def test_partial_staged_projection_is_rejected(self):
        report, expected, _ = self.prepare()
        self.git("restore", "--staged", "--source=HEAD", ".systems/new.md", cwd=self.destination)
        with self.assertRaisesRegex(ValueError, "index differs"):
            pub.verify_candidate(self.root, self.destination, report, expected)

    def test_required_root_file_missing_is_rejected(self):
        (self.root / "README.md").unlink()
        self.save("missing required root")
        with self.assertRaisesRegex(ValueError, "required root"):
            pub.plan(self.root, "dev", "main")

    def test_inherited_git_selectors_do_not_redirect_source_or_candidate_index(self):
        index = self.root / ".git/index"
        before = index.read_bytes()
        external_index = self.temp_root / "foreign-index"
        with patch.dict(os.environ, {"GIT_DIR": str(self.temp_root / "missing.git"),
                                     "GIT_WORK_TREE": str(self.temp_root),
                                     "GIT_INDEX_FILE": str(external_index)}):
            report, expected, _ = self.prepare()
            pub.verify_candidate(self.root, self.destination, report, expected)
        self.assertEqual(before, index.read_bytes())
        self.assertFalse(external_index.exists())


if __name__ == "__main__":
    unittest.main()
