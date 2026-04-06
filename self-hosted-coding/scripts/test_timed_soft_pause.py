import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("timed_soft_pause.py")


class TimedSoftPauseTests(unittest.TestCase):
    def test_create_writes_pending_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "soft-pause.json"
            cmd = [
                "python3",
                str(SCRIPT),
                "create",
                "--state",
                str(state_path),
                "--question",
                "Which parser should I pick?",
                "--recommended",
                "Use the existing conservative parser path.",
                "--timeout-seconds",
                "120",
            ]

            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            self.assertTrue(state_path.exists())
            record = json.loads(state_path.read_text())
            self.assertEqual(record["status"], "pending")
            self.assertEqual(record["question"], "Which parser should I pick?")
            self.assertEqual(record["recommended"], "Use the existing conservative parser path.")
            self.assertEqual(record["timeout_seconds"], 120)
            self.assertIn("pending", result.stdout)

    def test_status_reports_pending_and_expired(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "soft-pause.json"
            create_cmd = [
                "python3",
                str(SCRIPT),
                "create",
                "--state",
                str(state_path),
                "--question",
                "Continue?",
                "--recommended",
                "Proceed with the conservative default.",
                "--timeout-seconds",
                "120",
            ]
            subprocess.run(create_cmd, check=True, capture_output=True, text=True)

            pending_cmd = [
                "python3",
                str(SCRIPT),
                "status",
                "--state",
                str(state_path),
            ]
            pending = subprocess.run(pending_cmd, check=True, capture_output=True, text=True)
            self.assertIn("pending", pending.stdout)

            record = json.loads(state_path.read_text())
            record["deadline_at"] = "2000-01-01T00:00:00+00:00"
            state_path.write_text(json.dumps(record), encoding="utf-8")

            expired = subprocess.run(pending_cmd, check=True, capture_output=True, text=True)
            self.assertIn("expired", expired.stdout)

    def test_resume_prompt_only_emits_after_expiry(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "soft-pause.json"
            create_cmd = [
                "python3",
                str(SCRIPT),
                "create",
                "--state",
                str(state_path),
                "--question",
                "Continue?",
                "--recommended",
                "Proceed with the conservative default.",
                "--timeout-seconds",
                "120",
            ]
            subprocess.run(create_cmd, check=True, capture_output=True, text=True)

            resume_cmd = [
                "python3",
                str(SCRIPT),
                "resume-prompt",
                "--state",
                str(state_path),
            ]
            pending = subprocess.run(resume_cmd, capture_output=True, text=True)
            self.assertEqual(pending.returncode, 1)
            self.assertIn("not expired", pending.stderr)

            record = json.loads(state_path.read_text())
            record["deadline_at"] = "2000-01-01T00:00:00+00:00"
            state_path.write_text(json.dumps(record), encoding="utf-8")

            expired = subprocess.run(resume_cmd, check=True, capture_output=True, text=True)
            self.assertIn("Continue with the previously recommended option", expired.stdout)
            self.assertIn("Proceed with the conservative default.", expired.stdout)


if __name__ == "__main__":
    unittest.main()
