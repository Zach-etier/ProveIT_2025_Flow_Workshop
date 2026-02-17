# Demo 03 — Reduce: Data Compaction

**Technique: Reduce** — Don't put raw data into the context window. Purpose-built scripts do the heavy computation internally — querying raw readings, computing deltas, deriving percentages — and return only compact, pre-computed results. The agent reasons about metrics, never about raw data.

## What This Demo Shows

The `/analyze-site` command demonstrates intentional data compaction — the scripts are the star:

1. **Script-level compaction** — Each script internally processes thousands of raw 10-second-interval readings and returns ~25 lines of derived metrics. OEE percentages, throughput rates, yield calculations — all computed by the script, not the LLM.
2. **Computational offloading** — The LLM never does arithmetic on raw counter values. Deltas, averages, percentages, and statistical analysis all happen inside deterministic Python scripts.
3. **Layered reduction** — Each stage in the pipeline reduces data volume by 10-100x. The context window only ever sees the final compact output.

## Setup

```bash
cd demos/03-reduce
bash ../setup.sh
```

## Demo Prompt

```
/analyze-site Site1
```

## What to Watch For

1. **Step 2 — Site overview**: The `query_equipment_states.py` script internally queries the historian, processes raw equipment state data, and returns a compact ~30-line JSON snapshot. All the computation is hidden from the context window — the agent receives pre-digested results.

2. **Step 3 — Per-line production analysis**: Each `calculate_oee.py` call is where the real compaction happens. The script internally queries ~15 raw counter tags (cumulative values sampled every 10 seconds over a 12-hour shift = thousands of readings), computes deltas between samples, derives percentages and rates, and returns 6 key metrics in ~25 lines of JSON. The agent never sees a single raw counter value.

3. **Step 4 — Compaction visible**: The agent shows what the scripts did — how many raw data points were processed vs. how many lines of output the context window received. This makes the reduction ratio visible to the audience.

4. **Step 5 — Consolidated summary**: The agent synthesizes the compact script outputs into a single site summary. This is the final reduction: multiple script results consolidated into one coherent narrative.

## Key Files

| File | Purpose |
|------|---------|
| `.claude/commands/analyze-site.md` | The `/analyze-site` command — scripted compaction pipeline |
| `.claude/skills/shift-report/SKILL.md` | Full shift report skill (also available) |
| `scripts/` → `shared/scripts/` | Deterministic compaction scripts (the workhorses) |
| `references/` → `shared/references/` | Domain knowledge for interpretation |

## The Compaction Chain

```
Historian (3,456 tags, 10-sec intervals, 12-hour shift)
  ↓ Scripts query raw data internally
Scripts process thousands of raw readings
  ↓ Compute deltas, percentages, derived metrics
JSON output (~25 lines per analysis)
  ↓ Agent synthesizes across lines
Site summary (~20 lines)
```

Each stage reduces data volume by 10-100x. The context window only ever sees the bottom of this chain — no raw counter values, no 10-second samples, just meaningful metrics ready for interpretation.
