---
name: start-feature
description: Use when starting work on a JIRA ticket, when the user says "work on PAYR-1234", "start feature", "begin ticket", "start ticket", or provides a JIRA issue ID to work on. Fetches the ticket from JIRA, assesses readiness, resolves the project, invokes prime-project, creates a branch, and generates an implementation plan. This is the single entry point for the full development workflow.
---

# Start Feature

The entry point for the development workflow. Fetches a JIRA ticket, assesses it, sets up the project context, creates a branch, and generates an implementation plan.

## Workflow

### 1. Get JIRA Issue

**Invoke `get-ticket`** to fetch the ticket from JIRA and assess requirement completeness. If the user already invoked `get-ticket` earlier in this conversation, the ticket data and assessment are already in context — summarize what was found and skip re-fetching.

If `get-ticket` reports the Atlassian MCP is unavailable, fall back to asking the user for the JIRA issue ID and validating the format only:

```
^(PAYR|WS|UP|TN|CARD|NSTRM|OS|NEW|PP|WM)-\d+$
```

If `get-ticket` flags gaps in the requirements, present the assessment and let the user decide whether to proceed. Respect their call.

### 2. Resolve the Project

Determine which local project this ticket belongs to. Scan all config files in `.claude/skills/prime-project/project-configs/` and check each config's `jiraPrefixes` array for the ticket's prefix.

**Priority order:**

1. **User-provided path** — If the user explicitly gave a project path (e.g., `apps/payroll-backend`, `libs/ws-ai-ui`), use that. It overrides auto-detection.
2. **Config match** — If a project config's `jiraPrefixes` contains the ticket's prefix, use its `projectPath`.
3. **Ask** — If no match and no user-provided path, ask which project they're working in.

### 3. Prime the Project

**Invoke `prime-project`** with the resolved project path. This loads project-specific conventions, references, and initializes session state. Prime-project will detect and clear any stale state from a previous workflow.

### 4. Update JIRA Status

First, check whether the Atlassian MCP is connected (look for `mcp__claude_ai_Atlassian__getJiraIssue` in available tools). If it is **not** connected, skip this entire section — JIRA updates are not blocking.

If the Atlassian MCP **is** connected, transition the issue to **In Development** and add a comment:

1. Get the cloud ID via `mcp__claude_ai_Atlassian__getAccessibleAtlassianResources`
2. Fetch available transitions via `mcp__claude_ai_Atlassian__getTransitionsForJiraIssue` for the issue
3. Look for a transition whose `to.name` is `"In Development"` (the transition is typically named "Start Work")
4. If found, execute it via `mcp__claude_ai_Atlassian__transitionJiraIssue`
5. Add a comment: `"Started working on the issue"` via `mcp__claude_ai_Atlassian__addCommentToJiraIssue`

If the transition doesn't exist (e.g., the issue is already in "In Development" or a later status), skip silently — the issue may have been moved manually.

### 5. Branch Setup

Check the current branch:

```bash
git branch --show-current
```

If the current branch already contains the JIRA ID (case-insensitive match), skip creation:

> "Already on branch `{branch}` for this ticket."

Otherwise, create a new branch:

- Derive the username from `git config user.name` (lowercase first name) or the local part of `git config user.email`
- Ask the user for a short description (2-4 words, kebab-case)
- Format: `{user}/{jira-id-lowercase}-{short-description}`
- Example: `gregory/payr-1234-add-processing-period`
- Create: `git checkout -b {branch-name}`

Also check that the JIRA prefix matches one of the `jiraPrefixes` in the loaded project config. If it doesn't match (e.g. `WS-` on payroll-backend which expects `PAYR-`), warn the user but allow it — cross-project tickets happen.

### 6. Create Implementation Plan

Use the project references that prime-project loaded (these vary per project — check the project config's `references` array for what's available). Together with the JIRA ticket context, these form the input for the plan.

**If `superpowers:writing-plans` is available**, invoke it with:

- The JIRA ticket context (from get-ticket's fetch, or what the user provided)
- The project's references as constraints (conventions, patterns, implementation order — whatever the project config lists)

**If `superpowers:writing-plans` is not available**, create the plan directly:

- Break the ticket into ordered implementation steps
- Reference the project conventions loaded by prime-project to ensure the steps follow established patterns
- Write the plan to a `PLAN.md` file in the working directory
- Present the plan to the user for review before proceeding

### 7. Update Session State

Update `.claude/skills/prime-project/session-state.md`:

```markdown
# Session State

<!-- Auto-updated by skills. Do not edit manually. Do not commit. -->

## Current State

- **Project**: {projectName}
- **JIRA ID**: {JIRA-ID}
- **Branch**: {branch-name}
- **Phase**: planning

## Next Steps

Begin implementation following the plan. When done, use `commit-changes`.
```

### 8. Tell the User

"Plan created for {JIRA-ID}. Ready to implement. When you're done, use `commit-changes` to commit."
