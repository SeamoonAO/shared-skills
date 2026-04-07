# shared-skills

Shared skills used across Codex and Cursor.

## Included Skills

- `auto-updater`
- `md-reformat`
- `prompt-architect-zh`
- `self-hosted-work`

## Layout

Each skill lives in its own directory and keeps the original skill structure, for example:

```text
skill-name/
  SKILL.md
  agents/
    openai.yaml
```

## Local Integration

Current local setup:

- Codex loads skills from `C:\Users\seamo\.codex\skills`
- Cursor loads skills from `C:\Users\seamo\.cursor\skills-cursor`

Both environments link selected shared skills back to this repository directory:

`D:\Desktop\iCloudDrive\shared-skills`

## Notes

- This repository only stores the shared skills.
- Cursor built-in skills stay local and are not tracked here.

## Quick Start

1. Clone this repository.
2. Pick a skill folder (for example `md-reformat`).
3. Link or copy that folder into your local Codex/Cursor skills directory.
4. Restart the client so the new skill is discovered.

## How to Add a New Skill

When adding a new skill to this repository, keep the same structure:

```text
new-skill/
  SKILL.md
  agents/
    openai.yaml
```

Recommended checklist:

- Use a clear, unique skill directory name.
- Document trigger conditions and workflow in `SKILL.md`.
- Add at least one agent config under `agents/`.
- Update the **Included Skills** section in this `README.md`.

## 维护建议（中文）

- 新增或修改技能后，建议在提交信息里注明影响范围（Codex / Cursor / Both）。
- 尽量保持 `SKILL.md` 中的步骤简洁、可执行，并避免冗余背景说明。
- 如果技能依赖外部工具，请在 `SKILL.md` 中写明前置条件与失败时的回退方案。
