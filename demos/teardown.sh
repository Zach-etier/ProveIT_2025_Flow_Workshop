#!/bin/bash
# Clean up the demo git repos after the presentation.
# Removes the .git dirs so the parent repo can track demo contents normally.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

DEMO_DIRS=(
    "00-reduce-compact"
    "01-offload-mcp"
    "02-offload-skill"
    "03-reduce"
    "04-isolate"
    "05-all-together"
)

for demo_name in "${DEMO_DIRS[@]}"; do
    demo_dir="$SCRIPT_DIR/$demo_name"
    if [ -d "$demo_dir/.git" ]; then
        echo "Removing .git from $demo_name..."
        rm -rf "$demo_dir/.git"
    fi
    # Clean up any analyses output from the demo
    if [ -d "$demo_dir/analyses" ]; then
        echo "Removing analyses from $demo_name..."
        rm -rf "$demo_dir/analyses"
    fi
done

echo "Done. Demo directories are clean."
