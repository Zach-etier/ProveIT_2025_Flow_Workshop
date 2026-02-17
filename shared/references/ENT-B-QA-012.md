# SPC Procedure — Process Weight Monitoring

**Document**: ENT-B-QA-012 Rev 2
**Effective**: 2025-03-01
**Owner**: Quality Director, Enterprise B
**Review cycle**: Annual

---

## 1. Scope

This procedure governs statistical process control monitoring of `processdata/process/weight` tags on mixing vats and storage tanks during active batches. It applies to all Enterprise B sites.

### Equipment Covered

| Site | Vats | Storage Tanks |
|------|------|---------------|
| Site1 | mixroom01/vat01 through vat04 | tankstorage01/tank01 through tank06 |
| Site2 | mixroom01/vat01 through vat02 | tankstorage01/tank01 through tank03 |
| Site3 | mixroom01/vat01 | tankstorage01/tank01 through tank02 |

### Tag Paths

```
Enterprise B/{Site}/liquidprocessing/mixroom01/{vat}/processdata/process/weight
Enterprise B/{Site}/liquidprocessing/tankstorage01/{tank}/processdata/process/weight
```

## 2. Vat Batch Cycle

Every vat follows a deterministic state sequence:

```
Idle → Fill → Mix → Pasteurize → Cool → Transfer → CIP → Idle
```

A **Blocked** state may occur between Cool and Transfer when the downstream storage tank is not ready to receive product. Blocked events are a scheduling/capacity signal, not a quality concern.

### Typical Cycle Timing

| Phase | Avg Duration | Range | Notes |
|-------|-------------|-------|-------|
| Idle | 32 min | 7–99 min | Highly variable — depends on batch scheduling |
| Fill | 20 min | 3–42 min | Weight increases at a constant rate per vat |
| Mix | 21 min | 5–36 min | Weight is constant (no historian data points recorded) |
| Pasteurize | 16 min | 11–20 min | Most consistent phase. Weight constant except ~1% evaporation loss at transition |
| Cool | 7 min | 0.1–14 min | Weight constant |
| Transfer | 15 min | 0.2–27 min | Weight decreases at constant rate as product drains to storage tank |
| CIP | 14 min | 9–22 min | Weight drops to zero during clean-in-place |
| Blocked | 16 min (when it occurs) | 6–20 min | Only occurs when downstream tank is unavailable |

**Full cycle time**: ~125 min (Fill through CIP) + variable Idle = ~155–160 min total

### Weight Behavior During Phases

**Critical for SPC interpretation:**

- **During Fill**: Weight increases monotonically at a constant rate. All data points trend upward.
- **During Mix, Pasteurize, Cool**: Weight is perfectly constant. The historian's deadband compression records **zero data points** during these phases because there is no change to report. Absence of data during hold phases is normal, not a data gap.
- **During Transfer/CIP**: Weight decreases monotonically at a constant rate to zero.
- **At Pasteurize→Cool transition**: A one-time weight loss of ~0.7–1.7% occurs, modeling evaporation during heat treatment. Average evaporation loss is ~1.1% per batch. This is expected and is not a quality excursion.

### Batch Size Reference

| Site/Vat | Observed Batch Range (kg) | Typical Peak | Notes |
|----------|--------------------------|-------------|-------|
| Site1/vat01 | 10,800–11,000 | ~10,900 | Most consistent batch sizes (CV 1.3%) |
| Site1/vat02 | 14,660–15,810 | ~15,240 | Highest throughput vat on Site1; only Site1 vat to experience Blocked states |
| Site1/vat03 | 11,130–15,140 | ~13,140 | Highest batch-to-batch variation (CV 15.3%) — different batches use different fill targets |
| Site1/vat04 | ~13,090 | ~13,090 | Limited observations |
| Site2/vat01 | 11,210–14,540 | ~12,880 | Experienced longest Idle period (99 min) and 20 min Blocked event |
| Site2/vat02 | ~15,710 | ~15,710 | Slowest fill rate (50 kg/step) but achieves large batches |
| Site3/vat01 | 10,910–11,280 | ~11,100 | Fastest fill rates (269–329 kg/min), most consistent operation (CV 1.7%) |

**Note**: The previously documented typical batch range of "5,000–10,000 kg depending on product" (Rev 1) has been superseded. Observed batch sizes across the enterprise range from 10,900 to 15,800 kg. Control limits should be set based on current observed data, not the legacy range.

## 3. Control Limits

### 3.1 Calculated Limits (default)

When explicit limits are not provided for a specific analysis:
- **Center line (CL)**: Mean of all data points in the analysis period
- **Upper Control Limit (UCL)**: Mean + 3 standard deviations
- **Lower Control Limit (LCL)**: Mean - 3 standard deviations

Zone boundaries for Western Electric Rule evaluation:
- **Zone A**: Between 2 sigma and 3 sigma (either side)
- **Zone B**: Between 1 sigma and 2 sigma (either side)
- **Zone C**: Within 1 sigma of center line

### 3.2 Interpreting Limits on Batch Weight Data

Because vat weight data spans the full 0 kg (empty) to ~15,000 kg (full batch) range within a single analysis window, calculated control limits will be very wide. This is expected — the data inherently includes fill ramps and drain ramps. The calculated limits are meaningful for detecting anomalies relative to the full batch profile, not for monitoring weight stability during a single phase.

**For meaningful process control**, focus SPC analysis on:
1. **Batch-to-batch peak weight variation** — are batch fill targets being met consistently?
2. **Evaporation loss percentage** — is heat treatment process consistent?
3. **Fill rate consistency** — is the fill equipment performing consistently across batches?

## 4. Western Electric Rules

All four rules are checked on every analysis run. Violations are reported with timestamps for correlation with operational events.

### Rule 1 — Point Beyond 3 Sigma
**Condition**: One or more data points beyond the UCL or LCL (outside +/- 3 sigma).
**Severity**: IMMEDIATE ACTION
**Response**: Notify shift supervisor immediately. Place batch on quality hold. Investigate root cause before resuming production.

**Expected false positives on vat weight data**: When the analysis window includes both empty-vat (0 kg) and full-vat (~15,000 kg) data points, the extreme values at the start of fill and end of drain will be statistical outliers from the overall distribution. **These Rule 1 violations are artifacts of the full-cycle data range and do not indicate quality problems.** Annotate as "batch cycle boundary — not a quality excursion" in the shift report.

### Rule 2 — Run of 9
**Condition**: 9 or more consecutive data points on the same side of the center line.
**Severity**: TREND ALERT
**Response**: Notify quality lead within 30 minutes. Indicates a sustained process shift — investigate raw material lot changes, equipment calibration drift, or recipe parameter changes.

**Expected false positives on vat weight data**: During the Fill phase, ALL data points are monotonically increasing and will be on one side of the center line. During Transfer/CIP drain, ALL data points are monotonically decreasing. **Rule 2 violations during fill or drain phases are guaranteed by the physics of the process and do not indicate a process shift.** Annotate as "fill phase — monotonic increase expected" or "drain phase — monotonic decrease expected."

A Rule 2 violation is only meaningful if it occurs during a hold phase (Mix, Pasteurize, Cool) — but note that the historian typically records zero data points during hold phases due to deadband compression, so Rule 2 evaluation during holds is usually not feasible.

### Rule 3 — Trend of 6
**Condition**: 6 or more consecutive data points steadily increasing or steadily decreasing.
**Severity**: TREND ALERT
**Response**: Notify quality lead within 30 minutes. Indicates a process drift — investigate ingredient supply consistency, temperature changes, or pump wear.

**Expected false positives on vat weight data**: Every fill phase produces a continuous monotonic increase. Every drain phase produces a continuous monotonic decrease. **Rule 3 violations during fill or drain phases are inherent to the batch process.** Annotate as "batch fill/drain in progress — trend expected."

### Rule 4 — Alternating Pattern of 14
**Condition**: 14 or more consecutive data points alternating up and down (sawtooth pattern).
**Severity**: PROCESS ALERT
**Response**: Check sensor calibration and wiring. This pattern typically indicates measurement system issues rather than actual process variation.

**This rule should NOT trigger on vat weight data** under normal operation because weight trajectories are monotonic within each phase. A Rule 4 violation on a vat would genuinely indicate sensor noise or control system instability and should be investigated.

## 5. Escalation Path

| Severity | Rule(s) | Action | Timeline |
|----------|---------|--------|----------|
| Immediate Action | Rule 1 (only if NOT a batch cycle boundary) | Line stop + quality hold + supervisor notification | Immediately |
| Trend Alert | Rules 2, 3 (only if NOT during fill/drain phase) | Quality lead investigation | Within 30 minutes |
| Process Alert | Rule 4 | Sensor/calibration check | Within 30 minutes |

If multiple rules trigger simultaneously, escalate to the highest severity. **Always check whether violations correlate with batch phase transitions before escalating** — the majority of SPC violations on vat weight data will be expected artifacts of the fill/drain cycle.

## 6. Storage Tank SPC Considerations

Storage tanks operate as buffers between vats and filling lines. Their weight profile is fundamentally different from vats:
- **Sawtooth pattern**: Weight rises when receiving product from vat transfers, drops when filling lines consume product
- **High inherent variability**: CV of 30–68% is normal for buffer tanks
- **No steady-state hold phase**: Tanks are continuously receiving or dispensing

**SPC analysis on storage tank weights is not meaningful for quality monitoring.** Tank level monitoring is an operational/logistics concern (ensuring filling lines have product supply), not a quality concern. Do not report tank weight SPC violations as quality flags in the shift report.

## 7. Sampling

- Use raw historian data without aggregation for the analysis period.
- Do not downsample or average — every recorded data point is evaluated.
- Minimum 20 data points required for meaningful SPC analysis. If fewer data points are available, report statistics only (no rule evaluation).
- **Be aware of deadband compression**: During constant-weight phases (Mix, Pasteurize, Cool), the historian records zero data points. This is not a data gap — it means the weight was perfectly stable.

## 8. Reporting

SPC results in shift reports should include:
- Number of data points analyzed
- Mean, standard deviation, min, max
- Control limits used (explicit or calculated) and their source
- Any rule violations with: rule number, description, timestamp of triggering point, value, and severity
- **For each violation**: Whether it correlates with a batch phase transition (fill start, drain start, pasteurize transition). If so, annotate it as an expected artifact and do not escalate.
- Recommended action per the escalation table above — only for violations that are NOT expected batch cycle artifacts

## 9. Per-Vat Operational Notes

| Vat | Known Characteristics |
|-----|----------------------|
| Site1/vat02 | Highest throughput vat at Site1. Only Site1 vat that has experienced Blocked states (downstream tank congestion). If a Blocked state is observed, check tank availability — this is a scheduling issue, not a quality issue. |
| Site1/vat03 | Largest batch-to-batch peak weight variation in the enterprise (CV 15.3%). Different batches use different fill targets (11,133 vs 15,141 kg observed). This is a recipe variation, not a control problem. Do not flag peak weight differences on this vat as SPC violations. |
| Site2/vat01 | Has experienced the longest Idle periods (up to 99 min) and occasional extended Blocked events (20 min). Anomalously short Cool phases have been observed (0.3 min) — likely a simulation edge case where the vat was already at target temperature. |
| Site2/vat02 | Slowest fill rate in the enterprise (50 kg/step) but achieves the largest batch sizes. Fill phases take significantly longer than other vats. |
| Site3/vat01 | Fastest fill rates in the enterprise (269–329 kg/min). Most consistent batch sizes (CV 1.7%) and most predictable operation overall. If this vat starts showing inconsistent behavior, it is noteworthy because it normally runs like clockwork. |
