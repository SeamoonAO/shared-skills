from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "auto-updater"
README = REPO_ROOT / "README.md"


def load_module():
    module_path = SKILL_DIR / "scripts" / "run.py"
    spec = spec_from_file_location("shared_skills_auto_updater", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AutoUpdaterLayoutTests(unittest.TestCase):
    def test_skill_directory_and_files_exist(self):
        expected = [
            SKILL_DIR / "SKILL.md",
            SKILL_DIR / "agents" / "openai.yaml",
            SKILL_DIR / "sources.json",
            SKILL_DIR / "scripts" / "run.py",
        ]
        for path in expected:
            self.assertTrue(path.exists(), f"missing expected path: {path}")

    def test_readme_mentions_auto_updater(self):
        text = README.read_text(encoding="utf-8")
        self.assertIn("`auto-updater`", text)


class AutoUpdaterBehaviorTests(unittest.TestCase):
    def test_discover_installed_skills_ignores_regular_dirs_and_system(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex = root / ".codex" / "skills"
            codex.mkdir(parents=True)
            system_dir = codex / ".system"
            system_dir.mkdir()
            regular_dir = codex / "plain-dir"
            regular_dir.mkdir()

            target = root / "skill-tools" / "repo" / "skills" / "demo-skill"
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("---\nname: demo-skill\n---\n", encoding="utf-8")
            (codex / "demo-skill").symlink_to(target, target_is_directory=True)

            discovered = module.discover_installed_skills([codex])

            self.assertEqual(set(discovered.keys()), {"demo-skill"})
            self.assertEqual(discovered["demo-skill"]["resolved"], target.resolve())

    def test_build_link_repairs_retargets_to_canonical_skill_dir(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_root = root / "skill-tools" / "baoyu-skills"
            canonical = source_root / "skills" / "baoyu-image-gen"
            canonical.mkdir(parents=True)
            (canonical / "SKILL.md").write_text("---\nname: baoyu-image-gen\n---\n", encoding="utf-8")

            old_project = root / "code" / "baoyu-skills"
            (old_project / "skills").mkdir(parents=True)
            indirect = old_project / "skills" / "baoyu-image-gen"
            indirect.symlink_to(canonical, target_is_directory=True)

            codex = root / ".codex" / "skills"
            codex.mkdir(parents=True)
            link_path = codex / "baoyu-image-gen"
            link_path.symlink_to(indirect, target_is_directory=True)

            installed = module.discover_installed_skills([codex])
            source_defs = [
                {
                    "name": "baoyu-skills",
                    "strategy": "git",
                    "root": str(source_root),
                }
            ]
            skill_index = module.scan_source_skill_dirs(source_defs)
            repairs = module.build_link_repairs(installed, skill_index)

            self.assertEqual(repairs, [(link_path, canonical.resolve())])

    def test_snapshot_metadata_marks_modified_directory_dirty(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_root = root / "ljg-skills"
            skill_dir = repo_root / "skills" / "ljg-card"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("card", encoding="utf-8")

            metadata_path = repo_root / ".auto-updater-source.json"
            metadata = {
                "strategy": "github_archive",
                "repo": "lijigang/ljg-skills",
                "ref": "master",
                "tree_hash": module.compute_tree_hash(repo_root),
            }
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

            self.assertFalse(module.snapshot_source_is_dirty(repo_root, metadata_path))

            (skill_dir / "SKILL.md").write_text("card changed", encoding="utf-8")

            self.assertTrue(module.snapshot_source_is_dirty(repo_root, metadata_path))

    def test_build_link_repairs_handles_codex_and_cursor_entries_for_same_skill(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_root = root / "skill-tools" / "superpowers"
            canonical = source_root / "skills" / "using-superpowers"
            canonical.mkdir(parents=True)
            (canonical / "SKILL.md").write_text("---\nname: using-superpowers\n---\n", encoding="utf-8")

            project_link = root / "code" / "superpowers"
            (project_link / "skills").mkdir(parents=True)
            indirect = project_link / "skills" / "using-superpowers"
            indirect.symlink_to(canonical, target_is_directory=True)

            codex = root / ".codex" / "skills"
            cursor = root / ".cursor" / "skills"
            codex.mkdir(parents=True)
            cursor.mkdir(parents=True)
            codex_link = codex / "using-superpowers"
            cursor_link = cursor / "using-superpowers"
            codex_link.symlink_to(indirect, target_is_directory=True)
            cursor_link.symlink_to(indirect, target_is_directory=True)

            installed = module.discover_installed_skills([codex, cursor])
            source_defs = [
                {
                    "name": "superpowers",
                    "strategy": "git",
                    "root": str(source_root),
                }
            ]
            skill_index = module.scan_source_skill_dirs(source_defs)
            repairs = module.build_link_repairs(installed, skill_index)

            self.assertEqual(
                repairs,
                [
                    (codex_link, canonical.resolve()),
                    (cursor_link, canonical.resolve()),
                ],
            )


if __name__ == "__main__":
    unittest.main()
