#!/usr/bin/env python3
"""Query current equipment states and line-level OEE metrics for a site.

Queries the Timebase historian HTTP API for equipment states (filling lines,
vats) and pre-calculated OEE metrics. Returns compact JSON to stdout for
consumption by AI agents.

Usage:
    python3 scripts/query_equipment_states.py --site "Enterprise B/Site1" --shift current
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta


SITE_CONFIG = {
    "Site1": {
        "filling_lines": ["fillingline01", "fillingline02", "fillingline03"],
        "vats": ["vat01", "vat02", "vat03", "vat04"],
    },
    "Site2": {
        "filling_lines": ["fillingline01", "fillingline02"],
        "vats": ["vat01", "vat02"],
    },
    "Site3": {
        "filling_lines": ["fillingline01"],
        "vats": ["vat01"],
    },
}

EQUIPMENT_TYPES = ["washer", "filler", "caploader"]

OEE_METRICS = ["oee", "availability", "performance", "quality"]


def parse_args():
    parser = argparse.ArgumentParser(description="Query equipment states for a site")
    parser.add_argument("--site", required=True,
                        help="ISA-95 site path, e.g. 'Enterprise B/Site1'")
    parser.add_argument("--shift", default="current", choices=["last", "current", "day", "night"],
                        help="Shift to query (default: current)")
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


def query_tags(base_url, dataset, tag_names, start, end):
    """Query the historian for multiple tags. Returns dict of tag_name -> latest value."""
    results = {}

    # Query in batches to avoid URL length issues
    batch_size = 5
    for i in range(0, len(tag_names), batch_size):
        batch = tag_names[i:i + batch_size]
        params = [("tagname", t) for t in batch]
        params.append(("start", start))
        params.append(("end", end))
        query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        url = f"{base_url}/api/datasets/{urllib.parse.quote(dataset)}/data?{query}"

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            for t in batch:
                results[t] = {"value": None, "error": str(e)}
            continue

        for tag_data in data.get("tl", []):
            name = tag_data["t"]["n"]
            points = [p for p in tag_data.get("d", []) if "v" in p]
            if points:
                results[name] = {"value": points[-1]["v"], "timestamp": points[-1]["t"]}
            else:
                results[name] = {"value": None, "error": "no data"}

    return results


def identify_site(site_path):
    """Extract site name from path like 'Enterprise B/Site1'."""
    parts = site_path.rstrip("/").split("/")
    return parts[-1]


def main():
    args = parse_args()

    if args.start and args.end:
        start, end = args.start, args.end
    else:
        start, end = resolve_shift(args.shift)

    site_name = identify_site(args.site)
    if site_name not in SITE_CONFIG:
        json.dump({"status": "error", "message": f"Unknown site: {site_name}. Expected: {list(SITE_CONFIG.keys())}"}, sys.stdout, indent=2)
        sys.exit(1)

    config = SITE_CONFIG[site_name]

    # Build tag lists
    equipment_state_tags = []
    oee_tags = []
    vat_state_tags = []

    for line in config["filling_lines"]:
        for equip in EQUIPMENT_TYPES:
            equipment_state_tags.append(f"{args.site}/fillerproduction/{line}/{equip}/processdata/state/name")
        for metric in OEE_METRICS:
            oee_tags.append(f"{args.site}/fillerproduction/{line}/metric/{metric}")

    for vat in config["vats"]:
        vat_state_tags.append(f"{args.site}/liquidprocessing/mixroom01/{vat}/processdata/state/name")

    all_tags = equipment_state_tags + oee_tags + vat_state_tags

    # Query historian
    raw = query_tags(args.historian, args.dataset, all_tags, start, end)

    # Assemble structured output
    filling_lines = {}
    for line in config["filling_lines"]:
        equipment = {}
        for equip in EQUIPMENT_TYPES:
            tag = f"{args.site}/fillerproduction/{line}/{equip}/processdata/state/name"
            result = raw.get(tag, {"value": None})
            equipment[equip] = result.get("value", None)

        oee_data = {}
        for metric in OEE_METRICS:
            tag = f"{args.site}/fillerproduction/{line}/metric/{metric}"
            result = raw.get(tag, {"value": None})
            val = result.get("value", None)
            if isinstance(val, (int, float)):
                oee_data[metric] = round(val * 100, 1)
            else:
                oee_data[metric] = val

        filling_lines[line] = {
            "equipment_states": equipment,
            "oee_metrics": oee_data,
        }

    vats = {}
    for vat in config["vats"]:
        tag = f"{args.site}/liquidprocessing/mixroom01/{vat}/processdata/state/name"
        result = raw.get(tag, {"value": None})
        vats[vat] = {"state": result.get("value", None)}

    output = {
        "site": args.site,
        "period": {"start": start, "end": end},
        "filling_lines": filling_lines,
        "vats": vats,
        "status": "ok",
    }

    json.dump(output, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
