---
name: sync-projects
description: Fetch all Linear projects for a board, match each to a code repo or monorepo sub-path, and generate a wor.local.json projects[] snippet the user can paste in. Run whenever new Linear projects have been created and wor.json does not yet include them.
---

# Sync Linear Projects → wor.local.json

## When to run

Use this skill after a new Linear project is created and you need to add it to
`$SYMPHONY_ROOT/config/boards/wor.local.json` without editing the committed `wor.json`.

---

## Step 1 — Fetch all Linear projects for the board

```bash
LINEAR_API_KEY="${LINEAR_API_KEY:-$(grep LINEAR_API_KEY $SYMPHONY_ROOT/secrets.env | cut -d= -f2)}"
BOARD_FILE="${SYMPHONY_ROOT}/config/boards/wor.json"
TEAM_ID=$(node -e "process.stdout.write(JSON.parse(require('fs').readFileSync('$BOARD_FILE','utf8')).teamId)")

curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"{ team(id: \\\"${TEAM_ID}\\\") { projects { nodes { id name } } } }\"}" \
  | node -e "
    const d = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
    d.data.team.projects.nodes.forEach(p => console.log(p.id, p.name));
  "
```

This prints every project's UUID and name.

---

## Step 2 — Find projects not yet in wor.json or wor.local.json

```bash
# Collect IDs already in the committed config
EXISTING_IDS=$(node -e "
  const base = JSON.parse(require('fs').readFileSync('$BOARD_FILE','utf8'));
  const local = (() => { try { return JSON.parse(require('fs').readFileSync('$BOARD_FILE'.replace('.json','.local.json'),'utf8')); } catch(e) { return {projects:[]}; } })();
  const all = [...(base.projects||[]), ...(local.projects||[])].map(p => p.linearProjectId);
  process.stdout.write(all.join('\n'));
")
echo "Already mapped project IDs:"
echo "$EXISTING_IDS"
```

Compare against the list from Step 1 to identify unmapped projects.

---

## Step 3 — Discover monorepo paths

```bash
MONO_ROOT=$(node -e "
  const base = JSON.parse(require('fs').readFileSync('$BOARD_FILE','utf8'));
  const monoRepo = base.repos.find(r => r.isMono);
  process.stdout.write(monoRepo ? monoRepo.path.replace('~', process.env.HOME) : '');
")

echo "=== apps/ ==="
ls "$MONO_ROOT/apps/" 2>/dev/null | sort

echo "=== libs/ ==="
ls "$MONO_ROOT/libs/" 2>/dev/null | sort
```

---

## Step 4 — Match projects to paths (inference rules)

Apply these rules in order for each unmapped Linear project:

1. **Exact name match** — normalize both sides: lowercase, replace spaces/hyphens/underscores with nothing.
   - `ws-components` → `wscomponents` matches `libs/ws-components` → `wscomponents`
   - `On-Demand Interviews` → `ondemandinterviews` matches `apps/on-demand-interviews` → `ondemandinterviews`

2. **Prefix/substring match** — if the project name is contained in a path segment or vice versa (after normalization).

3. **No match** — mark as `UNMATCHED`; the user must supply the path manually.

For each match, determine:
- Whether the path is under `apps/` (typically `primaryRepo: "workstream-mono"`) or a separate repo
- A one-sentence `hint` describing the sub-app's purpose (read the directory's `README.md` or `project.json` if available)

---

## Step 5 — Read hints from project.json

For each matched app/lib:

```bash
cat "$MONO_ROOT/apps/<name>/project.json" 2>/dev/null | node -e "
  const d = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  console.log(d.name, d.tags);
" || echo "(no project.json)"
```

Use the `name` and `tags` fields to compose a `hint` sentence.

---

## Step 6 — Generate wor.local.json snippet

Print a JSON fragment for each newly matched project:

```jsonc
{
  "projects": [
    // For each matched project:
    {
      "linearProjectId": "<uuid-from-step-1>",
      "name": "<Linear project name>",
      "primaryRepo": "workstream-mono",
      "repos": [
        {
          "name": "workstream-mono",
          "path": "~/Documents/workstream-mono/<apps-or-libs>/<dir-name>",
          "hint": "<one-sentence description of what this sub-app does>"
        }
      ]
    }
    // UNMATCHED projects appear as comments — user fills in the path manually
  ]
}
```

---

## Step 7 — Merge into wor.local.json

If `$SYMPHONY_ROOT/config/boards/wor.local.json` already exists, deep-merge the new entries
(add only projects whose `linearProjectId` is not already present):

```bash
LOCAL_FILE="$SYMPHONY_ROOT/config/boards/wor.local.json"

if [ -f "$LOCAL_FILE" ]; then
  echo "Existing wor.local.json found — append only new project entries."
  echo "Review the generated snippet above, then manually add missing entries."
else
  echo "No wor.local.json yet. Copy wor.local.json.example and paste the snippet above into projects[]."
  echo "Template: $SYMPHONY_ROOT/config/boards/wor.local.json.example"
fi
```

---

## Notes

- `wor.local.json` is gitignored — it is safe to include machine-specific paths or personal API tokens.
- The poller (`poll-linear.mts`) merges `wor.local.json` onto `wor.json` at startup automatically.
- When a project is added to the upstream `wor.json`, you can delete the corresponding entry from your local file to avoid duplication (duplicate entries are harmless but cluttering).
