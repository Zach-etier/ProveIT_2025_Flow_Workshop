# Demo 05 — All Together: Research → Plan → Implement

**All three techniques combined** — Offload (skills + scripts on filesystem), Reduce (compact script outputs), and Isolate (subagents for parallel analysis) — plus hooks for validation and integrity stamping.

## What This Demo Shows

A full industrial analysis pipeline with three slash commands:
1. `/research` — Discover what data exists (spawns historian-explorer subagent)
2. `/plan` — Design the analysis approach from research findings
3. `/implement` — Execute the plan step by step (hooks validate and stamp)

Each stage produces a document that feeds the next. The human reviews between stages.

## Setup

```bash
cd demos/05-all-together
bash ../setup.sh
```

## Demo Flow

### 1. Research

```
/research How did the day shift perform at Site1?
```

The agent spawns a `historian-explorer` subagent (Isolate) to discover data availability, then writes a research document listing available scripts, tags, and recommended analysis window.

### 2. Plan

```
/plan analyses/research/research-day-shift-site1-2026-02-17.md
```

The agent reads the research, consults reference docs (Offload), and writes a step-by-step execution plan with exact script commands and parallelization notes.

### 3. Implement

```
/implement analyses/plans/plan-day-shift-site1-2026-02-17.md
```

The agent executes each planned step, runs scripts that return compact metrics (Reduce), assembles a 9-section shift report, and writes it. Hooks fire:
- **PreToolUse**: Validates all 9 sections are present (blocks write if not)
- **PostToolUse**: Stamps with timestamp + SHA256 hash

## What to Watch For

1. **Research stage**: The historian-explorer runs in its own context (Isolate), discovers data range, and returns a compact report of what's available.

2. **Plan stage**: The agent reads reference docs ON DEMAND (Offload) to understand OEE targets, report requirements, and operational context — then designs a concrete plan.

3. **Implement stage**: Scripts return pre-computed metrics (Reduce), not raw data. The agent interprets using domain knowledge. Hooks enforce completeness.

4. **Human in the loop**: Between each stage, the presenter reviews the output and decides to proceed. The agent doesn't blindly execute — it researches, proposes, then implements.

## Key Files

| File | Purpose |
|------|---------|
| `.claude/commands/research.md` | `/research` — discover available data |
| `.claude/commands/plan.md` | `/plan` — design analysis approach |
| `.claude/commands/implement.md` | `/implement` — execute the plan |
| `.claude/agents/historian-explorer.md` | Data discovery subagent (read-only) |
| `.claude/agents/site-analyzer.md` | Per-site analysis subagent |
| `.claude/hooks/validate-shift-report.sh` | PreToolUse: validates 9 sections |
| `.claude/hooks/stamp-shift-report.sh` | PostToolUse: SHA256 stamp |
| `.claude/skills/shift-report/SKILL.md` | Full shift report recipe |
| `scripts/` → `shared/scripts/` | Deterministic analysis scripts |
| `references/` → `shared/references/` | Plant procedures and standards |

## Techniques in Action

| Technique | Where It Appears |
|-----------|-----------------|
| **Offload** | Skills, scripts, and references on filesystem — loaded on demand |
| **Reduce** | Scripts return ~25 lines of derived metrics from thousands of raw readings |
| **Isolate** | historian-explorer and site-analyzer run in their own context windows |
| **Hooks** | validate-shift-report.sh blocks incomplete reports; stamp-shift-report.sh adds integrity hash |
