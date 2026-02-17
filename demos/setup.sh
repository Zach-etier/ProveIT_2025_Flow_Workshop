#!/bin/bash
# Run this before the demo to isolate each demo directory as its own project.
# Claude Code uses the git root as the project root, so each demo needs its own
# .git to prevent inheriting the parent repo's .claude configuration.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

DEMO_DIRS=(
    "00-reduce-compact"
    "01-offload-mcp"
    "02-offload-skill"
    "03-reduce"
    "04-isolate"
    "05-all-together"
)

# Verify shared/ directory exists
if [ ! -d "$ROOT_DIR/shared/scripts" ] || [ ! -d "$ROOT_DIR/shared/references" ]; then
    echo "ERROR: shared/scripts or shared/references not found."
    echo "Make sure you're running this from the repository root."
    exit 1
fi

# Verify symlinks resolve for demos that use them
for demo_name in "${DEMO_DIRS[@]}"; do
    demo_dir="$SCRIPT_DIR/$demo_name"
    skill_dir="$demo_dir/.claude/skills/shift-report"

    if [ -d "$skill_dir" ]; then
        if [ -L "$skill_dir/scripts" ] && [ ! -e "$skill_dir/scripts" ]; then
            echo "WARNING: Broken symlink in $demo_name — recreating..."
            rm "$skill_dir/scripts"
            ln -s ../../../../../shared/scripts "$skill_dir/scripts"
        fi
        if [ -L "$skill_dir/references" ] && [ ! -e "$skill_dir/references" ]; then
            echo "WARNING: Broken symlink in $demo_name — recreating..."
            rm "$skill_dir/references"
            ln -s ../../../../../shared/references "$skill_dir/references"
        fi
    fi
done

# Check if historian is reachable
if command -v curl &>/dev/null; then
    if curl -s --connect-timeout 2 http://localhost:4511/api/datasets > /dev/null 2>&1; then
        echo "Historian is running at http://localhost:4511"
    else
        echo "WARNING: Historian not reachable at http://localhost:4511"
        echo "Run 'docker compose up -d' from the repository root first."
    fi
fi

# Initialize git repos
for demo_name in "${DEMO_DIRS[@]}"; do
    demo_dir="$SCRIPT_DIR/$demo_name"
    if [ -d "$demo_dir" ] && [ ! -d "$demo_dir/.git" ]; then
        echo "Initializing git repo in $demo_name..."
        git init "$demo_dir" --quiet
        # Stage files so Claude Code sees a clean working tree
        git -C "$demo_dir" add -A
        git -C "$demo_dir" commit -m "Demo setup" --quiet
    else
        echo "Skipping $demo_name (already initialized or missing)"
    fi
done

echo ""
echo "Done. Each demo directory is now an isolated project."
echo ""
echo "Demo order:"
echo "  0. cd demos/00-reduce-compact && claude    # Persist context to filesystem"
echo "  1. cd demos/01-offload-mcp && claude       # MCP bloat (the problem)"
echo "  2. cd demos/02-offload-skill && claude     # Skills on filesystem"
echo "  3. cd demos/03-reduce && claude            # Compaction"
echo "  4. cd demos/04-isolate && claude           # Subagents"
echo "  5. cd demos/05-all-together && claude      # Full pipeline"
