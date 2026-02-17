#!/usr/bin/env bash
# stamp-shift-report.sh — Claude Code PostToolUse hook for Write tool
# Appends a validation stamp to shift report files after successful write.
# Runs after validate-shift-report.sh (PreToolUse) has already confirmed
# all 9 mandatory sections are present.
#
# Exit codes:
#   0 — always (PostToolUse hooks should not block)

set -euo pipefail

# Read the tool input JSON from stdin
INPUT=$(cat)

# Extract file_path from the Write tool input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# If no file_path, pass through
if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Only stamp files matching *shift*report*.md (case-insensitive)
BASENAME=$(basename "$FILE_PATH")
if ! echo "$BASENAME" | grep -iqE 'shift.*report.*\.md$'; then
  exit 0
fi

# Verify the file exists (write succeeded)
if [[ ! -f "$FILE_PATH" ]]; then
  exit 0
fi

# Generate stamp fields
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
CONTENT_HASH=$(sha256sum "$FILE_PATH" | cut -d' ' -f1)
SHORT_HASH=${CONTENT_HASH:0:12}

# Append validation stamp
cat >> "$FILE_PATH" <<EOF

---

> **Validated**: ${TIMESTAMP} | ENT-B-OPS-005 Rev 4 | All 9 mandatory sections present | SHA256: \`${SHORT_HASH}\`
EOF

exit 0
