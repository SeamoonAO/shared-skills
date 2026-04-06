# Self-Hosted Work Upgrade Candidates

Record distilled protocol candidates here before changing `SKILL.md` or a branch reference.

## What belongs here

- cross-project behavior patterns
- recurring ambiguity in autonomy, checkpoints, planning, verification, or memory handling
- concise candidate rules that might tighten or clarify the protocol across work types

## What does not belong here

- project-specific bugs or repo details
- one-off anecdotes
- implementation notes that belong in project docs
- protocol changes that are already approved and merged
- rejected candidates and review failures (store those in `../logs/review-loop.log`)

## Promotion rule

Move a candidate into a protocol file only when one of these is true:

- it tightens or clarifies the protocol without weakening an existing guardrail
- the user explicitly approves the protocol change

Prefer replacing or compressing existing text over appending more text.
Do not read `../logs/review-loop.log` unless the user explicitly wants a review-history audit or the raw log needs investigation.

## Review Loop

Use this three-pass review loop when a candidate matters enough for subagent evaluation:

1. Extraction pass
   Capture the proposed rule from raw artifacts without deciding whether it should be promoted.
2. Challenge pass
   Try to falsify it: is it project-specific, redundant, too wordy, or likely to weaken an existing guardrail?
3. Protocol pass
   Main agent decides where it belongs: reject it, keep it here, move it to project docs, or promote it into a protocol file.

Subagent output is review feedback, not authority. Main-agent verification is still required.

## Candidate template

```markdown
## Candidate: <short label>

Signal:
- what recurring behavior or ambiguity exposed this

Proposed rule:
- one concise rule in protocol language

Scope:
- why this is cross-project rather than project-specific

Promotion status:
- pending user approval
- safe tightening

Review notes:
- extraction
- challenge
- protocol decision
```
