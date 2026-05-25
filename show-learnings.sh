#!/usr/bin/env bash
# show-learnings.sh — display learnings.jsonl without requiring gstack
#
# WHAT: Pretty-print the compound engineering learnings for this project.
# WHY: Not everyone has gstack installed. This makes learnings readable
#      with only jq (standard on most developer machines).
#
# Usage:
#   ./show-learnings.sh                 # show all learnings
#   ./show-learnings.sh pitfall         # filter by type
#   ./show-learnings.sh high            # show high confidence (≥8) only

LEARNINGS_FILE=".claude/projects/compound-eng-demo/learnings.jsonl"

if [ ! -f "$LEARNINGS_FILE" ]; then
  echo "No learnings file found at $LEARNINGS_FILE"
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "jq is required. Install with: brew install jq"
  exit 1
fi

FILTER="${1:-}"

# Build jq filter
if [ "$FILTER" = "high" ]; then
  JQ_FILTER='select(.confidence >= 8)'
elif [ -n "$FILTER" ]; then
  JQ_FILTER="select(.type == \"$FILTER\")"
else
  JQ_FILTER='.'
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Compound Engineering Learnings"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

jq -r "$JQ_FILTER | \"\\n[\(.type | ascii_upcase)] \(.key)  (confidence: \(.confidence))\\n  \(.insight)\"" \
  "$LEARNINGS_FILE"

echo ""
TOTAL=$(jq -s 'length' "$LEARNINGS_FILE")
echo "Total: $TOTAL learning(s)"
echo ""
