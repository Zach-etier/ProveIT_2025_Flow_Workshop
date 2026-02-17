#!/usr/bin/env python3
"""Discover available data range for a site in the historian.

Queries the Timebase historian HTTP API to find the earliest and latest data
points for a site's primary OEE tag, then recommends an analysis window.
Returns compact JSON to stdout for consumption by AI agents.

Usage:
    python3 scripts/discover_data_range.py --site "Enterprise B/Site1"
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta


SITE_FIRST_LINE = {
    "Site1": "fillingline01",
    "Site2": "fillingline01",
    "Site3": "fillingline01",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Discover available data range for a site")
    parser.add_argument("--site", required=True,
                        help="ISA-95 site path, e.g. 'Enterprise B/Site1'")
    parser.add_argument("--historian", default="http://localhost:4511",
                        help="Historian base URL")
    parser.add_argument("--dataset", default="Virtual Factory",
                        help="Dataset name")
    return parser.parse_args()


def identify_site(site_path):
    """Extract site name from path like 'Enterprise B/Site1'."""
    parts = site_path.rstrip("/").split("/")
    return parts[-1]


def query_historian(base_url, dataset, tag_name, start, end):
    """Query the historian for a single tag over a time range."""
    params = [
        ("tagname", tag_name),
        ("start", start),
        ("end", end),
    ]
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    url = f"{base_url}/api/datasets/{urllib.parse.quote(dataset)}/data?{query}"

    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        return None, str(e)

    for tag_data in data.get("tl", []):
        if tag_data["t"]["n"] == tag_name:
            return [p for p in tag_data.get("d", []) if "v" in p], None

    return [], None


def recommend_window(earliest_ts, latest_ts):
    """Recommend a 12-hour analysis window containing the most recent data.

    Snaps to shift boundaries (06:00 or 18:00 UTC). Returns the shift
    that contains the latest data point.
    """
    latest = datetime.fromisoformat(latest_ts).astimezone(timezone.utc)

    # Find which shift the latest data falls in
    if latest.hour >= 18:
        # Night shift starting today
        shift_start = latest.replace(hour=18, minute=0, second=0, microsecond=0)
        shift_end = shift_start + timedelta(hours=12)
    elif latest.hour >= 6:
        # Day shift today
        shift_start = latest.replace(hour=6, minute=0, second=0, microsecond=0)
        shift_end = shift_start + timedelta(hours=12)
    else:
        # Night shift that started yesterday
        shift_start = (latest - timedelta(days=1)).replace(
            hour=18, minute=0, second=0, microsecond=0)
        shift_end = shift_start + timedelta(hours=12)

    return shift_start.isoformat(), shift_end.isoformat()


def main():
    args = parse_args()

    site_name = identify_site(args.site)
    if site_name not in SITE_FIRST_LINE:
        json.dump({
            "status": "error",
            "message": f"Unknown site: {site_name}. Expected: {list(SITE_FIRST_LINE.keys())}",
        }, sys.stdout, indent=2)
        sys.exit(1)

    first_line = SITE_FIRST_LINE[site_name]
    probe_tag = f"{args.site}/fillerproduction/{first_line}/metric/oee"

    # Query the last 30 days to find data boundaries
    now = datetime.now(timezone.utc)
    start_30d = (now - timedelta(days=30)).isoformat()
    end_now = now.isoformat()

    points, err = query_historian(args.historian, args.dataset, probe_tag, start_30d, end_now)
    if err:
        json.dump({
            "status": "error",
            "message": f"Historian query failed: {err}",
        }, sys.stdout, indent=2)
        sys.exit(1)

    if not points:
        json.dump({
            "site": args.site,
            "status": "no_data",
            "message": f"No data found for {probe_tag} in the last 30 days",
            "tag_probed": probe_tag,
        }, sys.stdout, indent=2)
        sys.exit(0)

    earliest = points[0]["t"]
    latest = points[-1]["t"]
    rec_start, rec_end = recommend_window(earliest, latest)

    output = {
        "site": args.site,
        "earliest": earliest,
        "latest": latest,
        "recommended_start": rec_start,
        "recommended_end": rec_end,
        "data_points_sampled": len(points),
        "tag_probed": probe_tag,
        "status": "ok",
    }

    json.dump(output, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
