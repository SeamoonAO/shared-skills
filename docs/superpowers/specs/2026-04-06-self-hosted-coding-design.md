# Self-Hosted Coding Design

**Date:** 2026-04-06

**Goal:** Create a cross-platform skill that lets a user tell Codex, Cursor, or Claude Code to continue a coding task with higher autonomy, while still enforcing explicit stop rules, disciplined debugging, and selective experience capture.

## Scope

This skill defines a work protocol, not a coding technique. It decides:

- when the agent should continue autonomously
- when it should pause and ask
- when it should switch into systematic debugging
- when it should summarize reusable lessons
- when it may call helper skills such as `systematic-debugging`, `continual-learning`, or `ralph-loop`

It does not replace normal implementation, testing, or domain-specific skills.

## Trigger Model

The skill should trigger only when the user clearly asks for higher-autonomy execution. Typical triggers:

- explicit skill invocation
- explicit mode words such as `强自治` or `半自治`
- instructions such as "继续迭代", "自行决策", "托管推进", or "不要每步都问我"

It should not trigger for ordinary coding requests that do not ask for this protocol.

## Mode Resolution

Mode precedence:

1. Explicit mode words from the user
2. Clear intent inferred from current conversation context
3. Default mode when the skill is explicitly invoked without a mode

Default mode: `强自治`

## Execution Modes

### 强自治

The agent should keep moving through analysis, implementation, testing, fixes, and re-verification with minimal interruption. It should only stop for hard red lines, true blockers, or consequential ambiguity.

### 半自治

The agent may work autonomously inside a stage, but it must stop after each stage and wait for confirmation before continuing. Default stage boundaries:

- diagnosis and plan
- implementation
- verification
- wrap-up and lessons

## Hard Stop Rules

The agent must stop and ask before any of the following:

- deployment, release, or pushing to a remote
- large-scale deletion of code or important data
- major architectural or foundational stack changes
- modifying important environment variables, secrets, or account configuration
- database migrations or production data operations
- paid actions or network calls to outside services
- modifying critical prompts, automations, or system configuration without explicit user authorization

## Debugging Rule

When the task enters a failure state, the agent should automatically use `systematic-debugging` if available. Failure state includes:

- bugs
- test failures
- unexpected behavior
- unclear root cause
- repeated failed fixes

If the helper skill is unavailable, the agent should follow the same root-cause-first discipline manually.

## Experience Capture

Default behavior is conservative.

- Do not summarize lessons for one-off noise.
- Write project-specific lessons into project documentation when they are concrete and stable.
- Write higher-level collaboration rules into `AGENTS.md` or equivalent long-term memory only when they are stable enough to influence future sessions.
- When both are needed, write details in project docs and short durable rules in `AGENTS.md`.

## Relationship To Helper Skills

### `continual-learning`

Borrow the principle of separating execution from long-term memory maintenance. Call it only when long-term memory maintenance is explicitly appropriate.

### `ralph-loop`

Borrow the principle of sustained iteration and strict completion standards. Do not start a real autonomous loop unless the user explicitly asks for one and the current platform supports it.

## Cross-Platform Requirement

This skill must work conceptually across Codex, Cursor, and Claude Code.

- Prefer native skills or tools available in the current environment.
- Do not rely on Cursor-specific loop hooks or file conventions.
- If a helper skill is unavailable, preserve the behavior manually rather than dropping it.

## Design Constraints

- Keep `SKILL.md` concise and directive.
- Put trigger conditions in frontmatter, not in the body.
- Use explicit decision rules and flat lists instead of long narrative explanations.
- Keep the skill focused on execution protocol, not implementation details.
