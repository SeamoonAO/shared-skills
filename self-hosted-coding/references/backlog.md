# Self-Hosted Coding Backlog

## Timed Soft Pause Integration

- Current status: a portable helper script exists, but true auto-resume still depends on a platform hook, automation, or external orchestrator that can re-inject a follow-up message into the active session.
- Desired end state: when a soft pause expires without user input, the host environment resumes the session with the helper's standardized continuation prompt.
- Constraints:
  - must never apply to hard stops
  - must work without claiming unsupported native timer behavior
  - should keep state outside repo-tracked files during normal runtime
