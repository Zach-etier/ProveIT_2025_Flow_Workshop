# Context Engineering Workshop

## Are you going to FAIL or WIN with AI?

Workshop materials for "Context Engineering: The Key to AI Performance and Reliability" — a live demo showing how three context engineering techniques (Offload, Reduce, Isolate) transform AI from unreliable to production-grade. Presented at ProveIt! 2026 by Zach Etier, VP of Architecture, Flow Software.

The demo runs against a virtual beverage bottling factory (Enterprise B) with ~3,456 live historian tags across 3 sites, using [Claude Code](https://docs.anthropic.com/en/docs/claude-code) as the AI agent platform.

## Quick Start

```bash
git clone https://github.com/flowsoftware/ProveIT_2025_Flow_Workshop.git
cd ProveIT_2025_Flow_Workshop
docker compose up -d        # Start the virtual factory
bash demos/setup.sh         # Initialize demo directories
```

**Prerequisites:**
- Docker / Docker Compose
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
- Anthropic API key (`ANTHROPIC_API_KEY` environment variable)
- Node.js/npm (for Demo 01's MCP servers)

## Workshop Demos

Each demo runs in its own isolated directory. `cd` into the demo folder and launch `claude` there — Claude Code picks up only that directory's `.claude` configuration.

### Demo 01 — Offload: MCP Bloat (The Problem)

```bash
cd demos/01-offload-mcp && claude
```

Three MCP servers load ~50 tool schemas into context at startup — before you even type a prompt. Lots of generic capabilities, zero domain knowledge. This is the problem that offloading solves. See [demo README](demos/01-offload-mcp/README.md).

### Demo 02 — Offload: Skills on Filesystem

```bash
cd demos/02-offload-skill && claude
```

Domain knowledge lives on the filesystem as a **skill** — a SKILL.md recipe, deterministic Python scripts, and reference documents. The agent loads them on demand. A 10-line prompt produces a full 9-section shift report. See [demo README](demos/02-offload-skill/README.md).

**Key insight:** Zero tool schemas in context at startup. Domain expertise offloaded to filesystem, loaded only when needed.

| File | Purpose |
|------|---------|
| [SKILL.md](demos/02-offload-skill/.claude/skills/shift-report/SKILL.md) | The "recipe" — step-by-step instructions |
| [scripts/](shared/scripts/) | Deterministic Python scripts (OEE, SPC, equipment, data range) |
| [references/](shared/references/) | Plant procedures, KPI standards, operational knowledge |

### Demo 03 — Reduce: Compaction

```bash
cd demos/03-reduce && claude
```

The `/analyze-site` command demonstrates intentional compaction — querying only ~50 tags out of ~3,456, with scripts that pre-compute metrics from thousands of raw readings. The context window never sees raw counter data. See [demo README](demos/03-reduce/README.md).

### Demo 04 — Isolate: Subagents

```bash
cd demos/04-isolate && claude
```

The `/multi-site-analysis` command spawns 3 subagents in parallel — one per site. Each gets its own context window so Site1's data doesn't compete with Site2's. Results merge into an enterprise comparison. See [demo README](demos/04-isolate/README.md).

### Demo 05 — All Together: Full Pipeline

```bash
cd demos/05-all-together && claude
```

All three techniques combined, plus hooks for validation. A human-in-the-loop pipeline:

1. `/research How did the day shift perform at Site1?` — discover available data
2. `/plan analyses/research/{file}.md` — design the analysis approach
3. `/implement analyses/plans/{file}.md` — execute, with hooks validating output

See [demo README](demos/05-all-together/README.md).

## Repository Structure

```
ProveIT_2025_Flow_Workshop/
├── README.md                                # You are here
├── docker-compose.yml                       # Virtual factory infrastructure
│
├── shared/                                  # Single source of truth
│   ├── scripts/                             # Deterministic Python scripts
│   │   ├── discover_data_range.py           # Find available data window
│   │   ├── calculate_oee.py                 # Production analysis
│   │   ├── spc_analysis.py                  # SPC with Western Electric Rules
│   │   ├── query_equipment_states.py        # Equipment state snapshot
│   │   └── render_report_html.py            # Markdown → styled HTML
│   └── references/                          # Plant procedures and standards
│       ├── FACTORY-CONTEXT.md               # ISA-95 hierarchy, tag conventions
│       ├── ENT-B-KPI-001.md                 # OEE calculation standard
│       ├── ENT-B-QA-012.md                  # SPC procedure
│       ├── ENT-B-OPS-005.md                 # Report structure requirements
│       └── ENT-B-OPS-010.md                 # Operational knowledge base
│
├── demos/
│   ├── setup.sh                             # Initialize demo git repos
│   ├── teardown.sh                          # Clean up after presentation
│   │
│   ├── 01-offload-mcp/                      # Technique: Offload (MCP bloat)
│   ├── 02-offload-skill/                    # Technique: Offload (skills)
│   ├── 03-reduce/                           # Technique: Reduce (compaction)
│   ├── 04-isolate/                          # Technique: Isolate (subagents)
│   └── 05-all-together/                     # Full pipeline + hooks
│
├── _archive/                                # Old demos preserved for reference
│   ├── 01-PromptEng/
│   ├── 02-ContextEng/
│   └── 03-HarnessEng/
│
└── virtualfactory/                          # Historian + collector configs
```

## The Three Techniques

| Technique | Problem It Solves | Demo |
|-----------|-------------------|------|
| **Offload** | Context window filled with tool schemas and static knowledge | 01 (problem), 02 (solution) |
| **Reduce** | Raw data floods context, degrading reasoning quality | 03 |
| **Isolate** | Multiple tasks compete for the same attention budget | 04 |

## The Virtual Factory

Enterprise B is a simulated multi-site beverage bottling operation:

| Site | Filling Lines | Standard Rate | OEE Target |
|------|--------------|---------------|-----------|
| Site1 | 3 lines | 300–475 bpm | 85% |
| Site2 | 2 lines | 220–240 bpm | 82% |
| Site3 | 1 line | 180 bpm | 78% |

Each site includes liquid processing (mixing vats, storage tanks), filling lines (washer, filler, cap loader), packaging (labelers, packagers, sealers), and palletizing. The historian records OEE metrics, equipment states, work orders, and process data at ~10-second intervals.

Run `docker compose up -d` to start the factory. Data begins flowing immediately. The historian API is at `http://localhost:4511` and the Explorer UI at `http://localhost:4531`.
