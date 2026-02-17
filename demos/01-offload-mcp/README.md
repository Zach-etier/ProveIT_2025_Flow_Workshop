# Demo 01 — Offload: MCP Bloat (The Problem)

**Technique: Offload** — This demo shows the *problem* that offloading solves. MCP servers inject tool schemas into the context window at startup, consuming space before the agent even starts working.

## What This Demo Shows

Three MCP servers are configured in `.mcp.json`:
- **filesystem** — File access tools (read, write, list, search, etc.)
- **memory** — Knowledge graph tools (create entities, relations, observations)
- **sequential-thinking** — Structured thinking tools

Each server adds its full tool schema (name, description, parameters, JSON schema) to the context window. Before you type a single character, ~50 tool definitions are already loaded.

## Setup

```bash
cd demos/01-offload-mcp
bash ../setup.sh   # or: git init . && git add -A && git commit -m "Demo setup"
```

**Prerequisite:** Node.js/npm must be available for `npx` to work.

## Demo Flow

1. Launch Claude Code in this directory:
   ```
   claude
   ```
2. Note the MCP server initialization messages — three servers starting up
3. The agent now has ~50 additional tools in context, each with full JSON schemas
4. **Exit** and move to Demo 02 to see the contrast

## What to Watch For

- **Tool count**: Notice how many tools are registered before you do anything
- **Context consumption**: Each tool schema is ~200-500 tokens. 50 tools = 10,000-25,000 tokens consumed at startup
- **No domain knowledge**: Despite all those tools, the agent has zero knowledge about beverage bottling, OEE, SPC, or shift reports
- **The wrong kind of capability**: These tools give the agent generic abilities (file I/O, memory graphs) but not the *specific* knowledge it needs for the task

## Key Point

MCP servers are powerful, but loading them indiscriminately is the opposite of offloading — it's *onloading*. Every tool schema competes for context space with the actual domain knowledge that makes the agent effective.

## Contrast with Demo 02

| | Demo 01 (MCP Bloat) | Demo 02 (Skills) |
|---|---|---|
| **Context at startup** | ~50 tool schemas loaded | Zero — just the user prompt |
| **Domain knowledge** | None | Loaded on demand from SKILL.md |
| **Approach** | Onload everything up front | Offload to filesystem, load on demand |
