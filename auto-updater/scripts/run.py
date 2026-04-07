#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import Dict, Iterable, List, Optional, Tuple


SKIP_NAMES = {".system"}
SNAPSHOT_METADATA_NAME = ".auto-updater-source.json"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_skill_dirs(home: Path) -> List[Path]:
    return [home / ".codex" / "skills", home / ".cursor" / "skills"]


def load_sources(config_path: Path) -> List[dict]:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return data["sources"]


def scan_source_skill_dirs(source_defs: List[dict]) -> Dict[str, dict]:
    index: Dict[str, dict] = {}
    for source in source_defs:
        root = Path(source["root"]).resolve()
        skills: Dict[str, Path] = {}
        if root.exists():
            for skill_md in root.rglob("SKILL.md"):
                skills[skill_md.parent.name] = skill_md.parent.resolve()
        index[source["name"]] = {
            **source,
            "root": root,
            "skills": skills,
        }
    return index


def discover_installed_skills(skill_dirs: Iterable[Path]) -> Dict[str, dict]:
    discovered: Dict[str, dict] = {}
    for base in skill_dirs:
        if not base.exists():
            continue
        for entry in sorted(base.iterdir()):
            if entry.name in SKIP_NAMES or entry.name.startswith("."):
                continue
            if not entry.is_symlink():
                continue
            record = {
                "name": entry.name,
                "link": entry,
                "raw_target": entry.readlink(),
                "resolved": entry.resolve(),
                "base": base,
            }
            if entry.name not in discovered:
                discovered[entry.name] = {
                    "name": entry.name,
                    "resolved": record["resolved"],
                    "entries": [record],
                }
            else:
                discovered[entry.name]["entries"].append(record)
    return discovered


def compute_tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.name == SNAPSHOT_METADATA_NAME:
            continue
        rel = path.relative_to(root)
        if path.is_dir():
            digest.update(f"dir:{rel}".encode("utf-8"))
            continue
        if path.is_symlink():
            digest.update(f"link:{rel}->{os.readlink(path)}".encode("utf-8"))
            continue
        digest.update(f"file:{rel}".encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def snapshot_source_is_dirty(root: Path, metadata_path: Path) -> bool:
    if not metadata_path.exists():
        return True
    data = json.loads(metadata_path.read_text(encoding="utf-8"))
    return data.get("tree_hash") != compute_tree_hash(root)


def build_link_repairs(installed: Dict[str, dict], source_index: Dict[str, dict]) -> List[Tuple[Path, Path]]:
    repairs: List[Tuple[Path, Path]] = []
    for skill_name, info in installed.items():
        canonical = find_canonical_target(skill_name, info["resolved"], source_index)
        if canonical is None:
            continue
        for entry in info.get("entries", []):
            current_target = absolute_link_target(entry["link"], entry["raw_target"])
            if current_target != canonical:
                repairs.append((entry["link"], canonical))
    return repairs


def find_canonical_target(skill_name: str, resolved: Path, source_index: Dict[str, dict]) -> Optional[Path]:
    for source in source_index.values():
        target = source["skills"].get(skill_name)
        if target is None:
            continue
        if resolved == target or is_relative_to(resolved, source["root"]):
            return target
    return None


def absolute_link_target(link: Path, raw_target: Path) -> Path:
    if raw_target.is_absolute():
        return raw_target
    return (link.parent / raw_target).absolute()


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def load_clawhub_locks(home: Path) -> Dict[str, str]:
    locks: Dict[str, str] = {}
    for workdir in (home / ".codex", home / ".cursor"):
        lock = workdir / ".clawhub" / "lock.json"
        if not lock.exists():
            continue
        data = json.loads(lock.read_text(encoding="utf-8"))
        for slug in data.get("skills", {}).keys():
            locks[slug] = str(workdir)
    return locks


def classify_sources(
    installed: Dict[str, dict],
    source_index: Dict[str, dict],
    clawhub_locks: Dict[str, str],
) -> Tuple[Dict[str, dict], List[dict]]:
    managed: Dict[str, dict] = {}
    unmanaged: List[dict] = []

    for skill_name, info in installed.items():
        sample = info.get("entries", [info])[0]
        matched = False
        for source_name, source in source_index.items():
            target = source["skills"].get(skill_name)
            if target is None:
                continue
            if sample["resolved"] == target or is_relative_to(sample["resolved"], source["root"]):
                managed.setdefault(
                    source_name,
                    {
                        "id": source_name,
                        "name": source_name,
                        "strategy": source["strategy"],
                        "root": source["root"],
                        "source": source,
                        "skills": set(),
                    },
                )["skills"].add(skill_name)
                matched = True
                break

        if matched:
            continue

        origin = sample["resolved"] / ".clawhub" / "origin.json"
        if origin.exists():
            origin_data = json.loads(origin.read_text(encoding="utf-8"))
            slug = origin_data.get("slug")
            workdir = clawhub_locks.get(slug)
            if slug and workdir:
                managed.setdefault(
                    f"clawhub:{slug}",
                    {
                        "id": f"clawhub:{slug}",
                        "name": slug,
                        "strategy": "clawhub",
                        "root": sample["resolved"],
                        "source": {
                            "slug": slug,
                            "workdir": workdir,
                        },
                        "skills": set(),
                    },
                )["skills"].add(skill_name)
                continue

        unmanaged.append(
            {
                "name": skill_name,
                "target": str(sample["resolved"]),
                "reason": "No configured source matched the resolved target",
            }
        )

    return managed, unmanaged


def run_command(cmd: List[str], cwd: Optional[Path] = None, capture_output: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=capture_output,
        text=True,
        check=False,
    )


def git_status(root: Path) -> dict:
    branch = run_command(["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"])
    if branch.returncode != 0:
        return {"ok": False, "reason": branch.stderr.strip() or branch.stdout.strip()}

    dirty = run_command(["git", "-C", str(root), "status", "--porcelain"])
    if dirty.returncode != 0:
        return {"ok": False, "reason": dirty.stderr.strip() or dirty.stdout.strip()}

    upstream = run_command(["git", "-C", str(root), "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if upstream.returncode != 0:
        return {
            "ok": True,
            "dirty": bool(dirty.stdout.strip()),
            "has_upstream": False,
            "branch": branch.stdout.strip(),
        }

    counts = run_command(["git", "-C", str(root), "rev-list", "--left-right", "--count", "HEAD...@{u}"])
    ahead, behind = (0, 0)
    if counts.returncode == 0 and counts.stdout.strip():
        left, right = counts.stdout.strip().split()
        ahead, behind = int(left), int(right)

    return {
        "ok": True,
        "dirty": bool(dirty.stdout.strip()),
        "has_upstream": True,
        "branch": branch.stdout.strip(),
        "upstream": upstream.stdout.strip(),
        "ahead": ahead,
        "behind": behind,
    }


def update_git_source(source: dict, mode: str) -> Tuple[str, str]:
    root = source["root"]
    status = git_status(root)
    if not status["ok"]:
        return "failed", status["reason"]
    if status["dirty"]:
        return "skipped_dirty", "Working tree has local changes"

    fetch = run_command(["git", "-C", str(root), "fetch", "--prune"])
    if fetch.returncode != 0:
        return "failed", fetch.stderr.strip() or fetch.stdout.strip()

    status = git_status(root)
    if not status["has_upstream"]:
        return "skipped_manual", "No upstream branch configured"
    if status["ahead"] > 0 and status["behind"] > 0:
        return "skipped_dirty", "Local branch diverged from upstream"
    if status["ahead"] > 0:
        return "skipped_dirty", "Local branch is ahead of upstream"
    if status["behind"] == 0:
        return "already_current", "Already current"
    if mode == "check":
        return "available_update", f"{status['behind']} upstream commit(s) available"

    pull = run_command(["git", "-C", str(root), "pull", "--ff-only"])
    if pull.returncode != 0:
        return "failed", pull.stderr.strip() or pull.stdout.strip()
    return "updated", pull.stdout.strip() or "Fast-forwarded"


def read_snapshot_metadata(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_snapshot_metadata(path: Path, repo: str, ref: str, commit: str, tree_hash: str) -> None:
    payload = {
        "strategy": "github_archive",
        "repo": repo,
        "ref": ref,
        "last_commit": commit,
        "tree_hash": tree_hash,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_github_commit(repo: str, ref: str) -> Tuple[Optional[str], Optional[str]]:
    result = run_command(["gh", "api", f"repos/{repo}/commits/{ref}", "--jq", ".sha"])
    if result.returncode != 0:
        return None, result.stderr.strip() or result.stdout.strip()
    return result.stdout.strip(), None


def extract_github_archive(repo: str, ref: str, destination: Path) -> Tuple[Optional[str], Optional[str]]:
    tarball = destination / "archive.tar.gz"
    with tarball.open("wb") as handle:
        process = subprocess.run(
            ["gh", "api", f"repos/{repo}/tarball/{ref}"],
            stdout=handle,
            stderr=subprocess.PIPE,
            check=False,
        )
    if process.returncode != 0:
        return None, process.stderr.decode("utf-8", errors="replace").strip()

    with tarfile.open(tarball, "r:gz") as archive:
        members = archive.getmembers()
        prefix = members[0].name.split("/")[0]
        for member in members:
            rel = Path(member.name).relative_to(prefix)
            if not rel.parts:
                continue
            member.name = str(rel)
            archive.extract(member, destination)

    tarball.unlink()
    return prefix, None


def update_github_archive_source(source: dict, mode: str) -> Tuple[str, str]:
    root = source["root"]
    metadata_name = source["source"].get("metadata_file", SNAPSHOT_METADATA_NAME)
    metadata_path = root / metadata_name
    metadata = read_snapshot_metadata(metadata_path)
    if metadata is None:
        return "skipped_manual", "Snapshot state metadata is missing"
    if snapshot_source_is_dirty(root, metadata_path):
        return "skipped_dirty", "Snapshot directory differs from the last recorded tree hash"

    repo = source["source"]["repo"]
    ref = source["source"]["ref"]
    remote_commit, error = fetch_github_commit(repo, ref)
    if error:
        return "failed", error

    current_commit = metadata.get("last_commit")
    if current_commit == remote_commit:
        return "already_current", "Already current"
    if mode == "check":
        return "available_update", f"Remote commit {remote_commit[:12]} is newer than {current_commit[:12]}"

    with tempfile.TemporaryDirectory(prefix="auto-updater-") as tmp:
        extract_root = Path(tmp) / "repo"
        extract_root.mkdir(parents=True)
        _, error = extract_github_archive(repo, ref, extract_root)
        if error:
            return "failed", error

        extracted_hash = compute_tree_hash(extract_root)
        write_snapshot_metadata(
            extract_root / metadata_name,
            repo=repo,
            ref=ref,
            commit=remote_commit,
            tree_hash=extracted_hash,
        )

        backup = root.parent / f".{root.name}.backup"
        if backup.exists():
            shutil.rmtree(backup)
        root.rename(backup)
        try:
            extract_root.rename(root)
        except Exception:
            if not root.exists() and backup.exists():
                backup.rename(root)
            raise
        shutil.rmtree(backup)

    return "updated", f"Updated to {remote_commit[:12]}"


def update_clawhub_source(source: dict, mode: str) -> Tuple[str, str]:
    slug = source["source"]["slug"]
    workdir = Path(source["source"]["workdir"])
    origin_path = source["root"] / ".clawhub" / "origin.json"
    if not origin_path.exists():
        return "skipped_manual", "Missing .clawhub origin metadata"
    origin = json.loads(origin_path.read_text(encoding="utf-8"))
    installed_version = origin.get("installedVersion")

    inspect = run_command(["npx", "-y", "clawhub@latest", "inspect", slug, "--no-input"])
    if inspect.returncode != 0:
        return "failed", inspect.stderr.strip() or inspect.stdout.strip()

    latest = None
    for line in inspect.stdout.splitlines():
        if line.startswith("Latest:"):
            latest = line.split(":", 1)[1].strip()
            break
    if not latest:
        return "failed", "Could not determine latest ClawHub version"
    if latest == installed_version:
        return "already_current", "Already current"
    if mode == "check":
        return "available_update", f"{installed_version} -> {latest}"

    expected_install_root = workdir / "skills" / slug
    if source["root"].resolve() != expected_install_root.resolve():
        return "skipped_manual", "ClawHub-managed source is not installed at the canonical lockfile path"

    update = run_command(
        ["npx", "-y", "clawhub@latest", "--workdir", str(workdir), "--dir", "skills", "update", slug],
    )
    if update.returncode != 0:
        return "failed", update.stderr.strip() or update.stdout.strip()
    return "updated", f"{installed_version} -> {latest}"


def apply_link_repairs(repairs: List[Tuple[Path, Path]]) -> List[Tuple[Path, Path]]:
    applied: List[Tuple[Path, Path]] = []
    for link, target in repairs:
        if link.is_symlink():
            link.unlink()
        elif link.exists():
            continue
        link.symlink_to(target, target_is_directory=True)
        applied.append((link, target))
    return applied


def summarize(results: Dict[str, List[str]]) -> str:
    order = [
        "Updated",
        "Already current",
        "Available updates",
        "Skipped (dirty)",
        "Skipped (manual/unmanaged)",
        "Failed",
        "Links repaired",
    ]
    lines: List[str] = []
    for heading in order:
        lines.append(f"{heading}:")
        entries = results.get(heading, [])
        if not entries:
            lines.append("- none")
        else:
            for entry in entries:
                lines.append(f"- {entry}")
        lines.append("")
    return "\n".join(lines).strip()


def execute(mode: str, home: Path) -> int:
    config_path = repo_root() / "auto-updater" / "sources.json"
    sources = load_sources(config_path)
    source_index = scan_source_skill_dirs(sources)
    installed = discover_installed_skills(default_skill_dirs(home))
    clawhub_locks = load_clawhub_locks(home)
    managed_sources, unmanaged_skills = classify_sources(installed, source_index, clawhub_locks)
    repairs = build_link_repairs(installed, source_index)

    results: Dict[str, List[str]] = {
        "Updated": [],
        "Already current": [],
        "Available updates": [],
        "Skipped (dirty)": [],
        "Skipped (manual/unmanaged)": [],
        "Failed": [],
        "Links repaired": [],
    }

    for info in unmanaged_skills:
        results["Skipped (manual/unmanaged)"].append(f"{info['name']}: {info['reason']} ({info['target']})")

    for source_name in sorted(managed_sources.keys()):
        source = managed_sources[source_name]
        strategy = source["strategy"]
        if strategy == "git":
            bucket, detail = update_git_source(source, mode)
        elif strategy == "github_archive":
            bucket, detail = update_github_archive_source(source, mode)
        elif strategy == "manual":
            bucket, detail = "skipped_manual", "No automatic upstream configured"
        elif strategy == "clawhub":
            bucket, detail = update_clawhub_source(source, mode)
        else:
            bucket, detail = "failed", f"Unknown strategy: {strategy}"

        label = f"{source['name']}: {detail}"
        if bucket == "updated":
            results["Updated"].append(label)
        elif bucket == "already_current":
            results["Already current"].append(label)
        elif bucket == "available_update":
            results["Available updates"].append(label)
        elif bucket == "skipped_dirty":
            results["Skipped (dirty)"].append(label)
        elif bucket == "skipped_manual":
            results["Skipped (manual/unmanaged)"].append(label)
        else:
            results["Failed"].append(label)

    applied = apply_link_repairs(repairs)
    for link, target in applied:
        results["Links repaired"].append(f"{link} -> {target}")

    print(summarize(results))
    return 0 if not results["Failed"] else 1


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update local Codex/Cursor skill sources safely.")
    parser.add_argument("mode", choices=["check", "safe-update"], nargs="?", default="safe-update")
    parser.add_argument("--home", default=str(Path.home()), help="Home directory used to discover Codex/Cursor skills")
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    return execute(args.mode, Path(args.home))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
