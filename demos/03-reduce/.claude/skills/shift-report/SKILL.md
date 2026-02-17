---
name: shift-report
description: Generate a shift handoff intelligence report for an Enterprise B beverage bottling site. Orchestrates production analysis scripts, SPC analysis, and historian queries to produce a structured report. Use when user says "/shift-report", "shift report", or asks for a shift handoff report.
---



# Shift Handoff Intelligence Report

Generate a comprehensive shift handoff report for an Enterprise B beverage bottling site.

## Parameters
- `site`: Site to report on (Site1, Site2, or Site3). Default: Site1

## Bundled Resources

This skill includes:
- `scripts/discover_data_range.py` — Discovers available data time range in the historian
- `scripts/calculate_oee.py` — Production analysis: throughput, yield, time utilization, work order progress
- `scripts/spc_analysis.py` — SPC analysis with Western Electric Rules
- `scripts/query_equipment_states.py` — Equipment states, vat states, and line-level OEE metrics
- `scripts/render_report_html.py` — Renders markdown report to styled HTML
- `references/ENT-B-KPI-001.md` — OEE calculation standard: formulas, site targets, product catalog, line speed matrix, equipment state model, changeover characteristics
- `references/ENT-B-QA-012.md` — SPC procedure: Western Electric Rules, expected vs concerning violations for batch processes, vat-specific operational notes, escalation paths
- `references/ENT-B-OPS-005.md` — Report structure requirements with interpretation guidance for each section
- `references/ENT-B-OPS-010.md` — Operational knowledge base: per-line characteristics, known equipment behaviors, vat quirks, packaging notes, data artifacts
- `references/FACTORY-CONTEXT.md` — Virtual factory infrastructure, ISA-95 site hierarchy, tag naming conventions, Historian API reference

All paths below are relative to this skill's directory: `.claude/skills/shift-report/`

## Instructions

### Step 0: Discover Available Data Range [SELECT]

Before querying production data, determine what time range has data:
```
python3 .claude/skills/shift-report/scripts/discover_data_range.py \
  --site "Enterprise B/{site}"
```
Use the `recommended_start` and `recommended_end` from the output for ALL subsequent script calls. Always use `--start` and `--end`, never `--shift`.

If the script returns `"status": "no_data"`, inform the user that no historian data is available for the requested site and stop.

### Step 1: Load Context Documents [SELECT]

Read the following reference documents in this skill's directory. These provide the domain knowledge needed to interpret the data — without them, the report will be mechanically correct but operationally useless.

1. **Read `references/ENT-B-OPS-005.md`** — This is your report template. It defines the 9 required sections AND provides interpretation guidance on how to contextualize findings (not just recite numbers).

2. **Read `references/ENT-B-KPI-001.md`** — This tells you how OEE is calculated, the site-specific targets and WHY they differ, the product catalog and line speed matrix, batch size planning, the equipment state model, and changeover characteristics. You need this to understand whether a number is good or bad and why.

3. **Read `references/ENT-B-OPS-010.md`** — This is the operational knowledge base. It contains per-line characteristics, known equipment behaviors, vat quirks, and data artifacts to watch for. This is the "tribal knowledge" that turns a data dump into an intelligent report.

4. **Read `references/FACTORY-CONTEXT.md`** — This provides the virtual factory infrastructure, ISA-95 site hierarchy, tag naming conventions, and Historian API details needed to query data and understand tag paths.

### Step 2: Identify Lines and Equipment [SELECT]

Using the tag hierarchy in `references/FACTORY-CONTEXT.md`, identify all filling lines and quality-relevant process tags for the specified site:
- Site1: fillingline01, fillingline02, fillingline03 (vat01–vat04)
- Site2: fillingline01, fillingline02 (vat01–vat02)
- Site3: fillingline01 (vat01)

### Step 3: Production Analysis [COMPRESS]
For each filling line identified in Step 2, run the bundled production analysis script:
```
python3 .claude/skills/shift-report/scripts/calculate_oee.py --line "Enterprise B/{site}/fillerproduction/{line}" --start {recommended_start} --end {recommended_end}
```
Collect the JSON results. Do NOT attempt to calculate throughput, yield, or utilization manually — the script handles all arithmetic and historian queries.

The script returns: time utilization breakdown (% running, idle, planned/unplanned downtime), production counts (in/out/defects), yield %, throughput per hour, rate efficiency, and current work order progress.

**Interpret the results using the OEE standard and operations notes:**
- Consult the OEE standard (Section 6) for this site's target OEE and the rationale behind it. Flag lines below target, but always explain WHY — reference the number of changeovers, cleaning cycles, or unplanned events that contributed.
- Consult the OEE standard (Section 7) to identify the product from the work order prefix and assess whether the batch is on pace using the batch duration estimates.
- Consult the OEE standard (Section 8) for the equipment state model — remember there is no Idle state for fillers.
- Consult the operations notes for line-specific characteristics. For example, Site1/L03 normally has higher planned downtime than other lines; Site2/L01 normally has high state transition frequency; Site3/L01 has a lower performance baseline.

### Step 4: SPC Analysis [COMPRESS]
Run the bundled SPC analysis on process weight tags for the site's vats:
```
python3 .claude/skills/shift-report/scripts/spc_analysis.py --tag "Enterprise B/{site}/liquidprocessing/mixroom01/{vat}/processdata/process/weight" --start {recommended_start} --end {recommended_end}
```
Run this for each vat at the site (Site1: vat01–vat04, Site2: vat01–vat02, Site3: vat01).

**Read `references/ENT-B-QA-012.md` to interpret violations.** This is critical:
- Most Western Electric Rule violations on vat weight data are **expected artifacts** of the fill/drain cycle (Rules 1, 2, 3 during fill or drain phases). The SPC procedure (Sections 4.1–4.3) explains exactly which violations are expected and which are concerning.
- Only report violations as quality flags if they meet the criteria in the SPC procedure — violations during fill/drain phases should be annotated as expected, not escalated.
- Rule 4 (alternating pattern) on vat data IS always concerning and should be flagged.
- Consult the SPC procedure Section 9 for vat-specific operational notes (e.g., Site1/vat03's high peak weight variation is recipe variation, not a control problem).
- Storage tank SPC is not meaningful for quality monitoring (Section 6 of the SPC procedure).

### Step 5: Equipment & Operational Context [SELECT]
Query the historian for additional context on each filling line:
Run the bundled equipment state query script:
```
python3 .claude/skills/shift-report/scripts/query_equipment_states.py --site "Enterprise B/{site}" --start {recommended_start} --end {recommended_end}
```
The script queries all equipment states, vat states, and line-level OEE metrics for the specified site. It returns compact JSON with current state of each piece of equipment.

**Interpret using the operations notes:**
- Consult the site-specific section of the operations notes for known equipment behaviors. Don't flag something that the operations notes describe as normal (e.g., Site2/L01's high transition frequency, manual palletizer low OEE).
- Check vat states against the batch cycle sequence in the SPC procedure — a vat in "Blocked" is a scheduling signal, not a quality issue.
- Production rates (current vs. standard) are already in the Step 3 output.

### Step 6: Assemble and Write Report
Using the handoff checklist as the template, assemble the shift report with these 9 mandatory sections. **Section headings MUST follow the numbered format exactly** (e.g., `## 1. Executive Summary`) — a validation hook checks for all 9 sections before allowing the file to be written:

1. `## 1. Executive Summary` — Write this LAST. Synthesize the key findings: overall production status with context on what was running, biggest win, biggest concern for incoming shift.
2. `## 2. Safety` — "No safety incidents reported" (no safety tags in this historian)
3. `## 3. Production vs. Target` — Table with per-line work order, product (identified from WO prefix per OEE standard Section 7), actual/target, completion %. Assess whether WOs are on pace using batch duration estimates.
4. `## 4. OEE Summary` — Table with per-line time utilization: % running, % idle, % planned down, % unplanned down, yield, rate efficiency. Flag lines below site target WITH root cause context. Reference the OEE standard for targets and the operations notes for line-specific expectations.
5. `## 5. Quality Flags` — SPC violations with context from the SPC procedure. Distinguish expected batch-cycle artifacts from genuine quality concerns. Cite the procedure document number and escalation path for any real violations.
6. `## 6. Equipment Status` — Current state of all major equipment, contextualized using operations notes. Flag issues per the criteria in the handoff checklist.
7. `## 7. Open Work Orders` — Active work orders across all lines, with product identification and estimated time remaining.
8. `## 8. Upcoming` — Note any information about next shift (if available from context)
9. `## 9. Notes` — Observations, concerns, anything the incoming shift lead needs to know. Reference operations notes for context on any anomalies observed.

Format as clean markdown with tables where appropriate. Lead with the most actionable information.

**Write the completed report** to `analyses/shift-report-{site}-{date}.md` (e.g., `analyses/shift-report-Site1-2026-02-09.md`). The validation hook will check that all 9 sections are present — if any are missing, the write will be blocked and you will receive feedback listing the missing sections. Fix the content and retry the write.

### Step 7: Generate HTML Report
After the markdown report is written successfully, generate the styled HTML version:
```
python3 .claude/skills/shift-report/scripts/render_report_html.py \
  --input analyses/shift-report-{site}-{date}.md \
  --output analyses/shift-report-{site}-{date}.html
```
Present both file paths to the user:
- Markdown: `analyses/shift-report-{site}-{date}.md`
- HTML: `analyses/shift-report-{site}-{date}.html`
