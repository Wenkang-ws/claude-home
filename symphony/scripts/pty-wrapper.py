#!/usr/bin/env python3
"""
PTY wrapper for Claude Code remote-control sessions.

Allocates a pseudo-terminal so --remote-control registers the session on
claude.ai. Strips ANTHROPIC_API_KEY so Claude uses OAuth auth instead of
API key auth (which bypasses session registration).

Usage:
    python3 pty-wrapper.py <prompt-file> [--session-id <uuid> | --resume <uuid>]

The prompt file is read and deleted immediately after reading.
"""

import pty, os, subprocess, sys, signal, threading, time

prompt = open(sys.argv[1]).read()
os.unlink(sys.argv[1])
session_args = sys.argv[2:]  # ['--session-id', '<uuid>'] or ['--resume', '<uuid>']

env = os.environ.copy()
for key in [
    'ANTHROPIC_API_KEY',
    'CLAUDE_CODE_USE_BEDROCK', 'CLAUDE_CODE_USE_VERTEX', 'CLAUDE_CODE_USE_FOUNDRY',
    'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC', 'DISABLE_TELEMETRY',
]:
    env.pop(key, None)

ticket_id = os.environ.get('TICKET_ID', 'WOR-?')
branch = os.environ.get('BRANCH', '')
slug = branch.replace(f"feat/{ticket_id}-", "", 1)
session_name = f"[{ticket_id}] {slug}"

# Only pass --name when creating a new session (--session-id).
# On resume (--resume), --name causes a duplicate entry in the desktop UI.
is_new_session = '--session-id' in session_args
name_args = ['--name', session_name] if is_new_session else []

# Enable TypeScript LSP plugin so the agent has diagnostics/hover without
# needing to manually re-read type definition files.
_lsp_plugin = os.path.expanduser(
    '~/.claude/plugins/cache/claude-plugins-official/typescript-lsp/1.0.0'
)
lsp_args = ['--plugin-dir', _lsp_plugin] if os.path.isdir(_lsp_plugin) else []

# Load user + project + local settings so permissions.deny, enabledPlugins, etc. apply.
# Use effort=medium to avoid unnecessary extended thinking in autonomous mode.
cmd = (
    ['claude', '--dangerously-skip-permissions', '--remote-control',
     '--setting-sources=user,project,local', '--effort', 'medium']
    + lsp_args + name_args + session_args + [prompt]
)

master_fd, slave_fd = pty.openpty()
proc = subprocess.Popen(
    cmd,
    stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
    env=env, close_fds=True,
)
os.close(slave_fd)


def forward_signal(signum, frame):
    try:
        proc.terminate()
    except Exception:
        pass


signal.signal(signal.SIGTERM, forward_signal)
signal.signal(signal.SIGINT, forward_signal)

# Auto-answer Claude Code's "Do you trust this folder?" prompt, but only when
# the repo root is the home directory (~). In that case, worktrees land in a
# subdirectory of HOME that Claude hasn't seen before, so it always prompts.
# For all other repos the worktree paths are fresh dirs too, but we only
# auto-confirm for the home-dir repo since that's a known-safe self-managed repo.
_repo_root = os.environ.get('REPO_PATH', '')
if os.path.realpath(os.path.expanduser(_repo_root)) == os.path.realpath(os.path.expanduser('~')):
    def _auto_trust():
        time.sleep(2)
        try:
            os.write(master_fd, b'\n')
        except OSError:
            pass
    threading.Thread(target=_auto_trust, daemon=True).start()

# Discard PTY output (visible on claude.ai instead)
# On macOS, os.read returns b'' (EOF) instead of raising OSError when the
# PTY slave closes; check for empty read to avoid an infinite spin loop.
while True:
    try:
        data = os.read(master_fd, 4096)
        if not data:
            break
    except OSError:
        break

proc.wait()
sys.exit(proc.returncode)
