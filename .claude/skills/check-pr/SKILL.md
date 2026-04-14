---
name: check-pr
description: >
  Use when you need to verify a PR is ready to proceed — checks CI status,
  merge conflicts, and review state. Call this after creating a PR, before
  moving to Human Review, and before merging.
---

# Check PR

Verify the PR is healthy before proceeding. Run this at three points:

1. Right after `gh pr create`
2. Before moving the ticket to Human Review
3. Before merging (the `land` skill runs this automatically)

## Step 1: Get PR Number

```bash
PR_NUMBER=$(gh pr view --json number --jq '.number')
echo "PR: $PR_NUMBER"
```

## Step 2: Check Merge Conflicts

GitHub takes a few seconds to compute `mergeable` after a push — poll until it resolves:

```bash
for i in 1 2 3 4 5 6; do
  MERGEABLE=$(gh pr view "$PR_NUMBER" --json mergeable --jq '.mergeable')
  [ "$MERGEABLE" != "UNKNOWN" ] && break
  echo "mergeable=UNKNOWN, waiting..."
  sleep 5
done
echo "mergeable=$MERGEABLE"
```

**If `MERGEABLE` is `CONFLICTING`:** suggest the user run `rebase-latest-master` to resolve, then repeat Step 2.

**If `MERGEABLE` is `MERGEABLE`:** proceed to Step 3.

## Step 3: Check CI Status

```bash
gh pr checks "$PR_NUMBER"
```

| Result                        | Action                                               |
| ----------------------------- | ---------------------------------------------------- |
| All `pass`                    | Proceed                                              |
| Any `pending` / `in_progress` | Wait: `gh pr checks "$PR_NUMBER" --watch`            |
| Any `fail`                    | Fix the failure, push, then repeat Step 2 and Step 3 |

> **HARD STOP:** Do not merge while any check is pending, queued, or running.

## Step 4: Report

Print a summary:

```
PR #<number>: <title>
mergeable:  MERGEABLE ✅  (or CONFLICTING ❌)
CI:         all pass ✅   (or N failing ❌)
ready:      YES / NO
```

If `ready: NO`, stay and fix before returning control.
