# Shift Handoff Report — Required Elements

**Document**: ENT-B-OPS-005 Rev 4
**Effective**: 2025-02-01
**Owner**: Director of Operations, Enterprise B
**Review cycle**: Semi-annual

---

## Purpose

Every shift transition requires a structured handoff report. The outgoing shift lead prepares this report for the incoming shift lead. The report ensures continuity of operations, flags active issues, and provides a clear picture of site status.

**The incoming shift lead should be able to read the Executive Summary alone and know the state of the plant.** The remaining sections provide the detail.

## Interpretation Guidance

A good shift report doesn't just recite numbers — it contextualizes them. When writing each section:

- **Compare against what was planned**: Was this a changeover-heavy shift or steady-state? A 3-changeover shift will naturally have lower OEE than a single-product run.
- **Distinguish expected from unexpected**: A filler CIP cycle at the 4-hour mark is routine hygiene. A filler CIP cycle 45 minutes into a batch is worth noting.
- **Cite the reason, not just the number**: "OEE 81%, below 85% target" is useless. "OEE 81% — two 25-minute CIP cycles for the Orange→Cola changeover plus a 7-minute unplanned stop at 14:32" is actionable.
- **Flag what needs action, not what needs reading**: The incoming shift lead needs to know what to DO, not just what happened. Every flag should imply or state a next step.
- **Reference applicable procedures by document number** when citing quality or safety issues (e.g., "per ENT-B-QA-012 Section 4" for SPC escalation).

## Required Sections

The shift handoff report MUST include all nine sections below, in this order.

### 1. Executive Summary

One paragraph summarizing overall shift status. Include:
- Overall production status (on target, ahead, behind) with context on what was running
- Biggest win of the shift (best line performance, completed work order, quality milestone)
- Biggest concern for incoming shift (equipment issue, quality flag, supply constraint, upcoming changeover)

Keep it to 3-4 sentences. **Write this section LAST** — after assembling all other sections, so the summary reflects the full picture.

### 2. Safety

Any safety incidents, near-misses, or safety observations during the shift. If no incidents occurred, state explicitly: "No safety incidents reported this shift."

Safety is always the first operational section — it sets the tone for the handoff.

### 3. Production vs. Target

Per filling line, report:

| Line | Work Order | Product | Actual | Target | Completion % |
|------|-----------|---------|--------|--------|-------------|
| fillingline01 | WO-xxx | Product Name | X,XXX | X,XXX | XX% |

Include units of measure. Flag any line below 90% of target with a brief explanation — but **account for elapsed time**: a work order at 35% completion is not behind if it started 1.5 hours ago on a 4-hour batch. Use the batch duration estimates from ENT-B-KPI-001 Section 7 to assess whether the work order is on pace.

Note the product being run (Orange Soda vs Cola Soda) — the WO prefix indicates the product (L03 = Orange, L04 = Cola).

### 4. OEE Summary

Per filling line, report time utilization and efficiency:

| Line | % Running | % Idle | % Planned DT | % Unplanned DT | Yield | Rate Efficiency | vs. Target |
|------|----------|--------|-------------|----------------|-------|----------------|-----------|
| fillingline01 | XX.X% | XX.X% | XX.X% | XX.X% | XX.X% | XX.X% | Above/Below |

Flag any line below the site OEE target (see ENT-B-KPI-001 Section 6 for site-specific targets and rationale). For flagged lines:
- State the primary OEE loss driver (availability, performance, or quality — it is almost always availability)
- Contextualize against what was happening: number of changeovers, CIP cycles, unplanned stops
- Reference the line's standard rate and whether the batch size explains the time utilization
- Only flag unplanned downtime if it exceeds 5% of the shift OR a single event exceeds 15 minutes

**Remember**: The equipment model has no Idle state for filling lines. Idle % will always be 0%. Do not report this as unusual.

### 5. Quality Flags

Report any quality issues identified during the shift:
- SPC violations (reference procedure ENT-B-QA-012): rule number, tag, timestamp, severity, and whether the violation is an expected batch cycle artifact or a genuine quality concern
- Defect counts — note that filler quality is typically 100%; if defects appear at the filler, that IS noteworthy
- Any quality holds placed
- Customer complaints received

**Critical**: Most SPC violations on vat weight data are expected artifacts of the fill/drain cycle (see ENT-B-QA-012 Sections 4.1–4.3). Only report violations as quality flags if they occur outside of fill/drain phases, or if Rule 4 (alternating pattern) is triggered. Always annotate expected violations with context.

If no quality issues: "No quality flags this shift."

### 6. Equipment Status

Current state of all major equipment at time of handoff:
- Filling lines: filler state, current run duration, any notes
- Mixing vats: state, current batch phase if active, weight if relevant
- Storage tanks: general fill level status

Flag any equipment in:
- Unplanned downtime exceeding 15 minutes (include duration and known cause)
- A pattern of repeated short unplanned stops (e.g., 5+ events in 2 hours — may indicate an emerging issue)
- Degraded performance (running but below standard rate by more than 5%)

**Do not flag**: Normal CIP cleaning cycles, brief unplanned DT events (3-7 min) that resolve automatically, vats in Blocked state (this is a scheduling issue, not an equipment issue — note it but don't flag it).

### 7. Open Work Orders

All active work orders across the site:

| Line | WO Number | Product | Status | Completion % | Est. Time Remaining | Notes |
|------|----------|---------|--------|-------------|--------------------| ------|

Include work orders that are in progress, pending, or recently completed during the shift. Use the batch duration estimates from the OEE standard to estimate time remaining. Note any work orders that completed during the shift as well.

### 8. Upcoming

Items the incoming shift should be aware of:
- Scheduled changeovers (line, estimated time, product transition — e.g., "Line 01 Cola→Orange, expected at ~02:30")
- Planned maintenance windows
- Work orders nearing completion (will need new WO setup)
- Expected deliveries or raw material changes
- Scheduled quality checks or audits
- Any time-sensitive tasks

If nothing is scheduled: "No scheduled activities for incoming shift."

### 9. Notes for Incoming Shift

Free-form section for anything that doesn't fit the categories above:
- Observations about process behavior (e.g., "Line 03 rate slightly below normal after last CIP — monitoring")
- Warnings about known issues being monitored
- Ongoing investigations
- Communication from management or other departments
- Anything the incoming shift lead needs to know

## Format Requirements

- Use markdown with clear section headers
- Use tables for production, OEE, and work order data
- Use bullet points for quality flags and equipment notes
- Lead with the most actionable information in each section
- Include timestamps where relevant (use 24-hour format)
- Reference applicable procedure numbers when citing quality or safety issues
