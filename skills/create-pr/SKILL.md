---
name: create-pr
description: Use when the user says "create PR", "open pull request", "land this", "ship it", or wants to submit their work for review. Composes a PR with the correct title format, background section, and work items diff.
---

# Create PR

Create a pull request with correct title format, structured body, and pre-push quality checks.

## Gathering Context

1. Read `.claude/skills/prime-project/session-state.md` for:
   - **JIRA ID** — if not found, ask the user
   - **Branch name** — if not found, get from `git branch --show-current`
   - **Project name** — to load the project config

2. Read `.claude/skills/prime-project/project-configs/{project-name}.json` for:
   - **commitScope** — used as the PR title scope

3. If neither is available, ask the user for scope and JIRA ID directly. The skill works standalone.

## PR Title

Format: `type(scope): description [JIRA-ID]`

Same format as commit messages. The PR title **must** match this format or CI will fail (`lint-pr.yml` validates it).

## PR Body

````markdown
## Background

{Description of what was introduced and changed — draft this from the commits and ask user to confirm}

Issue ref: JIRA-ID

## Work items

\```diff

- Added ...

* Removed ...
  ~ Updated ...
  \```
````

**Rules:**

- **Background**: Summarize changes from `git log master..HEAD` and `git diff master...HEAD`. Present to the user for confirmation before creating the PR.
- **Issue ref**: JIRA ID on its own line (GitHub auto-links to Jira)
- **Work items**: Use diff block with `+` additions, `-` removals, `~` modifications

## Pre-Push Checklist

Before creating the PR, ask the user to confirm:

1. **Rebased onto master?** — If not, offer to rebase (but only if the user asks)
2. **Unit tests pass?** — Remind them of the command from the project config
3. **Integration tests pass?** — Same
4. **Coverage adequate for new code?**

If the user says no to any, ask them to complete it first. Do **not** proceed without confirmation.

**Rebase** (only if user explicitly asks): read `.claude/skills/rebase-latest-master/SKILL.md` and follow its steps.

## Creating the PR

````bash
gh pr create --title "type(scope): description [JIRA-ID]" --body "$(cat <<'EOF'
## Background

{confirmed description}

Issue ref: JIRA-ID

## Work items

\```diff
{work items}
\```
EOF
)"
````

## Post-Creation

- Show the PR URL to the user
- Update the **Phase** field in `.claude/skills/prime-project/session-state.md` to `ready-to-ship`

### Update JIRA Status

First, check whether the Atlassian MCP is connected (look for `mcp__claude_ai_Atlassian__getJiraIssue` in available tools). If it is **not** connected, skip this entire section — JIRA updates are not blocking.

If the Atlassian MCP **is** connected, transition the issue to **Reviewing** and add a comment:

1. Get the cloud ID via `mcp__claude_ai_Atlassian__getAccessibleAtlassianResources`
2. Read the JIRA ID from session state (or the one confirmed earlier in this workflow)
3. Fetch available transitions via `mcp__claude_ai_Atlassian__getTransitionsForJiraIssue` for the issue
4. Look for a transition whose `to.name` is `"Reviewing"` (the transition is typically named "Review")
5. If found, execute it via `mcp__claude_ai_Atlassian__transitionJiraIssue`
6. Add a comment: `"Issue in review"` via `mcp__claude_ai_Atlassian__addCommentToJiraIssue`

If the transition doesn't exist (e.g., the issue is already in "Reviewing" or a later status), skip silently — the issue may have been moved manually.

### Next Step

- Suggest: "To notify the team for review, use `notify-review`."
