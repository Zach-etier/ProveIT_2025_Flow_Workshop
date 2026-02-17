---
description: Analyze all 3 Enterprise B sites in parallel using isolated subagents, then merge results into a cross-site comparison. Demonstrates the Isolate technique.
---

# Multi-Site Analysis

Analyze all three Enterprise B sites in parallel using isolated subagents, then merge results into an enterprise-wide comparison.

## Step 1: Discover Data Range

Find the available data window:
```
python3 .claude/skills/shift-report/scripts/discover_data_range.py \
  --site "Enterprise B/Site1"
```

Use the `recommended_start` and `recommended_end` for all site analyses.

## Step 2: Spawn Site Analyzers in Parallel

Using the Task tool, spawn **3 site-analyzer subagents in parallel** — one for each site. Each agent gets its own isolated context window.

For each site (Site1, Site2, Site3), spawn a `site-analyzer` agent with this prompt:

```
Analyze Enterprise B/{site_name} for the period {recommended_start} to {recommended_end}.

The site path is "Enterprise B/{site_name}".
Start time: {recommended_start}
End time: {recommended_end}
```

**IMPORTANT:** Spawn all 3 agents in a single message (parallel tool calls). Do NOT run them sequentially.

**Teaching moment for the audience:** Each subagent runs in its own context window. Site1's data doesn't compete with Site2's data for context space. If Site3 has an anomaly, the agent analyzing it can focus deeply without being distracted by Site1 and Site2's normal operations.

## Step 3: Merge Results

After all 3 subagents return, merge their summaries into a cross-site comparison:

### Enterprise B — Cross-Site Comparison

| Metric | Site1 | Site2 | Site3 |
|--------|-------|-------|-------|
| Overall Status | ... | ... | ... |
| Average OEE | ... | ... | ... |
| Total Lines | 3 | 2 | 1 |
| Lines Meeting Target | ... | ... | ... |
| Key Concern | ... | ... | ... |

### Enterprise Summary
- **Best performing site:** [site] — [why]
- **Needs attention:** [site] — [why]
- **Enterprise-wide OEE:** [weighted average]

### Per-Site Details
[Include the compact summaries from each subagent]

## Step 4: Write Report

Write the merged enterprise analysis to:
```
analyses/enterprise-analysis-{date}.md
```

**Final teaching moment:** Three sites analyzed in parallel, each in its own isolated context. The merge step combines ~60 lines of summarized findings. If we had done this sequentially in one context, we'd have loaded raw data for all 3 sites simultaneously — more data competing for the same attention budget.
