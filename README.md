# claude-home

Private configuration repo for Claude Code. Contains global instructions, autonomous agent system (Symphony), and shared skills.

> **Not for public sharing** — contains personal preferences, team-specific skills, and pointers to internal tooling.

## Structure

```
~/.claude/
  CLAUDE.md          — Global Claude Code instructions (language, autonomous mode detection)
  WORKFLOW.md        — Symphony agent workflow template (injected into each agent session)
  skills/            — Shared skills usable by both interactive and Symphony sessions
  symphony/          — Symphony autonomous agent system (see symphony/README.md)
  memory/            — Persistent memory across Claude sessions (auto-managed)
```

## Setup

### 1. Clone this repo

```bash
git clone git@github.com:Stupidism/claude-home.git ~/.claude
```

> If `~/.claude` already exists (Claude Code creates it on first run), move or merge it first:
> ```bash
> mv ~/.claude ~/.claude.bak
> git clone git@github.com:Stupidism/claude-home.git ~/.claude
> cp -n ~/.claude.bak/settings.json ~/.claude/  # restore local settings if needed
> ```

### 2. Install Symphony dependencies

```bash
cd ~/.claude/symphony && npm install
```

### 3. Add secrets

```bash
cp ~/.claude/symphony/secrets.env.example ~/.claude/symphony/secrets.env
# Edit secrets.env and fill in LINEAR_API_KEY
```

### 4. Configure your assignee ID

Edit `~/.claude/symphony/config/symphony.json` and set `assigneeId` to your Linear user ID.

---

## Skills

Skills live in `~/.claude/skills/`. Each skill is a Markdown file read by the agent at runtime.

- **Interactive skills** (called via Skill tool in Claude Code): `commit-changes`, `create-pr`, `start-feature`, etc.
- **Symphony skills** (called autonomously): `linear`, `read-and-plan`, `setup-worktree`, `validate`, etc.
- Some skills (e.g. `deploy-mfe`, `debug-mfe`) are shared and work in both modes.

---

## What's gitignored

Runtime data, caches, and secrets are excluded — see `.gitignore`. The `settings.json` (Claude Code local settings) is also excluded since it's machine-specific.
