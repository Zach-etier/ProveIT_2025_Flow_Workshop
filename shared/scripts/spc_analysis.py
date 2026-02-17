#!/usr/bin/env python3
"""SPC analysis with Western Electric Rules for process tags.

Queries the Timebase historian HTTP API and evaluates process data against
Western Electric Rules. Returns compact JSON to stdout for consumption by AI agents.

Usage:
    python3 scripts/spc_analysis.py \
      --tag "Enterprise B/Site1/liquidprocessing/mixroom01/vat01/processdata/process/weight" \
      --shift last
"""

import argparse
import json
import math
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta


def parse_args():
    parser = argparse.ArgumentParser(description="SPC analysis with Western Electric Rules")
    parser.add_argument("--tag", required=True,
                        help="Full tag path to analyze")
    parser.add_argument("--shift", default="last", choices=["last", "current", "day", "night"],
                        help="Shift to analyze (default: last)")
    parser.add_argument("--start", default=None,
                        help="ISO 8601 start time (overrides --shift)")
    parser.add_argument("--end", default=None,
                        help="ISO 8601 end time (overrides --shift)")
    parser.add_argument("--ucl", type=float, default=None,
                        help="Upper control limit (optional, auto-calculated if omitted)")
    parser.add_argument("--lcl", type=float, default=None,
                        help="Lower control limit (optional, auto-calculated if omitted)")
    parser.add_argument("--target", type=float, default=None,
                        help="Target value / center line (optional, uses mean if omitted)")
    parser.add_argument("--historian", default="http://localhost:4511",
                        help="Historian base URL")
    parser.add_argument("--dataset", default="Virtual Factory",
                        help="Dataset name")
    return parser.parse_args()


def resolve_shift(shift_name):
    """Resolve shift name to (start, end) ISO 8601 timestamps."""
    now = datetime.now(timezone.utc)
    today_6am = now.replace(hour=6, minute=0, second=0, microsecond=0)
    today_6pm = now.replace(hour=18, minute=0, second=0, microsecond=0)

    if shift_name == "day":
        return today_6am.isoformat(), today_6pm.isoformat()
    elif shift_name == "night":
        return today_6pm.isoformat(), (today_6am + timedelta(days=1)).isoformat()
    elif shift_name == "current":
        if 6 <= now.hour < 18:
            return today_6am.isoformat(), now.isoformat()
        else:
            if now.hour >= 18:
                return today_6pm.isoformat(), now.isoformat()
            else:
                yesterday_6pm = today_6pm - timedelta(days=1)
                return yesterday_6pm.isoformat(), now.isoformat()
    elif shift_name == "last":
        if 6 <= now.hour < 18:
            yesterday_6pm = today_6pm - timedelta(days=1)
            return yesterday_6pm.isoformat(), today_6am.isoformat()
        else:
            return today_6am.isoformat(), today_6pm.isoformat()


def query_historian(base_url, dataset, tag_name, start, end):
    """Query the Timebase historian for a single tag over a time range."""
    params = [
        ("tagname", tag_name),
        ("start", start),
        ("end", end),
    ]
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    url = f"{base_url}/api/datasets/{urllib.parse.quote(dataset)}/data?{query}"

    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        return None, str(e)

    for tag_data in data.get("tl", []):
        if tag_data["t"]["n"] == tag_name:
            return [p for p in tag_data.get("d", []) if "v" in p], None

    return [], None


def compute_statistics(values):
    """Compute mean, std dev, min, max."""
    n = len(values)
    if n == 0:
        return None
    mean = sum(values) / n
    if n > 1:
        variance = sum((v - mean) ** 2 for v in values) / (n - 1)
        std_dev = math.sqrt(variance)
    else:
        std_dev = 0.0
    return {
        "mean": mean,
        "std_dev": std_dev,
        "min": min(values),
        "max": max(values),
        "count": n,
    }


def check_rule_1(values, timestamps, ucl, lcl):
    """Rule 1: One point beyond 3 sigma (UCL or LCL)."""
    violations = []
    for i, v in enumerate(values):
        if v > ucl or v < lcl:
            violations.append({
                "rule": 1,
                "description": f"Point beyond control limits ({'above UCL' if v > ucl else 'below LCL'})",
                "timestamp": timestamps[i],
                "value": round(v, 2),
                "severity": "immediate_action",
            })
    return violations


def check_rule_2(values, timestamps, center):
    """Rule 2: 9 consecutive points on same side of center."""
    violations = []
    if len(values) < 9:
        return violations

    run_count = 1
    above = values[0] > center

    for i in range(1, len(values)):
        current_above = values[i] > center
        if values[i] == center:
            run_count = 0
            continue
        if current_above == above:
            run_count += 1
        else:
            run_count = 1
            above = current_above

        if run_count >= 9:
            violations.append({
                "rule": 2,
                "description": f"9 consecutive points {'above' if above else 'below'} center line",
                "timestamp": timestamps[i],
                "value": round(values[i], 2),
                "severity": "trend_alert",
            })
            run_count = 0  # Reset to avoid duplicate reporting for extended runs

    return violations


def check_rule_3(values, timestamps):
    """Rule 3: 6 consecutive points steadily increasing or decreasing."""
    violations = []
    if len(values) < 6:
        return violations

    inc_count = 1
    dec_count = 1

    for i in range(1, len(values)):
        if values[i] > values[i - 1]:
            inc_count += 1
            dec_count = 1
        elif values[i] < values[i - 1]:
            dec_count += 1
            inc_count = 1
        else:
            inc_count = 1
            dec_count = 1

        if inc_count >= 6:
            violations.append({
                "rule": 3,
                "description": "6 consecutive points steadily increasing",
                "timestamp": timestamps[i],
                "value": round(values[i], 2),
                "severity": "trend_alert",
            })
            inc_count = 1  # Reset
        elif dec_count >= 6:
            violations.append({
                "rule": 3,
                "description": "6 consecutive points steadily decreasing",
                "timestamp": timestamps[i],
                "value": round(values[i], 2),
                "severity": "trend_alert",
            })
            dec_count = 1  # Reset

    return violations


def check_rule_4(values, timestamps):
    """Rule 4: 14 consecutive points alternating up and down."""
    violations = []
    if len(values) < 14:
        return violations

    alt_count = 1

    for i in range(2, len(values)):
        prev_dir = values[i - 1] - values[i - 2]
        curr_dir = values[i] - values[i - 1]

        if (prev_dir > 0 and curr_dir < 0) or (prev_dir < 0 and curr_dir > 0):
            alt_count += 1
        else:
            alt_count = 1

        if alt_count >= 14:
            violations.append({
                "rule": 4,
                "description": "14 consecutive points alternating up and down",
                "timestamp": timestamps[i],
                "value": round(values[i], 2),
                "severity": "process_alert",
            })
            alt_count = 1  # Reset

    return violations


def main():
    args = parse_args()

    # Resolve time range
    if args.start and args.end:
        start, end = args.start, args.end
    else:
        start, end = resolve_shift(args.shift)

    # Query historian
    points, err = query_historian(args.historian, args.dataset, args.tag, start, end)
    if err:
        json.dump({"status": "error", "message": f"Historian query failed: {err}"}, sys.stdout, indent=2)
        sys.exit(1)

    if not points:
        json.dump({
            "tag": args.tag,
            "period": {"start": start, "end": end},
            "statistics": None,
            "control_limits": None,
            "violations": [],
            "violation_count": 0,
            "status": "ok",
            "message": "No data points in the specified period",
        }, sys.stdout, indent=2)
        print()
        sys.exit(0)

    # Extract values and timestamps
    values = [p["v"] for p in points]
    timestamps = [p["t"] for p in points]

    # Compute statistics
    stats = compute_statistics(values)
    if stats is None:
        json.dump({"status": "error", "message": "Could not compute statistics"}, sys.stdout, indent=2)
        sys.exit(1)

    # Determine control limits
    center = args.target if args.target is not None else stats["mean"]

    if args.ucl is not None and args.lcl is not None:
        ucl = args.ucl
        lcl = args.lcl
        limit_source = "provided"
    else:
        ucl = stats["mean"] + 3 * stats["std_dev"]
        lcl = stats["mean"] - 3 * stats["std_dev"]
        limit_source = "calculated"

    # Check Western Electric Rules
    all_violations = []
    if stats["count"] >= 20:
        all_violations.extend(check_rule_1(values, timestamps, ucl, lcl))
        all_violations.extend(check_rule_2(values, timestamps, center))
        all_violations.extend(check_rule_3(values, timestamps))
        all_violations.extend(check_rule_4(values, timestamps))

    # Summarize by rule, cap detail to first 3 per rule for compact output
    rule_summary = {}
    violations = []
    for v in all_violations:
        r = v["rule"]
        rule_summary[r] = rule_summary.get(r, 0) + 1
        if sum(1 for x in violations if x["rule"] == r) < 3:
            violations.append(v)

    # Build output
    output = {
        "tag": args.tag,
        "period": {"start": start, "end": end},
        "statistics": {
            "mean": round(stats["mean"], 2),
            "std_dev": round(stats["std_dev"], 2),
            "min": round(stats["min"], 2),
            "max": round(stats["max"], 2),
            "count": stats["count"],
        },
        "control_limits": {
            "ucl": round(ucl, 2),
            "lcl": round(lcl, 2),
            "target": round(center, 2),
            "source": limit_source,
        },
        "violations": violations,
        "violation_summary": {f"rule_{r}": c for r, c in sorted(rule_summary.items())},
        "violation_count": len(all_violations),
        "status": "ok",
    }

    if stats["count"] < 20:
        output["message"] = f"Only {stats['count']} data points — minimum 20 required for Western Electric Rule evaluation. Statistics reported only."

    json.dump(output, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
