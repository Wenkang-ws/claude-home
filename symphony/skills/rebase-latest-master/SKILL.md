---
name: symphony-rebase-latest-master
description: Symphony autonomous version of rebase-latest-master — runs automatically without user confirmation
---

# Symphony Rebase Latest Master

Follow all rules in `.claude/skills/rebase-latest-master/SKILL.md`, with these overrides:

- **Run automatically**: do not ask the user for confirmation — proceed immediately
- **Push automatically**: after successful rebase, push with `--force-with-lease` without asking
