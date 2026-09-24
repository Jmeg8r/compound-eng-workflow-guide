#!/usr/bin/env bash
# show-learnings.sh — display learnings.jsonl without requiring gstack
#
# WHAT: Pretty-print the compound engineering learnings for this project.
# WHY:  Not everyone has gstack installed. This makes learnings readable
#       with only jq (standard on most developer machines).
#
# Usage:
#   ./show-learnings.sh                 # show all learnings
#   ./show-learnings.sh pitfall         # filter by type
#   ./show-learnings.sh high            # show high confidence (≥8) only
set -euo pipefail

LEARNINGS_FILE=".claude/projects/compound-eng-demo/learnings.jsonl"

if [ ! -f "$LEARNINGS_FILE" ]; then
  echo "No learnings file found at $LEARNINGS_FILE" >&2
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "jq is required. Install with: brew install jq" >&2
  exit 1
fi

FILTER="${1:-}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Compound Engineering Learnings"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# WHAT: dedupe by key+type (latest-wins per docs/learnings-schema.md), then filter
#       and print. FILTER is passed via --arg (data, not code) so special characters
#       in it can't break or inject into the jq program.
JQ_KEEP='def keep: if $f == "" then true elif $f == "high" then (.confidence // 0) >= 8 else .type == $f end;'
jq -rs --arg f "$FILTER" "$JQ_KEEP"'
  group_by(.key + "|" + .type)
  | map(max_by(.ts // ""))
  | sort_by(-(.confidence // 0))
  | .[]
  | select(keep)
  | "\n[\(.type | ascii_upcase)] \(.key)  (confidence: \(.confidence))\n  \(.insight)"
' "$LEARNINGS_FILE"

echo ""
# WHAT: count the SAME deduped+filtered set that was printed so Total can't contradict
#       the rows shown when a filter is active.
TOTAL=$(jq -rs --arg f "$FILTER" "$JQ_KEEP"'
  [ group_by(.key + "|" + .type) | map(max_by(.ts // ""))[] | select(keep) ] | length' "$LEARNINGS_FILE")
echo "Total: ${TOTAL} learning(s)${FILTER:+ (filter: $FILTER)}"
echo ""
