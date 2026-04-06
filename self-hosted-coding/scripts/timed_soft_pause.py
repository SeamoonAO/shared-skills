#!/usr/bin/env python3

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc)


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def load_state(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def is_expired(state: dict) -> bool:
    return parse_timestamp(state["deadline_at"]) <= utc_now()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create and inspect portable timed soft-pause state for external orchestrators."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a pending soft-pause state file.")
    create.add_argument("--state", required=True, help="Path to the JSON state file.")
    create.add_argument("--question", required=True, help="Question asked during the soft pause.")
    create.add_argument("--recommended", required=True, help="Recommended option if the pause expires.")
    create.add_argument(
        "--timeout-seconds",
        type=int,
        default=120,
        help="How long to wait before the recommendation should be resumed automatically.",
    )

    status = subparsers.add_parser("status", help="Report whether the soft pause is pending or expired.")
    status.add_argument("--state", required=True, help="Path to the JSON state file.")

    resume = subparsers.add_parser(
        "resume-prompt",
        help="Emit a standard resume instruction once the soft pause has expired.",
    )
    resume.add_argument("--state", required=True, help="Path to the JSON state file.")

    return parser


def handle_create(args: argparse.Namespace) -> int:
    created_at = utc_now()
    deadline_at = created_at + timedelta(seconds=args.timeout_seconds)
    state = {
        "status": "pending",
        "question": args.question,
        "recommended": args.recommended,
        "timeout_seconds": args.timeout_seconds,
        "created_at": created_at.isoformat(),
        "deadline_at": deadline_at.isoformat(),
    }
    path = Path(args.state).expanduser().resolve()
    save_state(path, state)
    print(f"pending {path} until {state['deadline_at']}")
    return 0


def handle_status(args: argparse.Namespace) -> int:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    status = "expired" if is_expired(state) else "pending"
    print(f"{status} {path}")
    return 0


def handle_resume_prompt(args: argparse.Namespace) -> int:
    path = Path(args.state).expanduser().resolve()
    state = load_state(path)
    if not is_expired(state):
        print("soft pause not expired yet", file=sys.stderr)
        return 1

    print(
        "Soft-pause deadline elapsed without user reply. "
        f"Continue with the previously recommended option: {state['recommended']}"
    )
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "create":
        return handle_create(args)
    if args.command == "status":
        return handle_status(args)
    if args.command == "resume-prompt":
        return handle_resume_prompt(args)

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
