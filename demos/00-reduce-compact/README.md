# Demo 00 — Reduce: Persist Context to the Filesystem

**Technique: Reduce** — The context window is ephemeral. When the conversation ends, everything the agent learned disappears. This demo shows how to persist research from the context window to a file on disk, so downstream agents and future sessions can read it instead of repeating the work.

## What This Demo Shows

1. **The problem**: You chat with the agent, ask it to investigate the historian, explore equipment states, check production data. It learns a lot — but all of that knowledge lives only in the context window. Close the session and it's gone. The next agent starts from zero.

2. **The solution**: `/create-research-report` tells the agent to distill everything it's learned in the current conversation into a structured file on disk. Now any future agent or session can read that file and pick up where this one left off — without re-querying the historian or re-reading references.

## Setup

```bash
cd demos/00-reduce-compact
bash ../setup.sh
```

## Demo Flow

### Phase 1: Explore naturally (fill the context window)

Just chat with the agent. Ask it questions about the factory:

```
Tell me about Site1 — what's running, how are the lines performing?
```

```
What do the vat weights look like? Any SPC concerns?
```

```
How does Site1 compare to its OEE targets?
```

The agent will read reference docs, run scripts against the historian, and accumulate findings in its context window. Let it explore — the messier and more organic, the better for the demo.

### Phase 2: Persist the knowledge

Once the agent has explored enough, run:

```
/create-research-report Site1 performance investigation
```

The agent distills everything from its context window into a concise research report on disk. It reports:
- Where it wrote the file
- How many lines (typically ~40-60)
- What sections it captured

### The teaching moment

"The agent just spent 10 minutes exploring the historian, reading docs, running scripts. All of that lives in the context window — which is ephemeral. When this session ends, it's gone. But now we have `analyses/research/research-site1-performance-investigation.md` on the filesystem. Any downstream agent — a report writer, a planner, a shift handoff tool — can read that 50-line file and get the same understanding without repeating the research. That's the Reduce pattern: persist what you've learned so the next agent doesn't start from scratch."

## Key Files

| File | Purpose |
|------|---------|
| `.claude/commands/create-research-report.md` | `/create-research-report` — persists context to disk |
| `.claude/skills/shift-report/SKILL.md` | Shift report skill (gives agent access to scripts + references) |
| `scripts/` → `shared/scripts/` | Analysis scripts the agent can run |
| `references/` → `shared/references/` | Domain knowledge (historian API, OEE standard, etc.) |

## Why This Matters

```
Without persistence:
  Agent A explores historian → learns about Site1 → session ends → knowledge gone
  Agent B explores historian → learns about Site1 → session ends → knowledge gone
  Agent C explores historian → learns about Site1 → ...

With persistence:
  Agent A explores historian → learns about Site1 → /create-research-report → file on disk
  Agent B reads file → already knows about Site1 → does its actual job
  Agent C reads file → already knows about Site1 → does its actual job
```

The file on the filesystem is the bridge between ephemeral context windows.
