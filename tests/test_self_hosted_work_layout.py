from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
NEW_SKILL = REPO_ROOT / "self-hosted-work"
OLD_SKILL = REPO_ROOT / "self-hosted-coding"
README = REPO_ROOT / "README.md"


class SelfHostedWorkLayoutTests(unittest.TestCase):
    def test_new_skill_directory_and_files_exist(self):
        expected = [
            NEW_SKILL / "SKILL.md",
            NEW_SKILL / "agents" / "openai.yaml",
            NEW_SKILL / "references" / "coding.md",
            NEW_SKILL / "references" / "writing.md",
            NEW_SKILL / "references" / "research.md",
            NEW_SKILL / "references" / "general.md",
            NEW_SKILL / "references" / "pressure-tests.md",
            NEW_SKILL / "references" / "upgrade-candidates.md",
            NEW_SKILL / "references" / "backlog.md",
            NEW_SKILL / "scripts" / "append_review_log.py",
            NEW_SKILL / "scripts" / "timed_soft_pause.py",
        ]
        for path in expected:
            self.assertTrue(path.exists(), f"missing expected path: {path}")

    def test_old_skill_directory_is_removed(self):
        self.assertFalse(OLD_SKILL.exists(), "self-hosted-coding should be removed after migration")

    def test_readme_points_to_new_skill_only(self):
        text = README.read_text(encoding="utf-8")
        self.assertIn("`self-hosted-work`", text)
        self.assertNotIn("`self-hosted-coding`", text)

    def test_main_skill_routes_and_references_branch_files(self):
        text = (NEW_SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Task-Type Routing", text)
        self.assertIn("coding.md", text)
        self.assertIn("writing.md", text)
        self.assertIn("research.md", text)
        self.assertIn("general.md", text)
        self.assertIn("self-hosted-work", text)


if __name__ == "__main__":
    unittest.main()
