# Amazon Regulation Chunking Backlog

## P1

### Template-as-Source Runner

- Enforce runner execution to always consume the prompt template files in `references/` instead of hand-written compressed prompts.
- Keep Stage A execution input fixed to `Stage A template + Stage A preview markdown`.
- Keep Stage B execution input fixed to `Stage B template + Stage B preview markdown`.
- Preserve JSONL only as storage/orchestration contract, not as model-facing input.

### Stage A Prompt Tightening

- Continue reducing near-`1:1` packet replay.
- Tighten handling of dangling lead-ins such as `如下` / `例如` / `下列内容`.
- Keep disclaimers, boilerplate, and generic compliance reminders in the `0-2` score band unless they contain a concrete prohibition or sellability gate.
- Split mixed chunks that combine low-value generic labeling details with high-value gating or prohibition rules.
- Add and maintain few-shot calibration examples for:
  - bare child item vs. minimal parent-scope injection
  - dangling lead-in mismatch
  - low-value labeling group vs. high-value inspection/gating group

## P2

### Storage Evolution Candidate

- Evaluate a JSONL + SQLite hybrid model.
- Keep JSONL for reviewability, diffability, and handoff artifacts.
- Consider SQLite later for task status, retries, dedup, and query-heavy orchestration.
- Do not replace the markdown-first subagent execution path with SQLite-backed raw JSON inputs.
