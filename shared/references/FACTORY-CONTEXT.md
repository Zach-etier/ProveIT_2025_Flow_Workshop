# Enterprise B Virtual Factory — Context Reference

## Virtual Factory Infrastructure
- **Historian**: Timebase on `localhost:4511` (HTTP API, no auth)
- **Explorer UI**: `localhost:4531`
- **Dataset**: `Virtual Factory` (MQTT tags)
- **MQTT Broker**: `virtualfactory.proveit.services:1883`

## Enterprise B Site Structure (ISA-95 Hierarchy)
```
Enterprise B/
├── Site1/                          # Largest site
│   ├── liquidprocessing/           # Mix rooms + tank storage
│   │   ├── mixroom01/vat01-04/     # Pasteurization vats
│   │   └── tankstorage01/tank01-06/# Storage tanks
│   ├── fillerproduction/           # 3 filling lines
│   │   ├── fillingline01/          # Equipment: washer, filler, caploader
│   │   ├── fillingline02/
│   │   └── fillingline03/
│   ├── packaging/                  # 4 labeler lines
│   │   ├── labelerline01-04/       # Labeler → Packager → Sealer
│   └── palletizing/                # 2 auto + 4 manual palletizers
├── Site2/                          # Mid-size: 2 fillers, 2 labelers, 1 palletizer
└── Site3/                          # Smallest: 1 filler, 1 labeler, 1 manual palletizer
```

## Tag Naming Convention
```
Enterprise B/{Site}/{area}/{line}/{equipment}/metric/{metric}
Enterprise B/{Site}/{area}/{line}/{equipment}/processdata/state/{field}
Enterprise B/{Site}/{area}/{line}/workorder/{field}
```

### Equipment Tag Segments (per filling line)
- `washer` — Bottle washer
- `filler` — Filling machine
- `caploader` — Cap loading/sealing machine

### Key Metric Tags (per equipment)
- `metric/oee` — Overall Equipment Effectiveness (0-1)
- `metric/availability` — Uptime ratio (0-1)
- `metric/performance` — Speed ratio (0-1)
- `metric/quality` — Good units ratio (0-1)
- `metric/input/countinfeed` — Units entering equipment
- `metric/input/countoutfeed` — Units leaving equipment
- `metric/input/countdefect` — Defective units
- `metric/input/rateactual` — Current production rate
- `metric/input/ratestandard` — Target production rate
- `metric/input/timerunning` — Cumulative run time
- `metric/input/timeidle` — Cumulative idle time
- `metric/input/timedownplanned` — Planned downtime
- `metric/input/timedownunplanned` — Unplanned downtime

### Process Data Tags
- `processdata/state/name` — Equipment state ("Running", "Idle", etc.)
- `processdata/state/type` — State type classification
- `processdata/state/code` — Numeric state code
- `processdata/state/duration` — Time in current state
- `processdata/process/weight` — Process weight (vats/tanks)

### Work Order Tags
- `workorder/workordernumber` — e.g., "WO-L03-0964"
- `workorder/lotnumber/lotnumber` — e.g., "L03-0964"
- `workorder/lotnumber/item/itemname` — e.g., "Cola 0.5L 20Pk"
- `workorder/quantityactual` — Units produced
- `workorder/quantitytarget` — Target quantity
- `workorder/quantitydefect` — Defective units
- `workorder/uom` — Unit of measure (e.g., "bottle")

## Historian API (Timebase HTTP)
Base URL: `http://localhost:4511`

### List datasets
`GET /api/datasets`

### List tags
`GET /api/datasets/Virtual%20Factory/tags`
Response: `{"User": [{"n": "tag/path", "t": "System.Double"}, ...]}`

### Read data
`GET /api/datasets/Virtual%20Factory/data?tagname={tag}&relativeStart=-1h`
- Multiple tags: repeat `tagname` parameter
- Time formats: ISO 8601 (`start`/`end`), unix (`unixStart`/`unixEnd`), or relative (`relativeStart`/`relativeEnd`)
- Relative examples: `-1h`, `-30m`, `d` (start of day), `h-2h` (start of hour, 2 hours ago)
- Response: `{"s": "start", "e": "end", "tl": [{"t": {"n": "tag", "t": "type"}, "d": [{"t": "timestamp", "v": value, "q": quality}]}]}`

### URL Encoding for Tag Names
- In the `tagname` query parameter, use **literal `/`** characters (do NOT encode as `%2F`)
- Encode spaces as `%20` (e.g., `Enterprise%20B` not `Enterprise+B`)
- Example: `?tagname=Enterprise%20B/Site1/fillerproduction/fillingline01/filler/processdata/state/name`
- When using Python `urllib.parse.urlencode`, pass `quote_via=urllib.parse.quote` to preserve literal slashes
