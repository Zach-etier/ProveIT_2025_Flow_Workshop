---
argument-hint: [research-file-path]
description: Create an analysis plan from a research document. Reads the research, determines which scripts to run for which sites/lines, and writes a step-by-step execution plan.
---

# Plan Analysis: $ARGUMENTS

You are creating an execution plan based on the research document at **$ARGUMENTS**.

## Step 1: Read the Research

Read the research document at `$ARGUMENTS` completely. Extract:
- The original question
- Available sites and time windows
- Recommended scripts and their parameters
- Any identified gaps

## Step 2: Read Domain Context

Read these references to understand what the scripts will return and how to interpret results:
- `.claude/skills/shift-report/references/ENT-B-KPI-001.md` — OEE targets and thresholds
- `.claude/skills/shift-report/references/ENT-B-OPS-005.md` — Report structure (9 sections)
- `.claude/skills/shift-report/references/ENT-B-OPS-010.md` — Operational knowledge

## Step 3: Design the Execution Plan

Based on the research, plan the exact script invocations needed. For each step, specify:
- The exact command to run (with full arguments)
- What the output will be used for
- Whether it can run in parallel with other steps

## Step 4: Write the Plan

Write the plan to `analyses/plans/plan-{topic}-{date}.md`:

```markdown
# Analysis Plan: {topic}

## Objective
{What question we're answering}

## Research Reference
{path to research document}

## Analysis Window
- Start: {recommended_start}
- End: {recommended_end}

## Execution Steps

### Phase 1: Data Collection (Parallel)

**Step 1.1: Site Overview — {site}**
```
python3 .claude/skills/shift-report/scripts/query_equipment_states.py \
  --site "Enterprise B/{site}" --start {start} --end {end}
```
Purpose: Get current equipment states and OEE metrics

**Step 1.2: Production Analysis — {site}/{line}**
```
python3 .claude/skills/shift-report/scripts/calculate_oee.py \
  --line "Enterprise B/{site}/fillerproduction/{line}" --start {start} --end {end}
```
Purpose: Get throughput, yield, time utilization for {line}

{repeat for each line}

**Step 1.3: SPC Analysis — {site}/{vat}** (if quality-related)
```
python3 .claude/skills/shift-report/scripts/spc_analysis.py \
  --tag "Enterprise B/{site}/liquidprocessing/mixroom01/{vat}/processdata/process/weight" \
  --start {start} --end {end}
```
Purpose: Check for quality flags on {vat}

{repeat for each vat}

### Phase 2: Assembly

**Step 2.1: Assemble Report**
Combine all Phase 1 results into a shift handoff report following ENT-B-OPS-005.
Required sections: {list the 9 sections}
Output file: `analyses/shift-report-{site}-{date}.md`

**Step 2.2: Generate HTML**
```
python3 .claude/skills/shift-report/scripts/render_report_html.py \
  --input analyses/shift-report-{site}-{date}.md \
  --output analyses/shift-report-{site}-{date}.html
```

## Parallelization Notes
- Steps 1.1, 1.2, 1.3 can run in parallel per site
- If multiple sites: use site-analyzer subagents for isolation
- Phase 2 requires all Phase 1 results

## Validation
- PreToolUse hook will validate all 9 sections before write
- PostToolUse hook will stamp with SHA256 hash after write

## Next Step
Run: `/implement analyses/plans/plan-{topic}-{date}.md`
```

Present the plan path to the user and suggest running `/implement` next.
