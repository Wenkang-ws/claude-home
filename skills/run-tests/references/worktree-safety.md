# Worktree Safety

This reference exists because agents have catastrophically broken worktree environments by switching to master to "verify existing bugs" — running tests there (where no feature changes exist), unstashing changes into master, then declaring tests pass against an empty diff. This must never happen again.

## Detecting Your Environment

```bash
# Am I in a linked worktree? If these differ, YES — you're in a worktree, not the main repo.
GIT_COMMON=$(git rev-parse --git-common-dir)
GIT_DIR=$(git rev-parse --git-dir)
[ "$GIT_COMMON" != "$GIT_DIR" ] && echo "WORKTREE" || echo "MAIN"

# Current worktree path and branch
git rev-parse --show-toplevel     # e.g., /Users/dev/repo.feature-branch
git branch --show-current         # e.g., feature-branch

# All worktrees
git worktree list --porcelain
```

## When You're in a Worktree — Forbidden Actions

These actions are **FORBIDDEN when you are in a linked worktree** (i.e., the detection above shows `WORKTREE`):

| Action                                            | Why it's forbidden                                                  |
| ------------------------------------------------- | ------------------------------------------------------------------- |
| `git checkout master` / `git switch master`       | Corrupts worktree state; runs tests against unchanged code          |
| `cd /path/to/master/worktree`                     | Same as above — you'd be running tests in a different worktree      |
| `git stash` + switch + `git stash pop`            | Contaminates other worktrees with your changes                      |
| "Let me verify on master if this is pre-existing" | This is the exact pattern that caused the disaster. Do NOT do this. |
| Running tests in any directory other than `pwd`   | Tests must run where your changes live                              |

## When You're NOT in a Worktree

If you're on a normal branch in the main repo (detection shows `MAIN`), switching branches is acceptable. You can `git checkout master` to compare, run tests on master, then switch back. The restrictions above only apply to worktree environments.

That said, `git diff master...HEAD` is still the faster approach for checking pre-existing failures — it avoids the overhead of switching and re-running.

## Safe Alternatives (for worktree environments)

**To check if a test failure is pre-existing** (without switching):

```bash
# Check if the failing test file was modified in your branch
git diff master...HEAD -- path/to/failing.spec.ts

# If the diff is EMPTY, the test file hasn't changed — the failure is pre-existing.
# Tell the user: "This test failure appears pre-existing — the test file hasn't changed in this branch."

# If the diff is NOT empty, you changed something — diagnose and fix it.
```

**To see what files you changed**:

```bash
git diff master...HEAD --name-only        # file list
git log master..HEAD --oneline --stat     # commit-by-commit changes
```

**To compare specific code against master**:

```bash
git diff master...HEAD -- path/to/file    # three-dot diff from merge-base
git show master:path/to/file              # view master's version without switching
```

**If the user truly needs master's test results**: Tell them to open a separate terminal in the master worktree and run the tests there. Do not do it yourself.

## Using Worktrunk (`wt`) — If Available

Worktrunk is a CLI for managing git worktrees. Check if it's available before using:

```bash
command -v wt >/dev/null 2>&1 && echo "available" || echo "not available"
```

### Key Commands

```bash
wt list                          # Show all worktrees with status
wt list --format=json            # JSON output for scripting
wt switch <branch>               # Switch to a worktree (use sparingly)
wt switch -                      # Previous worktree (like cd -)
wt switch ^                      # Default branch worktree
```

### When to Use `wt`

- **Listing worktrees**: Always prefer `wt list` over `git worktree list` — it shows richer status info
- **Switching**: Only if the user explicitly asks you to switch worktrees. The `run-tests` skill should NEVER need to switch.

### When `wt` Is Not Available

Fall back to raw git commands:

```bash
git worktree list                # List all worktrees
git rev-parse --show-toplevel    # Current worktree path
```

Do NOT attempt to `git worktree add` or `git worktree remove` without the user's explicit permission.

## Pre-Test Safety Checklist

Before running any test command, verify:

1. ✅ `pwd` matches the worktree path you recorded at the start
2. ✅ `git branch --show-current` matches the branch you recorded
3. ✅ You have NOT run `git checkout`, `git switch`, or `cd` to another worktree
4. ✅ The test command runs from the monorepo root within this worktree

If any check fails, STOP and tell the user what happened.
