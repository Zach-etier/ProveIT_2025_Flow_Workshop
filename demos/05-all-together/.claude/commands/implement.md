---
argument-hint: [plan-file-path]
description: Execute an analysis plan step by step. Runs the scripts specified in the plan, assembles the report, and lets hooks validate and stamp the output.
---

# Implement Plan: $ARGUMENTS

You are executing the analysis plan at **$ARGUMENTS**. Follow it step by step.

## Step 1: Read the Plan

Read the plan document at `$ARGUMENTS` completely. Understand:
- The objective (what question we're answering)
- The execution steps (exact commands to run)
- The parallelization notes (what can run concurrently)
- The expected outputs

## Step 2: Read the Referenced Research

Read the research document referenced in the plan to understand the context.

## Step 3: Load Domain Context

Read the reference documents needed to interpret script outputs:
- `.claude/skills/shift-report/references/ENT-B-OPS-005.md` — Report template with 9 required sections
- `.claude/skills/shift-report/references/ENT-B-KPI-001.md` — OEE calculation standard, targets, product catalog
- `.claude/skills/shift-report/references/ENT-B-OPS-010.md` — Operational knowledge base
- `.claude/skills/shift-report/references/ENT-B-QA-012.md` — SPC procedure (if quality analysis is in the plan)

## Step 4: Execute Phase 1 (Data Collection)

Run each script command exactly as specified in the plan. Follow the parallelization notes — if the plan says steps can run in parallel, run them concurrently.

For multi-site analysis: if the plan calls for it, spawn `site-analyzer` subagents for parallel per-site analysis.

Collect all JSON outputs. Do NOT attempt manual calculations — trust the script results.

## Step 5: Execute Phase 2 (Assembly)

Using the collected results and domain context from the reference docs, assemble the output document as specified in the plan.

If the plan calls for a shift handoff report, follow the SKILL.md template:
- Read `.claude/skills/shift-report/SKILL.md` for the full report assembly instructions
- All 9 sections MUST be present (the validation hook will check)
- Section headings MUST match exactly: `## 1. Executive Summary`, `## 2. Safety`, etc.
- Interpret results using the reference documents — don't just recite numbers

**Write the report** to the path specified in the plan. The hooks will:
1. **PreToolUse (validate)**: Check that all 9 mandatory sections are present. If any are missing, the write will be blocked — fix and retry.
2. **PostToolUse (stamp)**: Append a validation timestamp and SHA256 hash to the written file.

## Step 6: Generate HTML (if specified)

If the plan includes an HTML generation step, run:
```
python3 .claude/skills/shift-report/scripts/render_report_html.py \
  --input {markdown_path} --output {html_path}
```

## Step 7: Present Results

Present to the user:
- Path to the analysis output (markdown and HTML if generated)
- Summary of key findings
- Note that the validation hook confirmed all sections and the stamp hook added integrity verification
- Note any deviations from the plan (if any steps produced unexpected results)
