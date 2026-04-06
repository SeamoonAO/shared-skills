---
name: self-hosted-work
description: Use when the user explicitly asks the agent to continue a task with higher autonomy, self-host execution, switch between 强自治 and 半自治, or says things like “继续迭代”, “托管推进”, “自行决策”, or “不要每步都问我” while the task may be coding, writing, research, or other work.
---

# Self-Hosted Work

Continue a task with an explicit autonomy protocol. This is a work agreement for how to proceed, not a replacement for domain-specific skills.

User instructions override mode defaults. If the current message is tighter than this skill, follow the tighter boundary. When this skill is improving itself or another governance file, preserve or tighten guardrails by default.

## Trigger and Mode Resolution

Use this skill only when the user clearly asks for higher-autonomy execution. Strong triggers:

- explicit invocation of `$self-hosted-work`
- explicit mode words such as `强自治` or `半自治`
- requests such as "continue iterating", "self-host this task", "make reasonable decisions", or "don't stop for every step"

Do not use this skill for ordinary task requests that do not ask for this protocol. A plain "继续" is not enough unless the surrounding context clearly asks for higher-autonomy execution.

Resolve mode in this order:

1. Use the user's explicit mode words.
2. Infer the mode from current conversation context if the user's intent is already clear.
3. Default to `强自治` when the user invokes this skill without naming a mode.

When a `半自治` checkpoint is active, a brief reply such as "继续", "go on", or "next" approves only the next stage. Do not silently switch back to `强自治` unless the user says so.

## Task-Type Routing

Route to one branch at a time:

- `coding`: code, bug, refactor, test, implement, fix, script, tooling, or deploy-adjacent software work. Load `references/coding.md`.
- `writing`: write, draft, rewrite, article, essay, post, outline, polish, edit, audience, or tone work. Load `references/writing.md`.
- `research`: research, investigate, analyze, compare, evaluate, gather evidence, or summarize sources. Load `references/research.md`.
- `general`: if none of the above clearly fits, load `references/general.md`.

Do not load multiple branch files just because the broader project spans several phases. Use the branch for the current dominant phase. Internal plan/todo tracking is execution scaffolding, not a branch switch.

## Execution Modes

### `强自治`

Keep moving through the current task with minimal interruption.

- Continue until the task is genuinely complete, clearly blocked, or stopped by a hard rule.
- Make reasonable local decisions without step-by-step approval.
- Prefer conservative local assumptions over waiting for routine clarification.
- Stop only for hard red lines, true blockers, or consequential ambiguity.

### `半自治`

Work autonomously within a stage, then stop for confirmation before entering the next one.

- Use these default stages unless the user defines different ones:
  - diagnosis and plan
  - execution
  - verification
  - wrap-up and lessons
- Stop after each stage and wait for confirmation before continuing.
- Phrases such as "keep going unless something is seriously wrong" do not cancel the stage checkpoint.

## Hard Stop Rules

Stop and ask before any of the following, regardless of mode:

- publish, send, submit, release, deploy, push, or otherwise externalize the result
- call external network services, spend money, or use paid retrieval
- modify important account configuration, secrets, environment configuration, or system configuration
- delete important material at large scale or make other clearly irreversible changes
- weaken this skill or another governance/protocol file by expanding autonomy, loosening hard stops, or relaxing verification or memory discipline
- modify critical prompts, automations, or system configuration without explicit authorization

For non-hard-stop ambiguity, prefer conservative defaults and continue. Do not turn ordinary implementation questions into approval checkpoints.

Pause only when several reasonable options exist and the choice would materially redirect long-term maintenance, scope, conventions, or downstream rework.

## Planning Discipline

Use the lightest planning shape that keeps execution reliable:

- simple task: keep a short todo only
- medium task: build and maintain a minimal internal plan before or during execution
- complex task: map the major files, stages, and verification path before making broad changes

Escalate planning as complexity grows, not by default. Use plans to prevent drift, missed verification, and lost context.

Call `writing-plans` only when the task needs a durable handoff artifact, long-running multi-stage execution, or explicit subtask decomposition that should survive context loss.

## Progress and Completion Discipline

Borrow the sustained-iteration discipline of `ralph-loop` without requiring an actual loop.

- Base each next action on the latest evidence, not on a fresh speculative restart.
- Keep iterating until completion is real, not just plausible.
- Do not declare success because the result looks "close enough".
- Do not turn "keep going" into infinite looping.

Start a real `ralph-loop` only when the user explicitly asks for one and the current platform supports it.
Before claiming completion, apply evidence-first verification manually or via the current branch's recommended helper.

## Soft Pause Discipline

In `强自治`, progress updates are for synchronization, not permission. If the user is quiet and no hard stop has fired, keep moving along the most conservative viable path.

Use a soft pause only when a brief user answer could reduce rework on a consequential but non-hard-stop choice. When that happens:

- state the question, the recommended option, and why that option is the conservative path
- if the current platform or external orchestrator supports timed resume, a short countdown such as about two minutes may be used before continuing with the recommended option, using `scripts/timed_soft_pause.py` or an equivalent helper when useful
- never use timed resume for hard stops
- if timed resume is unavailable, do not pretend it exists; either continue with the conservative choice in `强自治` or wait normally in `半自治`

## Self-Assessment

During execution, reassess these states:

- boundary state: are you approaching a hard stop or a tighter user boundary
- route state: is the current branch still the right dominant task type
- mode state: does the current reply approve only the next stage, or actually change the mode
- planning state: is a todo enough, or has the task crossed the threshold for a minimal or formal plan
- failure state: should the active branch switch into tighter domain-specific recovery
- pause state: is this truly a hard stop or soft pause, or should it be resolved locally
- completion state: is the evidence strong enough to claim the task is done
- lesson state: is there a distilled, cross-project protocol insight worth recording as a candidate

Use self-assessment to tighten execution, not to rewrite the protocol mid-task.

## Review Loop

When a protocol lesson seems worth upgrading, isolate evaluation from execution:

- use subagents with minimal task-local context when that materially improves rigor
- treat subagent output as review feedback, not as authority
- evaluate candidate rules the way you would handle code review: verify against actual behavior, reject project-specific noise, and push back on weak suggestions
- prefer writing candidates to `references/upgrade-candidates.md` before changing protocol files
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
- Do not promote a candidate into a protocol file unless it tightens or clarifies the protocol without weakening it, or the user explicitly approves the change.
- When updating protocol files, prefer replacing, compressing, or moving text to references over appending more rules.
- Do not read `logs/review-loop.log` by default; use it as a machine-written history file.

## Red Flags

Stop and correct course if you notice any of these thoughts:

- "The next stage is obvious, so I can skip the 半自治 checkpoint."
- "This is close enough to done."
- "I will just publish, send, deploy, or call the service quickly and explain later."
- "The helper skill is missing, so I can skip the discipline entirely."
- "This lesson might be useful, so I should update long-term memory immediately."
- "The user said continue, so they must want higher autonomy."
- "The user said continue after a 半自治 checkpoint, so I can drop the checkpoint pattern now."
- "This only changes the protocol, so I can relax the boundary quietly."

## Cross-Platform Adaptation

Keep this protocol platform-agnostic across Codex, Cursor, and Claude Code.

- Prefer helper skills or tools available in the current environment.
- If a helper skill is unavailable, preserve the behavior manually instead of dropping it.
- Distinguish platform-native `Plan Mode` from internal plan/todo scaffolding. Native plan mode is a session-level planning constraint; internal plans are execution aids.
- If the platform is already in a native `Plan Mode`, respect that mode and produce a decision-complete plan instead of silently treating it like ordinary execution state.
- Do not rely on Cursor-only hooks, files, or loop mechanics.
- Treat timed soft pause as an optional accelerator that needs platform or orchestrator support, not as a guaranteed built-in capability.
- Treat `ralph-loop` and `continual-learning` as optional accelerators, not hard dependencies.
