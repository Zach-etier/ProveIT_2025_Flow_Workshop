# Demo 04 — Isolate: Subagents

**Technique: Isolate** — Give each unit of work its own context window. Subagents analyze one site each in parallel, so data from Site1 doesn't compete with Site2 for the agent's attention.

## What This Demo Shows

The `/multi-site-analysis` command spawns 3 subagents in parallel — one per Enterprise B site. Each subagent:
1. Runs in its own isolated context window
2. Loads only the reference docs it needs
3. Queries only its assigned site's data
4. Returns a compact summary (~20 lines)

The orchestrator merges the 3 summaries into a cross-site comparison.

## Setup

```bash
cd demos/04-isolate
bash ../setup.sh
```

## Demo Prompt

```
/multi-site-analysis
```

## What to Watch For

1. **Parallel spawning**: All 3 site-analyzer agents launch simultaneously (look for parallel Task tool calls)

2. **Context isolation**: Each agent has ~200K tokens of context for just ONE site's data. In a single-agent approach, all 3 sites would share that same 200K — a third of the attention budget per site.

3. **Compact handoff**: Each agent returns ~20 lines of summary. The orchestrator works with ~60 lines total, not thousands of raw data points from all 3 sites.

4. **Cross-site comparison**: The merged table shows enterprise-wide patterns that no single-site analysis would reveal.

## Key Files

| File | Purpose |
|------|---------|
| `.claude/agents/site-analyzer.md` | Per-site analysis subagent definition |
| `.claude/commands/multi-site-analysis.md` | Orchestrator command that spawns 3 agents |
| `.claude/skills/shift-report/SKILL.md` | Full shift report skill (also available) |
| `scripts/` → `shared/scripts/` | Shared analysis scripts |
| `references/` → `shared/references/` | Shared domain knowledge |

## The Isolation Pattern

```
Orchestrator (main context)
  ├── Task: site-analyzer (Site1)  ← own context window
  ├── Task: site-analyzer (Site2)  ← own context window
  └── Task: site-analyzer (Site3)  ← own context window
        ↓ each returns ~20 lines
Orchestrator merges → enterprise summary
```

Without isolation, one agent handles all 3 sites sequentially in a single context — data accumulates, context fills, attention degrades. With isolation, each site gets full context depth.
