---
argument-hint: [site-name]
description: Analyze a site's production performance using deterministic scripts that compact raw data into metrics. Demonstrates the Reduce technique — scripts do the computation, the LLM reasons about results.
---

# Analyze Site: $ARGUMENTS

You are analyzing **Enterprise B/$ARGUMENTS** production performance. Your goal is to demonstrate intentional data compaction — deterministic scripts do all the heavy computation (querying raw historian data, computing deltas, deriving percentages) and return compact results. You reason about pre-computed metrics, never about raw data.

## Step 1: Discover Data Range

First, find what time range has data:

```
python3 .claude/skills/shift-report/scripts/discover_data_range.py \
  --site "Enterprise B/$ARGUMENTS"
```

Use the `recommended_start` and `recommended_end` for all subsequent queries.

## Step 2: Get Site Overview (Script Does the Work)

Run the equipment states query — the script internally queries the historian, processes raw equipment state data, and returns a compact site-wide snapshot (~30 lines of JSON):

```
python3 .claude/skills/shift-report/scripts/query_equipment_states.py \
  --site "Enterprise B/$ARGUMENTS" \
  --start {recommended_start} --end {recommended_end}
```

**Teaching moment:** The script just queried the historian, processed raw state data for every piece of equipment at this site, and returned a compact summary. You received ~30 lines of pre-computed results. All the data processing happened inside the script — the context window never saw the raw historian responses.

## Step 3: Per-Line Production Analysis (Where Compaction Really Shines)

For each filling line returned in Step 2, run the production analysis:

```
python3 .claude/skills/shift-report/scripts/calculate_oee.py \
  --line "Enterprise B/$ARGUMENTS/fillerproduction/{line}" \
  --start {recommended_start} --end {recommended_end}
```

**Teaching moment:** This is the core of the Reduce technique. Each `calculate_oee.py` call does the following INSIDE the script — hidden from the context window:
- Queries ~15 raw counter tags from the historian (cumulative values sampled every 10 seconds)
- Over a 12-hour shift, that's ~4,300 readings per tag — roughly **65,000 raw data points per line**
- Computes deltas between consecutive samples to get rates
- Derives percentages: OEE, availability, performance, quality, yield, time utilization
- Returns **~25 lines of JSON** with 6 key derived metrics

You are reasoning about OEE percentages and throughput rates — not doing arithmetic on raw cumulative counters. The script did the math; you interpret the results.

## Step 4: Show the Compaction Ratio

Note for the audience what the scripts just did:
- **Raw data processed by scripts**: Thousands of 10-second-interval readings across multiple tags per line, plus equipment state histories — easily **100,000+ raw data points** for a 3-line site
- **What entered the context window**: ~30 lines from the equipment overview + ~25 lines per line from production analysis = roughly **100 lines of pre-computed metrics**
- **Compaction ratio**: ~1,000:1 — the scripts turned raw historian data into derived metrics before any of it entered the context

The LLM never computed a delta, never calculated a percentage, never parsed a raw counter value. Deterministic scripts handled all of that and returned only what matters for reasoning.

## Step 5: Produce Consolidated Site Summary

Synthesize the compact script outputs into a single site summary:

1. **Site Status** — One sentence: is the site running normally?
2. **Line Performance Table** — One row per line: OEE, throughput, yield, status
3. **Key Observations** — 2-3 bullet points: what's notable, what needs attention
4. **Compaction Summary** — Note the reduction: raw historian data (100K+ data points) → script outputs (~100 lines of metrics) → this summary (~20 lines)

Write the summary to `analyses/site-analysis-$ARGUMENTS-{date}.md`.

**Final teaching moment:** "The scripts did the heavy lifting. They queried raw historian data, processed thousands of 10-second-interval readings, computed deltas and percentages, and returned compact derived metrics. My context window never saw a single raw counter value — only meaningful, pre-computed results ready for interpretation. That's the Reduce technique: deterministic computation outside the context, compact results inside it."
