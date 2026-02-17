#!/usr/bin/env bash
# validate-shift-report.sh — Claude Code PreToolUse hook for Write tool
# Validates that shift report markdown files contain all 9 mandatory sections
# per ENT-B-OPS-005 (shift-handoff-checklist.md).
#
# Exit codes:
#   0 — pass (not a shift report, or all sections present)
#   2 — block (missing mandatory sections)

set -euo pipefail

# Read the tool input JSON from stdin
INPUT=$(cat)

# Extract file_path from the Write tool input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# If no file_path, pass through
if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Only validate files matching *shift*report*.md (case-insensitive)
BASENAME=$(basename "$FILE_PATH")
if ! echo "$BASENAME" | grep -iqE 'shift.*report.*\.md$'; then
  exit 0
fi

# Extract the content that will be written
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')

if [[ -z "$CONTENT" ]]; then
  echo '{"additionalContext": "Warning: shift report content is empty."}' >&2
  exit 2
fi

# Define the 9 mandatory sections with flexible regex patterns
declare -a SECTION_NAMES=(
  "1. Executive Summary"
  "2. Safety"
  "3. Production vs. Target"
  "4. OEE Summary"
  "5. Quality Flags"
  "6. Equipment Status"
  "7. Open Work Orders"
  "8. Upcoming"
  "9. Notes"
)

declare -a SECTION_PATTERNS=(
  '## .*1\..*Executive Summary'
  '## .*2\..*Safety'
  '## .*3\..*Production vs\..*Target'
  '## .*4\..*OEE Summary'
  '## .*5\..*Quality Flags'
  '## .*6\..*Equipment Status'
  '## .*7\..*Open Work Orders'
  '## .*8\..*Upcoming'
  '## .*9\..*Notes'
)

MISSING=()

for i in "${!SECTION_PATTERNS[@]}"; do
  if ! echo "$CONTENT" | grep -qiE "${SECTION_PATTERNS[$i]}"; then
    MISSING+=("${SECTION_NAMES[$i]}")
  fi
done

if [[ ${#MISSING[@]} -eq 0 ]]; then
  echo '{"additionalContext": "Shift report validation passed — all 9 mandatory sections (ENT-B-OPS-005) are present."}'
  exit 0
else
  MISSING_LIST=""
  for section in "${MISSING[@]}"; do
    MISSING_LIST="${MISSING_LIST}\n  - ${section}"
  done
  echo -e "SHIFT REPORT VALIDATION FAILED (ENT-B-OPS-005)\n\nMissing mandatory sections:${MISSING_LIST}\n\nAll 9 sections are required. Section headings must follow the format: ## N. Section Name\n(e.g., '## 1. Executive Summary', '## 2. Safety', etc.)" >&2
  exit 2
fi
