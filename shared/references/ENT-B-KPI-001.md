# KPI Standard — Enterprise B Beverage Filling Operations

**Document**: ENT-B-KPI-001 Rev 3
**Effective**: 2025-01-15
**Owner**: VP Manufacturing, Enterprise B
**Review cycle**: Annual

---

## 1. Scope

This standard applies to all filling lines across Enterprise B sites:

| Site | Filling Lines | Combined Standard Rate |
|------|--------------|----------------------|
| Site1 | fillingline01, fillingline02, fillingline03 | 1,095 bpm |
| Site2 | fillingline01, fillingline02 | 460 bpm |
| Site3 | fillingline01 | 180 bpm |

Each filling line consists of three equipment positions: Washer, Filler, and Cap Loader. OEE is tracked at both equipment level and line level. **The filler is the constraining resource on every line** — washer and caploader are not separately metered for OEE purposes. Line-level OEE equals filler OEE.

## 2. OEE Formula

**OEE = Availability x Performance x Quality**

### 2.1 Availability

```
Availability = (Scheduled Time - Downtime) / Scheduled Time
```

Where:
- **Scheduled Time** = `timerunning` + `timeidle` + `timedownunplanned` + `timedownplanned`
- **Downtime** = `timedownunplanned`

Note: `timedownplanned` (scheduled maintenance, changeovers, CIP cleaning) is excluded from the downtime numerator — it reduces scheduled time but is not penalized as lost availability. `timeidle` (line ready but waiting for product or upstream) counts as available time.

**Availability is the dominant OEE driver across all Enterprise B lines**, typically accounting for 80-85% of total OEE loss. Availability generally ranges 0.884–0.899 across lines. Improving availability (reducing unplanned downtime) has far greater OEE impact than improving performance or quality.

### 2.2 Performance

```
Performance = rateactual / ratestandard
```

Capped at 1.0 — overperformance is not credited. If `ratestandard` is zero (line not scheduled), performance is reported as N/A.

Note: Lines typically achieve 97–100% of standard rate when in the Running state. Performance losses are minor (2-3%) and are NOT a significant OEE lever. Actual rates may briefly exceed standard rate by 5-8% during normal operation — this is within tolerance and does not indicate a metering error.

### 2.3 Quality

```
Quality = (countoutfeed - countdefect) / countoutfeed
```

If `countoutfeed` is zero (no production), quality is reported as N/A.

**Quality at the filler is consistently near-perfect (1.000).** Defects at the filling stage are extremely rare — typically zero per shift across all lines. Quality issues are more likely to surface at downstream packaging operations (labelers, packagers) rather than at the filler. When reporting filler quality in the shift report, note that this reflects filling quality only; packaging quality is tracked separately.

## 3. Tag Mapping

All tags follow the ISA-95 path: `Enterprise B/{Site}/fillerproduction/{line}/{equipment}/metric/input/{metric}`

| Variable | Tag Suffix | Type |
|----------|-----------|------|
| Time Running | `metric/input/timerunning` | Cumulative seconds |
| Time Idle | `metric/input/timeidle` | Cumulative seconds |
| Planned Downtime | `metric/input/timedownplanned` | Cumulative seconds |
| Unplanned Downtime | `metric/input/timedownunplanned` | Cumulative seconds |
| Actual Rate | `metric/input/rateactual` | Units/hour (instantaneous) |
| Standard Rate | `metric/input/ratestandard` | Units/hour (target) |
| Count Outfeed | `metric/input/countoutfeed` | Cumulative units |
| Count Defect | `metric/input/countdefect` | Cumulative units |
| Count Infeed | `metric/input/countinfeed` | Cumulative units |

Pre-calculated metrics are also available for validation:
- `metric/oee`, `metric/availability`, `metric/performance`, `metric/quality`

## 4. Line-Level vs. Equipment-Level OEE

- **Equipment-level OEE**: Calculated per equipment (washer, filler, cap loader). Available at `{line}/{equipment}/metric/oee`.
- **Line-level OEE**: The bottleneck equipment's OEE. Available at `{line}/metric/oee`. **Use line-level for shift reports.**

For shift reporting, always reference line-level tags: `Enterprise B/{Site}/fillerproduction/{line}/metric/*`

## 5. Shift Boundaries

| Shift | Start | End |
|-------|-------|-----|
| Day | 06:00 local | 18:00 local |
| Night | 18:00 local | 06:00 local (next day) |

When querying "last shift": if current time is between 06:00–18:00, last shift = previous night (18:00 yesterday to 06:00 today). If current time is between 18:00–06:00, last shift = previous day (06:00 to 18:00 today).

## 6. OEE Targets

| Site | Target OEE | Line Count | Rationale |
|------|-----------|------------|-----------|
| Site1 | 85% | 3 lines | High-volume site. Lines 01 and 02 tend to run dedicated products across multiple work orders with minimal changeovers. Line 03 is the high-speed line (475 bpm) and handles the largest batches (up to 104,000 bottles) but also accumulates the most planned downtime (~33% of total time) due to longer CIP cycles. |
| Site2 | 82% | 2 lines | Mid-volume site. Both lines handle moderate batch sizes (36,000–54,000 bottles) and see more product changeovers than Site1 Lines 01/02. Line 01 has the highest state transition frequency in the enterprise (~21 transitions per 6 hours), indicating more start/stop cycling. |
| Site3 | 78% | 1 line | Low-volume, single-line site. Runs the smallest batches (42,000 bottles) with the most frequent work order turnover (2-3 WO changes per shift). The filler operates at a lower performance ratio (0.971 vs 0.978-0.982 elsewhere), which is a known characteristic of the Site3 filler — it is not a defect. Target accounts for both the higher changeover frequency and the lower performance baseline. |

Any line operating below the site target for a full shift should be flagged in the shift handoff report. **When flagging, always contextualize against what was happening on the line** — a line running below target during a shift with 3 changeovers has a different root cause than a line below target during steady-state production. Check the work order history and equipment state transitions before concluding there is a problem.

## 7. Product Catalog and Line Speed Matrix

Enterprise B produces two beverage SKUs:

| Product | Recipe Code | WO Prefix | Description |
|---------|-----------|-----------|-------------|
| Orange Soda 0.5L | L03 | WO-L03-xxxx | Orange-flavored carbonated beverage, 0.5L bottle |
| Cola Soda 0.5L | L04 | WO-L04-xxxx | Cola-flavored carbonated beverage, 0.5L bottle |

**Identifying product from work order**: The WO prefix indicates the product. `WO-L03-` = Orange Soda, `WO-L04-` = Cola Soda. Lot numbers mirror the WO: `L03-1100` corresponds to `WO-L03-1100`.

### Standard Rates per Line

Both products run at identical speeds on any given line (same bottle format, same fill parameters):

| Line | Standard Rate (bpm) | Hourly Capacity | Speed Tier |
|------|---------------------|-----------------|------------|
| Site1/fillingline01 | 300 | 18,000/hr | Medium |
| Site1/fillingline02 | 320 | 19,200/hr | Medium |
| Site1/fillingline03 | 475 | 28,500/hr | High-speed |
| Site2/fillingline01 | 220 | 13,200/hr | Standard |
| Site2/fillingline02 | 240 | 14,400/hr | Standard |
| Site3/fillingline01 | 180 | 10,800/hr | Compact |

### Batch Size Planning

Batch sizes are calibrated so that wall-clock batch duration clusters at 3–4 hours regardless of line speed:

| Batch Target | Typical Lines | Est. Duration at Standard Rate |
|-------------|--------------|-------------------------------|
| 36,000 | Site2/L02 | ~2.5 hr |
| 42,000 | Site3/L01 | ~3.9 hr |
| 52,000 | Site1/L01, L02, L03 | 1.9–2.9 hr (varies by line speed) |
| 54,000 | Site2/L01 | ~4.1 hr |
| 78,000 | Site1/L01, L02 | ~4.2–4.4 hr |
| 104,000 | Site1/L03 only | ~3.7 hr |

**Interpretation note**: When evaluating work order completion %, account for how long the WO has been running relative to its expected duration. A WO at 35% completion is not behind if it started 1.5 hours ago on a 4-hour batch.

## 8. Equipment State Model

All filler equipment uses a 4-state model:

| State Code | State Name | State Type | Classification | OEE Impact | Typical Duration |
|------------|-----------|------------|----------------|------------|-----------------|
| 0 | Running | Running | Productive | None — counts as running time | 25–45 min avg (highly variable) |
| 306 | Cleaning | PlannedDowntime | Scheduled (CIP) | Reduces scheduled time (not penalized) | 15–28 min typical |
| 300 | Planned Downtime | PlannedDowntime | Scheduled | Reduces scheduled time (not penalized) | 18–124 min (highly variable) |
| 100 | Unplanned Downtime | UnplannedDowntime | Unscheduled | **Penalizes availability** | 3–7 min avg (short events) |

**Important operational characteristics:**
- **No Idle state exists** in the current equipment model. Equipment is always either Running or in some form of downtime. Do not report idle time for filling equipment — it will always be zero.
- **Unplanned downtime events are consistently short** (3–7 minute average) and represent minor faults or jams with quick automatic recovery, not major breakdowns. Multiple short unplanned DT events per shift is normal operating behavior. Only flag unplanned DT if: (a) total unplanned DT exceeds 5% of the shift, or (b) a single event exceeds 15 minutes.
- **Cleaning (code 306) and Planned Downtime (code 300) are separate states**. Both count as planned downtime for OEE purposes but have different operational meanings. Cleaning is a CIP cycle; Planned Downtime covers scheduled maintenance, breaks, and changeover preparation.
- **Running durations between stops are typically 25–45 minutes**, punctuated by brief unplanned DT events. A pattern of Running → Unplanned DT (3-5 min) → Running → Unplanned DT is normal and does not indicate a systemic problem unless the frequency increases significantly above baseline.

## 9. Changeover Characteristics

Product changeovers (Orange Soda ↔ Cola Soda) are logged as Cleaning (CIP) events followed by a new work order.

- **Changeover duration**: Typically 15–28 minutes for the CIP cycle, plus ramp-up time on the new product (first few minutes at reduced rate)
- **Same-product WO changes**: When a work order completes and a new WO for the same product begins, there is usually only a brief Planned Downtime (1-5 min) for WO setup — no CIP required
- **Cross-product changeovers may be coordinated**: Multiple lines have been observed changing from Orange to Cola simultaneously, suggesting enterprise-level production scheduling

When evaluating time utilization, distinguish between:
- **CIP for changeover** (expected, 15-28 min per product transition)
- **CIP for hygiene** (routine, typically every 4-6 hours of continuous running)
- **Planned downtime for maintenance** (variable, 18-124 min)

## 10. Calculation Notes for Cumulative Counters

Time and count tags are cumulative (monotonically increasing). To get the value for a specific period:

```
Period value = Last reading in period - First reading in period
```

Rate tags (`rateactual`, `ratestandard`) are instantaneous — use the most recent value in the period for the performance calculation.

## 11. Known Data Artifacts

- **Historian restart events**: The historian occasionally records quality code `28` entries simultaneously across all tags during connection loss/restart events. These are system artifacts, not production events. Data gaps following these events (typically 30-90 minutes) should be excluded from time utilization calculations.
- **Rate overshoot**: Actual rates may briefly exceed standard rates by 5-8% during normal operation. This does not indicate a metering error — the standard rate is a design target, not a hard limit.
