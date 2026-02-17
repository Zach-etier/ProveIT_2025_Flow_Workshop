---
argument-hint: [question about production]
description: Research what data is available to answer a production question. Spawns a historian-explorer subagent to discover tags and data availability.
---

# Research: $ARGUMENTS

You are researching what data is available to answer: **"$ARGUMENTS"**

## Step 1: Parse the Question

Identify from the user's question:
- **Sites involved** — Which Enterprise B sites? (Site1, Site2, Site3, or all)
- **Time scope** — Are they asking about a specific shift, day, or period?
- **Metrics of interest** — OEE? Quality? Equipment status? Production counts?
- **Depth needed** — Quick overview or deep analysis?

## Step 2: Spawn Historian Explorer

Use the Task tool to spawn a `historian-explorer` agent:

```
Discover what data is available to answer this question: "$ARGUMENTS"

Check these sites: {identified sites}
Focus areas: {identified metrics}
```

Wait for the explorer to return its findings.

## Step 3: Assess Coverage

Based on the explorer's findings, determine:
- **What CAN be answered** — Which scripts and tags support the question
- **What CANNOT be answered** — Any gaps in data availability
- **Recommended approach** — Which scripts to run, in what order

## Step 4: Write Research Document

Write a research document to `analyses/research/research-{short-topic}-{date}.md`:

```markdown
# Research: $ARGUMENTS

## Question
$ARGUMENTS

## Data Availability
- Sites with data: {list}
- Analysis window: {start} to {end}
- Available metrics: {list}

## Recommended Analysis Approach

### Scripts to Run
1. `query_equipment_states.py` — Site overview for {sites}
2. `calculate_oee.py` — Per-line production analysis for {lines}
3. `spc_analysis.py` — Quality analysis for {vats} (if quality-related)

### Sites and Lines to Analyze
- {site}: {lines} ({reason})

### Expected Output
- {what the analysis will produce}
- {what questions it will answer}

## Gaps
- {anything that can't be answered with available data}

## Next Step
Run: `/plan analyses/research/research-{short-topic}-{date}.md`
```

Present the research document path to the user and suggest running `/plan` next.
