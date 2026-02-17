# Enterprise B — Site Operations Notes

**Document**: ENT-B-OPS-010 (Informal)
**Last updated**: 2025-12-15
**Maintainers**: Site shift leads, CI engineering
**Status**: Living document — updated as operational knowledge evolves

---

This document captures operational knowledge that isn't covered by formal procedures. It reflects patterns, quirks, and lessons learned from running these sites. New shift leads should read this before their first solo shift.

---

## General — All Sites

### Product Identification Shortcut
- **WO-L03** = Orange Soda 0.5L. **WO-L04** = Cola Soda 0.5L. You can identify the product from the work order number alone without querying the item name. Lot numbers mirror the WO prefix: L03-xxxx = Orange, L04-xxxx = Cola.
- Both products run at the same speed on any given line (same 0.5L bottle format). A product changeover does NOT change the standard rate.

### Batch Duration Planning
- Batch sizes are calibrated so that every work order takes roughly 3–4 hours of wall-clock running time regardless of line speed. A 104,000-bottle batch on the high-speed Site1/L03 finishes in about the same time as a 42,000-bottle batch on the slower Site3/L01. Don't compare batch sizes across lines — compare completion percentages against elapsed time.

### Unplanned Downtime Baseline
- Across the enterprise, unplanned downtime runs at 7–9% of total time. This is a systemic baseline, not isolated incidents. Individual events average 3–7 minutes — minor jams and automatic restarts. This is normal. Only escalate if:
  - Total unplanned DT exceeds 10% in a 2-hour window
  - A single event exceeds 15 minutes
  - The same line has 5+ events in rapid succession (possible emerging fault)

### OEE Reality Check
- Enterprise-wide OEE averages about 0.873 (87.3%). This is driven almost entirely by availability losses. Quality at the filler is essentially perfect (zero defects). Performance when running is 97-100% of standard rate. **If someone asks "how do we improve OEE," the answer is always "reduce planned downtime" — not "run faster" or "reduce defects."**

### The No-Idle Model
- The filling equipment state model has no Idle state. Equipment is always Running, Cleaning, Planned DT, or Unplanned DT. Zero idle time is not exceptional — it's how the system is configured. Don't report "zero idle time" as a finding.

---

## Site1 — Largest Site (3 Filling Lines)

### Line 01 (300 bpm — Medium Speed)
- **Steady workhorse**. Tends to run dedicated products across multiple work orders with minimal changeovers. Often assigned Orange Soda for extended runs.
- Best OEE performer at Site1 (typically 0.879). Highest availability (~90%).
- Typical batch sizes: 52,000 or 78,000 bottles (2.9–4.4 hour runs).

### Line 02 (320 bpm — Medium Speed)
- **Weakest OEE at Site1** (typically 0.866). Higher planned downtime than other lines — has shown extended planned DT events up to 124 minutes in recent observations. Investigate if planned DT exceeds 35% of total time in any shift.
- Tends to run Cola Soda for extended periods.
- Higher rate variability than Line 01 (stdev 33 bpm vs 19 bpm). Not a concern — just the nature of this line's operating profile.

### Line 03 (475 bpm — High Speed)
- **The powerhouse**. Fastest line in the enterprise at 475 bpm. Handles the largest batches (up to 104,000 bottles) but finishes them in ~3.7 hours because of the speed.
- Accumulates the most planned downtime in the enterprise (~33% of total time). This is proportional to its throughput — more product = more frequent CIP cycles. Do not flag high planned DT percentage on this line unless it's significantly above its baseline.
- Has the only recorded filler defects in the enterprise (4 cumulative units out of ~1.5M produced). This is statistically negligible but worth noting because all other lines show exactly zero.
- Rate variability is highest (stdev 46 bpm) — this is expected for a high-speed line. Actual rate ranges from ~216 to ~502 bpm during ramp-up/down.
- When Line 03 changes products, it's often coordinated with other lines across the enterprise (observed simultaneous Orange→Cola changeovers on multiple lines).

### Site1 Vats (4 vats)
- **Vat 02** is the highest-throughput vat and the only one that experiences Blocked states (downstream tank congestion). If vat 02 is Blocked, check storage tank availability — it usually clears within 6–20 minutes.
- **Vat 03** has the largest batch-to-batch variation in peak weight (CV 15.3%). This is because it runs different recipe fill targets (11,133 vs 15,141 kg observed). This is NOT a control problem — it's recipe variation. Don't flag peak weight differences on vat 03 as anomalies.
- **Vat 01** is the most consistent: batch sizes cluster tightly around 10,900 kg (CV 1.3%).

### Site1 Storage Tanks (6 tanks)
- Tanks operate as buffers. Some are accumulating (tank02), some are draining (tank03, tank04), some are cycling (tank01, tank05, tank06). This is normal buffer management.
- **Tank02** has the highest peak capacity observed (~20,850 kg). If it's consistently above 18,000 kg, it may be accumulating faster than filling lines are consuming — check if a filling line is down or in planned DT.
- **Tank03** has been observed with zero idle or CIP states — it appears to run continuously.

---

## Site2 — Mid-Size Site (2 Filling Lines)

### Line 01 (220 bpm — Standard Speed)
- **Most "restless" line in the enterprise**: highest state transition frequency (~21 transitions per 6 hours). Frequent start/stop cycling. This is its normal behavior — likely related to upstream product supply timing.
- Handles moderate batch sizes (54,000 bottles, ~4.1 hour runs).
- OEE is consistent with Site2 target (~0.872).

### Line 02 (240 bpm — Standard Speed)
- Has shown the highest unplanned downtime percentage in recent observations (12.3% in one 6-hour window vs the 7-9% enterprise average). **Monitor this line** — if elevated unplanned DT persists across multiple shifts, it may indicate an emerging maintenance need.
- Runs smaller batches (36,000 bottles, ~2.5 hour runs) — fastest work order turnover among medium-speed lines.

### Site2 Vats (2 vats)
- **Vat 01** has experienced the longest Idle periods in the enterprise (up to 99 minutes) and extended Blocked events (20 minutes). It has also shown anomalously short Cool phases (0.3 min). These appear to be timing artifacts rather than quality issues.
- **Vat 02** has the slowest fill rate in the enterprise (50 kg/step) but achieves large batches (~15,710 kg). Fill phases on this vat take notably longer than others.

### Site2 Tanks (3 active)
- **Tank03** has been observed as nearly static (only 2 data points in 24 hours at a constant ~13,476 kg). It may be inactive or in standby. If tank03 shows up as "Running" at a constant weight, this is its normal behavior.

---

## Site3 — Smallest Site (1 Filling Line)

### Line 01 (180 bpm — Compact Speed)
- Single-line site. Slowest line in the enterprise but has shown the highest running time percentage (83.7% in one 6-hour window) due to fewer planned downtime events.
- **Performance ratio is notably lower** (0.971 vs 0.978-0.982 elsewhere). This is a known characteristic of the Site3 filler, not a defect. The site OEE target of 78% accounts for this.
- **Cola specialist**: Only Cola Soda work orders have been observed on this line in 48+ hours of monitoring. May occasionally run Orange but appears to be a dedicated Cola line.
- Runs small batches (42,000 bottles, ~3.9 hour runs) with the most frequent work order turnover (2-3 changes per shift).
- Has shown one anomalously long Cleaning cycle (116 minutes vs the typical 15-28 min). If this recurs, investigate — it may indicate a CIP system issue or a manual override.

### Site3 Vat (1 vat)
- **Vat 01** is the most predictable vat in the enterprise. Fastest fill rates (269-329 kg/min), most consistent batch sizes (CV 1.7% — the tightest in the enterprise). If this vat starts showing inconsistent behavior, pay attention — it normally runs like clockwork.

### Site3 Tanks (2 tanks)
- **Tank01** is the primary buffer, maintaining level between 2,000-14,000 kg. It has been observed with Running state only — no CIP or Idle states recorded in 24h. If it goes to CIP, the single filling line may need to pause.
- **Tank02** has been observed in a draining pattern with relatively low levels. CIP cycles observed.

---

## Packaging Notes (All Sites)

### Labeler Is the Packaging Bottleneck
- On every packaging line, the labeler has the lowest OEE. When the labeler goes down (unplanned DT), the downstream packager and sealer go to Idle (starved). They don't log their own unplanned DT — they just wait. If you see packager/sealer idle, check the labeler first.
- Packaging OEE is significantly lower than filling OEE (0.57-0.79 vs 0.87-0.90). This is expected — packaging involves more mechanical complexity (labels, multi-pack collation, sealing).

### Pack Sizes in the Product Mix
- The packaging lines produce multi-packs from the filled bottles: 4-pack, 6-pack, 16-pack, 20-pack, and 24-pack configurations.
- Packaging work orders add a pack suffix to the filling WO: `WO-L04-0724-P24` = Cola Soda lot 0724, 24-pack format.
- UOM at packaging is "CS" (cases), not "bottle" as at filling.

### Manual Palletizers Are Overflow
- Manual palletizers run at 2-4% OEE and are mostly Idle. This is by design — they are overflow capacity for peak demand. Do not report low manual palletizer OEE as a problem.
- Automated palletizers (Sites 1 and 2) run at >94% OEE and are not a constraint.

---

## Data Artifacts to Be Aware Of

1. **Historian restart events** appear as quality code `28` entries simultaneously across all tags. These create data gaps of 30-90 minutes. The event is a system artifact — not a production event. Do not count this gap as downtime.

2. **Vat hold phase data gaps**: During Mix, Pasteurize, and Cool phases, the historian records zero data points because weight is perfectly constant (deadband compression). This is normal — absence of data during hold phases means the process was stable, not that data was lost.

3. **Rate readings of zero**: When a line is in Planned DT or Cleaning, the rate reads zero. When computing average rates, exclude zero readings to get the "rate while running" figure.
