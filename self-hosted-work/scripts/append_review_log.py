#!/usr/bin/env python3

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Append one structured review-loop record and rotate the log if needed."
    )
    parser.add_argument("--root", default=None, help="Skill root directory. Defaults to parent of this script.")
    parser.add_argument("--name", required=True, help="Candidate or event name.")
    parser.add_argument("--outcome", required=True, help="Outcome label, for example rejected or accepted.")
    parser.add_argument("--summary", required=True, help="Short one-line summary.")
    parser.add_argument("--category", default="general", help="Short category label.")
    parser.add_argument("--signal", default="", help="Optional short signal.")
    parser.add_argument("--proposal", default="", help="Optional proposed rule.")
    parser.add_argument("--reason", default="", help="Optional concise reason.")
    parser.add_argument("--max-bytes", type=int, default=16384, help="Rotate when current log exceeds this size.")
    parser.add_argument(
        "--keep-archives",
        type=int,
        default=0,
        help="Keep only the newest N rotated logs. 0 keeps all archives.",
    )
    return parser.parse_args()


def resolve_root(arg_root):
    if arg_root:
        return Path(arg_root).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def prune_archives(archive_dir: Path, keep_archives: int):
    if keep_archives <= 0:
        return

    archives = sorted(archive_dir.glob("review-loop-*.log"))
    excess = len(archives) - keep_archives
    if excess <= 0:
        return

    for old_path in archives[:excess]:
        old_path.unlink()


def rotate_if_needed(log_path: Path, max_bytes: int, keep_archives: int):
    if not log_path.exists() or log_path.stat().st_size <= max_bytes:
        return

    archive_dir = log_path.parent / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    rotated = archive_dir / f"review-loop-{timestamp}.log"
    log_path.rename(rotated)
    prune_archives(archive_dir, keep_archives)


def main():
    args = parse_args()
    root = resolve_root(args.root)
    logs_dir = root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "review-loop.log"

    rotate_if_needed(log_path, args.max_bytes, args.keep_archives)

    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "name": args.name,
        "outcome": args.outcome,
        "category": args.category,
        "summary": args.summary,
    }
    if args.signal:
        record["signal"] = args.signal
    if args.proposal:
        record["proposal"] = args.proposal
    if args.reason:
        record["reason"] = args.reason

    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=True) + "\n")


if __name__ == "__main__":
    main()
