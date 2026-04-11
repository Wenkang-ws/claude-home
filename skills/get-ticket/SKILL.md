---
name: get-ticket
description: Use when the user wants to read, review, or triage a JIRA ticket — "get ticket PAYR-1234", "fetch ticket WS-5678", "pull up this ticket", "what's NSTRM-42 about", "grab PAYR-1234", or pastes a JIRA ID with "get this" or "check this ticket". Fetches the full ticket from JIRA via the Atlassian MCP and assesses whether requirements are complete enough to begin coding. This is a read-only skill — it does not create branches or start workflows. Use this whenever someone wants to look at a JIRA ticket, even if they just say "get this" with an ID.
---

# Get Ticket

Fetch a JIRA ticket and assess requirement completeness. This is a read-only operation — no branches, no session state, no downstream workflow. Use `start-feature` to begin the full development workflow.

## Prerequisite — Atlassian MCP

This skill requires the **Atlassian MCP** (`claude.ai Atlassian`) to be connected. Before anything else, check that Atlassian tools are available — specifically `mcp__claude_ai_Atlassian__getJiraIssue`.

If the Atlassian MCP is **not** connected, tell the user:

> "I need the Atlassian MCP to fetch JIRA tickets. Enable it via `/mcp` or your Claude Code settings, then try again."

**Stop here.** Do not attempt to proceed without the Atlassian MCP.

## Workflow

### 1. Parse the Ticket ID

Extract the JIRA issue ID from the user's message. Validate against:

```
^(PAYR|WS|UP|TN|CARD|NSTRM|OS|NEW|PP|WM)-\d+$
```

If no ticket ID was provided, ask for one.

### 2. Fetch from JIRA

Discover the Atlassian cloud ID:

```
mcp__claude_ai_Atlassian__getAccessibleAtlassianResources()
```

Then fetch the issue in markdown format for readability:

```
mcp__claude_ai_Atlassian__getJiraIssue({
  cloudId: <cloud-id>,
  issueIdOrKey: "<JIRA-ID>",
  responseContentFormat: "markdown"
})
```

If the fetch fails, report the error and stop.

### 3. Assess Requirement Completeness

Analyze the ticket and give the user an honest, candid assessment. The goal is to catch problems _before_ coding starts — rework from ambiguous requirements is expensive.

**Check for these two things first:**

- **Description** — Does the ticket have a substantive description beyond just repeating the title?
- **Acceptance criteria** — Are there clear, testable conditions for "done"?

**Then apply a heuristic assessment.** Even if both exist, evaluate whether an engineer could produce correct, complete software from what's written:

- Are the requirements specific enough to code against, or would you need to make assumptions?
- Are there ambiguous terms that different people might interpret differently?
- Are edge cases mentioned, or only the happy path?
- Is it clear what should change and what should stay the same?
- Are there unstated dependencies or prerequisites?

**Present the assessment:**

If the ticket looks solid:

> "This ticket looks ready to work on. [1-2 sentence summary of what it asks for]"

If there are gaps:

> "This ticket has some gaps that could cause rework:
>
> - [specific gap 1]
> - [specific gap 2]
>
> I'd suggest [specific action — e.g., adding acceptance criteria, clarifying X with the reporter] before starting. Want to proceed anyway, or use `start-feature` to begin work regardless?"
