#!/usr/bin/env python3
"""Production analysis for Enterprise B filling lines.

Queries the Timebase historian HTTP API, computes throughput, yield, time utilization,
and production vs. target from raw cumulative counters and work order data.
Returns compact JSON to stdout for consumption by AI agents.

Usage:
    python3 scripts/calculate_oee.py --line "Enterprise B/Site1/fillerproduction/fillingline01" --shift last
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta


def parse_args():
    parser = argparse.ArgumentParser(description="Production analysis for a filling line")
    parser.add_argument("--line", required=True,
                        help="ISA-95 path to filling line, e.g. 'Enterprise B/Site1/fillerproduction/fillingline01'")
    parser.add_argument("--shift", default="last", choices=["last", "current", "day", "night"],
                        help="Shift to analyze (default: last)")
    parser.add_argument("--start", default=None,
                        help="ISO 8601 start time (overrides --shift)")
    parser.add_argument("--end", default=None,
                        help="ISO 8601 end time (overrides --shift)")
    parser.add_argument("--historian", default="http://localhost:4511",
                        help="Historian base URL")
    parser.add_argument("--dataset", default="Virtual Factory",
                        help="Dataset name")
    return parser.parse_args()


def resolve_shift(shift_name):
    """Resolve shift name to (start, end) ISO 8601 timestamps.

    Shift boundaries (UTC):
      Day shift:   06:00 – 18:00
      Night shift: 18:00 – 06:00 (next day)
    """
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


def shift_label(start_str):
    """Determine shift label from start time."""
    dt = datetime.fromisoformat(start_str)
    return "day" if dt.hour == 6 else "night"


def query_historian(base_url, dataset, tag_names, start, end):
    """Query the Timebase historian for multiple tags over a time range."""
    params = [("tagname", t) for t in tag_names]
    params.append(("start", start))
    params.append(("end", end))
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    url = f"{base_url}/api/datasets/{urllib.parse.quote(dataset)}/data?{query}"

    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        return None, str(e)

    result = {}
    for tag_data in data.get("tl", []):
        name = tag_data["t"]["n"]
        points = [p for p in tag_data.get("d", []) if "v" in p]
        result[name] = points

    return result, None


def get_delta(points):
    """Get delta value for a cumulative counter (last - first)."""
    if not points:
        return None
    if len(points) == 1:
        return 0.0
    return points[-1]["v"] - points[0]["v"]


def get_latest(points):
    """Get the most recent value."""
    if not points:
        return None
    return points[-1]["v"]


def main():
    args = parse_args()

    if args.start and args.end:
        start, end = args.start, args.end
    else:
        start, end = resolve_shift(args.shift)

    line = args.line

    # --- Tags to query ---

    # Cumulative time counters (delta = seconds in each state during the shift)
    time_tags = {
        "timerunning": f"{line}/metric/input/timerunning",
        "timeidle": f"{line}/metric/input/timeidle",
        "timedownplanned": f"{line}/metric/input/timedownplanned",
        "timedownunplanned": f"{line}/metric/input/timedownunplanned",
    }

    # Cumulative production counters (delta = units during the shift)
    count_tags = {
        "countinfeed": f"{line}/metric/input/countinfeed",
        "countoutfeed": f"{line}/metric/input/countoutfeed",
        "countdefect": f"{line}/metric/input/countdefect",
    }

    # Instantaneous rates (latest value)
    rate_tags = {
        "rateactual": f"{line}/metric/input/rateactual",
        "ratestandard": f"{line}/metric/input/ratestandard",
    }

    # Work order data (latest value)
    wo_tags = {
        "wo_number": f"{line}/workorder/workordernumber",
        "wo_product": f"{line}/workorder/lotnumber/item/itemname",
        "wo_actual": f"{line}/workorder/quantityactual",
        "wo_target": f"{line}/workorder/quantitytarget",
        "wo_defect": f"{line}/workorder/quantitydefect",
        "wo_uom": f"{line}/workorder/uom",
    }

    all_tags = list(time_tags.values()) + list(count_tags.values()) + list(rate_tags.values()) + list(wo_tags.values())

    # Query historian
    data, err = query_historian(args.historian, args.dataset, all_tags, start, end)
    if err:
        json.dump({"status": "error", "message": f"Historian query failed: {err}"}, sys.stdout, indent=2)
        sys.exit(1)

    # --- Extract raw values ---

    # Time deltas (seconds in each state during shift)
    t_running = get_delta(data.get(time_tags["timerunning"], []))
    t_idle = get_delta(data.get(time_tags["timeidle"], []))
    t_down_planned = get_delta(data.get(time_tags["timedownplanned"], []))
    t_down_unplanned = get_delta(data.get(time_tags["timedownunplanned"], []))

    if t_running is None:
        json.dump({"status": "error", "message": f"No time data for {line}"}, sys.stdout, indent=2)
        sys.exit(1)

    # Default missing time counters to 0
    t_idle = t_idle or 0.0
    t_down_planned = t_down_planned or 0.0
    t_down_unplanned = t_down_unplanned or 0.0

    # Count deltas (units during shift)
    c_infeed = get_delta(data.get(count_tags["countinfeed"], [])) or 0.0
    c_outfeed = get_delta(data.get(count_tags["countoutfeed"], [])) or 0.0
    c_defect = get_delta(data.get(count_tags["countdefect"], [])) or 0.0

    # Rates (instantaneous)
    rate_actual = get_latest(data.get(rate_tags["rateactual"], [])) or 0.0
    rate_standard = get_latest(data.get(rate_tags["ratestandard"], [])) or 0.0

    # Work order
    wo_number = get_latest(data.get(wo_tags["wo_number"], []))
    wo_product = get_latest(data.get(wo_tags["wo_product"], []))
    wo_actual = get_latest(data.get(wo_tags["wo_actual"], []))
    wo_target = get_latest(data.get(wo_tags["wo_target"], []))
    wo_defect = get_latest(data.get(wo_tags["wo_defect"], []))
    wo_uom = get_latest(data.get(wo_tags["wo_uom"], []))

    # --- Compute derived metrics ---

    # Time utilization
    total_time = t_running + t_idle + t_down_planned + t_down_unplanned
    if total_time > 0:
        pct_running = round(t_running / total_time * 100, 1)
        pct_idle = round(t_idle / total_time * 100, 1)
        pct_down_planned = round(t_down_planned / total_time * 100, 1)
        pct_down_unplanned = round(t_down_unplanned / total_time * 100, 1)
    else:
        pct_running = pct_idle = pct_down_planned = pct_down_unplanned = 0.0

    # Throughput (units per hour while running)
    t_running_hours = t_running / 3600.0
    if t_running_hours > 0:
        throughput = round(c_outfeed / t_running_hours, 1)
    else:
        throughput = 0.0

    # Rate efficiency (actual vs standard)
    if rate_standard > 0:
        rate_efficiency = round(rate_actual / rate_standard * 100, 1)
    else:
        rate_efficiency = None

    # Yield (good units out / units in)
    if c_infeed > 0:
        yield_pct = round((c_outfeed - c_defect) / c_infeed * 100, 2)
    else:
        yield_pct = None

    # Work order completion
    if wo_target is not None and wo_target > 0 and wo_actual is not None:
        wo_completion = round(wo_actual / wo_target * 100, 1)
    else:
        wo_completion = None

    # --- Build output ---
    output = {
        "line": line,
        "period": {
            "start": start,
            "end": end,
            "shift": shift_label(start) if not (args.start and args.end) else "custom",
        },
        "time_utilization": {
            "total_seconds": round(total_time, 1),
            "running_seconds": round(t_running, 1),
            "idle_seconds": round(t_idle, 1),
            "planned_down_seconds": round(t_down_planned, 1),
            "unplanned_down_seconds": round(t_down_unplanned, 1),
            "pct_running": pct_running,
            "pct_idle": pct_idle,
            "pct_planned_down": pct_down_planned,
            "pct_unplanned_down": pct_down_unplanned,
        },
        "production": {
            "units_in": round(c_infeed),
            "units_out": round(c_outfeed),
            "defects": round(c_defect),
            "yield_pct": yield_pct,
            "throughput_per_hour": throughput,
            "rate_actual": round(rate_actual, 1),
            "rate_standard": round(rate_standard, 1),
            "rate_efficiency_pct": rate_efficiency,
        },
        "work_order": {
            "number": wo_number,
            "product": wo_product,
            "actual": round(wo_actual) if wo_actual is not None else None,
            "target": round(wo_target) if wo_target is not None else None,
            "defects": round(wo_defect) if wo_defect is not None else None,
            "completion_pct": wo_completion,
            "uom": wo_uom,
        },
        "status": "ok",
    }

    json.dump(output, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
