---
name: symphony-create-pr
description: Symphony autonomous version of create-pr — skips all interactive confirmations
---

# Symphony Create PR

Follow all rules in `.claude/skills/create-pr/SKILL.md`, with these overrides:

- **Skip Pre-Push Checklist**: the agent has already run tests and rebased as part of its workflow — proceed directly
- **Draft and submit directly**: do not present the PR background for user confirmation
- **Skip Jira status update**: symphony uses Linear, not Jira — skip that section entirely
