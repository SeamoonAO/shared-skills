---
name: auto-updater
description: "Safely update Codex/Cursor skills from shared local sources and repair skill symlinks. Supports check-only and safe-update modes."
---

# Local Auto-Updater

Use this skill to update the locally managed skill sources behind Codex and Cursor.

This version is designed for a workspace where skills are exposed through symlinks in:

- `~/.codex/skills`
- `~/.cursor/skills`

and the real source directories live under `~/code/skill-tools` or `~/code/shared-skills`.

## What It Does

The updater:

1. Scans the current Codex/Cursor skill symlinks
2. Resolves the real source directories behind those links
3. Groups skills by source project
4. Applies the configured update strategy for each source
5. Repairs existing Codex/Cursor links so they point directly at canonical targets
6. Prints a summary of what updated, what was skipped, and what failed

## Modes

### Check

Check current source state and report what would update:

```bash
python3 /Users/aoshi/code/shared-skills/auto-updater/scripts/run.py check
```

### Safe Update

Perform automatic safe updates:

```bash
python3 /Users/aoshi/code/shared-skills/auto-updater/scripts/run.py safe-update
```

Safe update rules:

- clean git sources: update with `fetch --prune` + `pull --ff-only`
- dirty git sources: skip
- managed GitHub snapshot sources: replace only when the local snapshot still matches the last recorded tree hash
- manual sources: report only
- unmanaged sources: report only

## Source Types

Configured project sources live in `sources.json`.

Current v1 sources:

- `shared-skills`
- `baoyu-skills`
- `ljg-skills`
- `superpowers`
- `cursor-plugins`

Additionally, ClawHub-installed single-skill directories are recognized when they are still managed by a local ClawHub lockfile.

## Output Summary

The script always prints grouped results for:

- `Updated`
- `Already current`
- `Available updates`
- `Skipped (dirty)`
- `Skipped (manual/unmanaged)`
- `Failed`
- `Links repaired`

## Safety Model

- No stash
- No forced overwrite of dirty sources
- No automatic installation of new skills
- No automatic publication, push, or deploy
- Only existing Codex/Cursor skill links are repaired

## Automation Use

Recommended automation command:

```bash
python3 /Users/aoshi/code/shared-skills/auto-updater/scripts/run.py safe-update
```

Recommended schedule:

- daily at `09:30`
- timezone `Asia/Shanghai`

## Notes

- `cursor-plugins` is currently treated as a manual source because this local copy does not have a configured upstream.
- `ljg-skills` and `superpowers` are updated through GitHub archive sync, not through local git history.
- ClawHub-managed skills are only updated if they are still recorded in the corresponding ClawHub lockfile.
