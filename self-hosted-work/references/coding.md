# Coding Branch

Use this branch when the current task is primarily software work: code changes, bug fixing, refactoring, tests, scripts, tooling, or deploy-adjacent implementation.

## Branch Rules

- Keep software-specific hard stops active for deploy, release, push, migrations, production data, secrets, environment changes, and major stack shifts.
- Treat introducing or upgrading dependencies, or changing validation/test strategy in a way that expands scope, as pause-worthy consequential ambiguity.
- When a coding task enters a failure state, default to `systematic-debugging` if available; otherwise keep the same root-cause-first discipline manually.
- Before claiming completion, use `verification-before-completion` if available; otherwise run equivalent evidence-first verification manually.
- Prefer conservative local implementation choices over stopping for ordinary coding clarification.
