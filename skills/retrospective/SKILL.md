---
name: retrospective
description: Capture and review user-marked retrospective notes.
disable-model-invocation: true
---

# Retrospective workflow

Activate this workflow when the user explicitly starts a retrospective or marks a note with `#retro`.

- For each `#retro` note, add a separate top-level comment to the relevant pull request as soon as the note arises. Do not wait until the retrospective ends, combine notes into one comment, or use commit messages to store them.
- When the user starts a retrospective, group the recorded notes, compare them with evidence, and decide what to accept, reject, or defer.
- Retrospective notes do not authorize repository changes. Agree on the scope of instruction changes before editing them.
- Prefer correcting an existing instruction that failed to guide behavior over adding a duplicate rule.
- Keep retrospective notes scoped to the current conversation unless the user asks otherwise.
