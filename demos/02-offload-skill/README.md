# Demo 02 — Offload: Skills on Filesystem

**Technique: Offload** — Move domain knowledge out of the prompt and onto the filesystem. The agent loads it on demand via skills, keeping the conversation context lean.

## What This Demo Shows

Instead of cramming instructions, scripts, and reference docs into the prompt, everything lives in `.claude/skills/shift-report/`. When the agent recognizes a shift report request, it reads the SKILL.md recipe and follows it step by step.

**Context cost of this approach:** ~10 lines of user prompt. The skill's instructions, scripts, and references are loaded on demand — they don't consume context until needed.

## Setup

```bash
cd demos/02-offload-skill
bash ../setup.sh   # or: git init . && git add -A && git commit -m "Demo setup"
```

## Demo Prompt

```
Generate a shift handoff report for Enterprise B Site1
```

## What to Watch For

1. **Step 0 — Data range discovery**: The agent runs `discover_data_range.py` first to find WHERE data actually exists, then uses `--start`/`--end` for all subsequent queries. No more "empty data" failures from `--shift last`.

2. **Reference loading**: The agent reads 4 reference documents BEFORE querying data — OEE standards, SPC procedures, operational knowledge, and factory context. This is the domain expertise that makes the report intelligent rather than mechanical.

3. **Deterministic scripts**: Production analysis, SPC analysis, and equipment queries are all handled by Python scripts — not LLM arithmetic. The agent orchestrates; the scripts compute.

4. **9-section report**: The output follows the ENT-B-OPS-005 template exactly because the SKILL.md tells the agent what sections are required and how to interpret data for each one.

## Key Files

| File | Purpose |
|------|---------|
| `.claude/skills/shift-report/SKILL.md` | The recipe — step-by-step instructions |
| `scripts/` → `shared/scripts/` | Symlink to deterministic Python scripts |
| `references/` → `shared/references/` | Symlink to plant procedures and standards |

## Contrast with Demo 01

| | Demo 01 (MCP Bloat) | Demo 02 (Skills) |
|---|---|---|
| **Context at startup** | ~50 tool schemas loaded | Zero — just the user prompt |
| **Domain knowledge** | None | Loaded on demand from SKILL.md |
| **Script execution** | N/A | Deterministic Python scripts |
| **Report quality** | N/A | 9-section structured report |
