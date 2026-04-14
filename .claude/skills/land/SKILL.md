---
name: land
description: >
  Use when the user says "land this", "merge the PR", "ship it", or the PR is approved and
  ready to squash-merge. Handles worktree cleanup, CI check verification, and squash merge.
---

# Land

Squash-merge an approved PR with worktree cleanup and CI verification.

> This is **Check #3 of 3** for PR health (mergeable + CI). The first two checks happen right after `gh pr create` and before Human Review — both via the `check-pr` skill.

## Step 1: Get PR Status

```bash
PR_NUMBER=$(gh pr view --json number --jq '.number')
gh pr view $PR_NUMBER --json number,state,reviewDecision,statusCheckRollup,mergeable
```

**If `state` is `MERGED`:** The PR is already merged. Skip Steps 2 and 4. Go directly to Step 3 (worktree cleanup) then Step 5 (report). Do not attempt to merge again.

**If `state` is `OPEN`:** Requirements before merging:

- `reviewDecision` is `APPROVED` (or user gives explicit consent)
- All required CI checks pass
- No merge conflicts (`mergeable` is `MERGEABLE`)

If any check is failing, investigate and fix before proceeding. Never force-merge to bypass checks.

## Step 2: Resolve Conflicts (if any)

If there are merge conflicts, suggest the user run `rebase-latest-master` to resolve them, then wait for CI to re-run.

## Step 3: Clean Up Worktree

**Must be done before `--delete-branch` or the merge will fail.**

```bash
# Find the worktree path for this branch
git worktree list

# Remove it — use --force because worktrees always contain .claude-session-id
# and a node_modules symlink (both untracked by design)
git worktree remove --force <path>

# If the directory is already gone or was removed manually, prune stale references
git worktree prune
```

## Step 4: Squash Merge

```bash
gh pr merge --squash --delete-branch
```

Verify completion:

```bash
gh pr view --json state,mergedAt
```

## Step 5: Report

Tell the user:

- Merged commit SHA
- PR number and title
- Confirm branch deleted

## Rules

- Never use `--merge` or `--rebase` — always `--squash`
- Never bypass required CI checks
- Always confirm with the user before merging if `reviewDecision` is not `APPROVED`
