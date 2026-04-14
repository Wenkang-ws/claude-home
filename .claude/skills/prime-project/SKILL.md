---
name: prime-project
description: Use when starting work on any app or lib in this monorepo, when the user says "prime", "load context", "start work on", or references a project by path like apps/payroll-backend. Loads project-specific conventions and configures session state for downstream skills.
---

# Prime Project

Load project context, conventions, and session state so all downstream skills share a consistent foundation.

## Workflow

1. **Identify the target project** from user input (e.g. "payroll-backend", "apps/payroll-backend")
2. **Load project config** from `$SKILLS_ROOT/prime-project/project-configs/{name}.json`
   - If config not found, tell the user and offer to create one
3. **Read each reference file** listed in the config's `references` array from `$SKILLS_ROOT/prime-project/references/`
4. **Explore key entry points** listed in the config's `entryPoints`:
   - App module — understand module registration
   - Prisma schema — understand data model (skim, don't read every line)
   - Constants directory — understand enums and constants
5. **Check for existing session state** in `$SKILLS_ROOT/prime-project/session-state.md`
   - If it has content and the branch in state matches the current git branch, present it and ask: "There's existing session state for {JIRA ID} on this branch. Keep it or start fresh?"
   - If it has content but the branch doesn't match, or the phase is `ready-to-ship`, it's stale — clear it silently and proceed to step 6
   - If empty or template-only, proceed to step 6
6. **Write initial session state**:

```markdown
# Session State

<!-- Auto-updated by skills. Do not edit manually. Do not commit. -->

## Current State

- **Project**: {projectName from config}
- **JIRA ID**: (none yet)
- **Branch**: {current git branch}
- **Phase**: context-loaded

## Next Steps

Ready to work. Use `start-feature` to begin a ticket.
```

7. **Tell the user**: "Ready to work on {projectName}. To start on a ticket, use `start-feature`."

## Adding New Projects

To support a new project:

1. Create `$SKILLS_ROOT/prime-project/project-configs/{name}.json` following the `payroll-backend.json` structure
2. Create `$SKILLS_ROOT/prime-project/references/{name}/` with condensed convention files
3. No skill changes needed — everything loads dynamically from config
