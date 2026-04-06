import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("append_review_log.py")


class AppendReviewLogTests(unittest.TestCase):
    def test_appends_structured_json_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cmd = [
                "python3",
                str(SCRIPT),
                "--root",
                str(root),
                "--name",
                "sample-candidate",
                "--outcome",
                "rejected",
                "--summary",
                "too vague",
                "--category",
                "ambiguity",
            ]

            subprocess.run(cmd, check=True)

            log_path = root / "logs" / "review-loop.log"
            self.assertTrue(log_path.exists())
            lines = log_path.read_text().strip().splitlines()
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])
            self.assertEqual(record["name"], "sample-candidate")
            self.assertEqual(record["outcome"], "rejected")
            self.assertEqual(record["summary"], "too vague")
            self.assertEqual(record["category"], "ambiguity")

    def test_rotates_when_log_exceeds_max_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            logs_dir = root / "logs"
            logs_dir.mkdir(parents=True)
            log_path = logs_dir / "review-loop.log"
            log_path.write_text("x" * 200)

            cmd = [
                "python3",
                str(SCRIPT),
                "--root",
                str(root),
                "--name",
                "rotate-me",
                "--outcome",
                "rejected",
                "--summary",
                "rotate",
                "--max-bytes",
                "100",
            ]

            subprocess.run(cmd, check=True)

            archive_dir = logs_dir / "archive"
            archived = list(archive_dir.glob("review-loop-*.log"))
            self.assertEqual(len(archived), 1)
            new_lines = log_path.read_text().strip().splitlines()
            self.assertEqual(len(new_lines), 1)
            record = json.loads(new_lines[0])
            self.assertEqual(record["name"], "rotate-me")

    def test_prunes_old_archives_after_rotation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            logs_dir = root / "logs"
            archive_dir = logs_dir / "archive"
            archive_dir.mkdir(parents=True)
            log_path = logs_dir / "review-loop.log"
            log_path.write_text("x" * 200)

            # Pre-seed older archives so the script has to prune.
            for name in [
                "review-loop-20260101-000001.log",
                "review-loop-20260101-000002.log",
                "review-loop-20260101-000003.log",
            ]:
                (archive_dir / name).write_text(name)

            cmd = [
                "python3",
                str(SCRIPT),
                "--root",
                str(root),
                "--name",
                "prune-me",
                "--outcome",
                "rejected",
                "--summary",
                "prune",
                "--max-bytes",
                "100",
                "--keep-archives",
                "2",
            ]

            subprocess.run(cmd, check=True)

            archived = sorted(p.name for p in archive_dir.glob("review-loop-*.log"))
            self.assertEqual(len(archived), 2)
            self.assertNotIn("review-loop-20260101-000001.log", archived)


if __name__ == "__main__":
    unittest.main()
