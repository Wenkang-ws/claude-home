---
name: rebase-latest-master
description: Use when the user says "rebase", "rebase master", "pull latest master", or explicitly asks to rebase. Do NOT run automatically — only when the user requests it.
---

# Rebase onto Latest Master

**This skill only runs when the user explicitly asks.** Do not invoke it automatically from other skills (create-pr, check-pr, etc.) — suggest it to the user instead and let them decide.

## Step 1 — Fetch and verify

```bash
git fetch origin master --quiet

# Verify local ref actually matches GitHub's HEAD (a second commit may have landed)
REMOTE_SHA=$(git ls-remote origin refs/heads/master | cut -f1)
LOCAL_SHA=$(git rev-parse origin/master)
if [ "$REMOTE_SHA" != "$LOCAL_SHA" ]; then
  echo "origin/master stale — re-fetching"
  git fetch origin master --force --quiet
fi
```

## Step 2 — Rebase

```bash
git rebase origin/master
```

## Step 3 — If conflicts arise

Resolve conflicts directly in each conflicting file, then continue:

```bash
# After resolving each file:
git add <resolved-file>
git rebase --continue
```

If the same files/lines conflict across multiple commits and resolution becomes unwieldy (e.g. one line modified by many commits causing repeated conflicts), abort and use `detangle-commits` skill first, then rebase again:

```bash
git rebase --abort
# Run detangle-commits skill, then retry this skill from Step 1
```

If conflicts **still** cannot be resolved after detangling, abort the rebase and stop. Leave the branch in a clean state and let a human engineer resolve manually. Do not force or guess your way through conflict resolution.

**Never use merge — the repo requires a linear git history.**

## Step 4 — Push

```bash
git push origin HEAD --force-with-lease
```
