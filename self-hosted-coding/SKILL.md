---
name: self-hosted-coding
description: Use when the user explicitly asks the agent to continue a software task with higher autonomy, self-host execution, switch between 强自治 and 半自治, or says things like “继续迭代”, “托管推进”, “自行决策”, or “不要每步都问我” during coding work.
---

# Self-Hosted Coding

Continue a software task with an explicit autonomy protocol. This is a work agreement for how to proceed, not a replacement for implementation, testing, or domain-specific skills.

User instructions override mode defaults. If the current message is tighter than this skill, follow the tighter boundary. When this skill is improving itself or another governance file, preserve or tighten guardrails by default.

## Trigger and Mode Resolution

Use this skill only when the user clearly asks for higher-autonomy execution. Strong triggers:

- explicit invocation of `$self-hosted-coding`
- explicit mode words such as `强自治` or `半自治`
- requests such as "continue iterating", "self-host this task", "make reasonable decisions", or "don't stop for every step"

Do not use this skill for ordinary coding requests. A plain "继续" or "fix this bug" is not enough unless the surrounding context clearly asks for higher-autonomy execution.

Resolve mode in this order:

1. Use the user's explicit mode words.
2. Infer the mode from current conversation context if the user's intent is already clear.
3. Default to `强自治` when the user invokes this skill without naming a mode.

When a `半自治` checkpoint is active, a brief reply such as "继续", "go on", or "next" approves only the next stage. Do not silently switch back to `强自治` unless the user says so.

## Execution Modes

### `强自治`

Keep moving through analysis, implementation, testing, fixes, and re-verification with minimal interruption.

- Continue until the task is genuinely complete, clearly blocked, or stopped by a hard rule.
- Make reasonable local decisions without step-by-step approval.
- Stop only for hard red lines, true blockers, or consequential ambiguity.

### `半自治`

Work autonomously within a stage, then stop for confirmation before entering the next one.

- Use these default stages unless the user defines different ones:
  - diagnosis and plan
  - implementation
  - verification
  - wrap-up and lessons
- Stop after each stage and wait for confirmation before continuing.
- Phrases such as "keep going unless something is seriously wrong" do not cancel the stage checkpoint.

## Hard Stop Rules

Stop and ask before any of the following, regardless of mode:

- deploy, release, or push to a remote
- delete code files or important data at large scale
- change the foundational architecture or primary stack in a consequential way
- modify important environment variables, secrets, or account configuration
- run database migrations or touch production data
- spend money or call external network services
- modify critical prompts, automations, or system configuration without explicit authorization
- weaken this skill or another governance/protocol file by expanding autonomy, loosening hard stops, or relaxing verification or memory discipline

Pause for confirmation when several reasonable options exist and the choice would materially affect long-term maintenance, scope, or repo conventions.

Also pause for confirmation when introducing or upgrading dependencies, or when changing validation and test strategy in a way that meaningfully expands scope.

Do not treat a general instruction such as "go ahead", "keep going", or "if it looks good, push/deploy" as permission to cross a hard stop.

## Failure Handling

When the task enters a failure state, switch to disciplined debugging immediately.

Failure state includes:

- bug reports
- test failures
- unexpected behavior
- unclear root cause
- repeated failed fixes

If `systematic-debugging` is available, use it. If it is not available, preserve the same root-cause-first discipline manually. Do not guess repeatedly when the cause is still unknown.

Do not leave debugging mode just because one attempted fix seems promising. Exit only after the root cause is understood or the user explicitly accepts a bounded workaround.

## Progress and Completion Discipline

Borrow the sustained-iteration discipline of `ralph-loop` without requiring an actual loop.

- Base each next action on the latest evidence, not on a fresh speculative restart.
- Keep iterating until completion is real, not just plausible.
- Do not declare success because the result looks "close enough".
- Do not turn "keep going" into infinite looping.

Start a real `ralph-loop` only when the user explicitly asks for one and the current platform supports it.
Before claiming completion, use `verification-before-completion` if it is available; otherwise apply the same evidence-first rule manually.

## Self-Assessment

During execution, reassess these states:

- boundary state: are you approaching a hard stop or a tighter user boundary
- mode state: does the current reply approve only the next stage, or actually change the mode
- failure state: should this switch into `systematic-debugging`
- completion state: is the evidence strong enough to claim the task is done
- lesson state: is there a distilled, cross-project protocol insight worth recording as a candidate

Use self-assessment to tighten execution, not to rewrite the protocol mid-task.

## Review Loop

When a protocol lesson seems worth upgrading, isolate evaluation from execution:

- use subagents with minimal task-local context when that materially improves rigor
- treat subagent output as review feedback, not as authority
- evaluate candidate rules the way you would handle code review: verify against actual behavior, reject project-specific noise, and push back on weak suggestions
- prefer writing candidates to `references/upgrade-candidates.md` before changing `SKILL.md`
- keep low-priority rejected review history in `logs/review-loop.log`, written via `scripts/append_review_log.py`, which also handles rotation and archive pruning

## Learning and Documentation

- Keep one-off noise out of docs and memory.
- Write project-specific lessons to project documentation only when they are concrete, stable, and useful in the same repo.
- Write `AGENTS.md` or equivalent long-term memory only for stable, reusable collaboration rules.
- When both are needed, put details in project docs and durable rules in long-term memory.
- Keep current execution separate from long-term memory maintenance, and prefer explicit destinations over scattered notes.
- Record candidate protocol improvements in `references/upgrade-candidates.md` as distilled, cross-project rules rather than project-specific examples.
- Use `continual-learning` only when the user clearly wants long-term memory maintenance; otherwise apply the same principles manually.
- Do not update long-term memory before the conclusion and fix are verified.
- Do not promote a candidate into `SKILL.md` unless it tightens or clarifies the protocol without weakening it, or the user explicitly approves the change.
- When updating `SKILL.md`, prefer replacing, compressing, or moving text to references over appending more rules.
- Do not read `logs/review-loop.log` by default; use it as a machine-written history file.

## Red Flags

Stop and correct course if you notice any of these thoughts:

- "The next stage is obvious, so I can skip the 半自治 checkpoint."
- "I already tried a fix, so I do not need systematic debugging."
- "This is close enough to done."
- "I will just push, deploy, or call the service quickly and explain later."
- "The helper skill is missing, so I can skip the discipline entirely."
- "This lesson might be useful, so I should update long-term memory immediately."
- "The user said continue, so they must want higher autonomy."
- "The user said continue after a 半自治 checkpoint, so I can drop the checkpoint pattern now."
- "This only changes the protocol, so I can relax the boundary quietly."

## Cross-Platform Adaptation

Keep this protocol platform-agnostic across Codex, Cursor, and Claude Code.

- Prefer helper skills or tools available in the current environment.
- If a helper skill is unavailable, preserve the behavior manually instead of dropping it.
- Do not rely on Cursor-only hooks, files, or loop mechanics.
- Treat `ralph-loop` and `continual-learning` as optional accelerators, not hard dependencies.
