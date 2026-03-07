# shared-skills

Shared skills used across Codex and Cursor.

## Included Skills

- `md-reformat`
- `prompt-architect-zh`

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
