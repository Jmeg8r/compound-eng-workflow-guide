#!/usr/bin/env bash
# compound-init.sh — scaffold the Compound Engineering workflow into a project (idempotent).
#
# WHAT: adds the committed half of the compound loop to a target repo:
#         - a managed "Compound Engineering Setup" + "Known Patterns" block in CLAUDE.md
#         - sessions/ with a cycle template
#         - show-learnings.sh + refresh-digest.sh helpers
#       The working store stays in gstack (~/.gstack/projects/<slug>/learnings.jsonl),
#       auto-loaded at session start — this only adds what gstack does NOT commit.
# WHY:  one scaffolder beats hand-editing every repo. Re-running is safe (no dupes).
#
# Usage:
#   scaffold/compound-init.sh /path/to/project          # full scaffold
#   scaffold/compound-init.sh /path/to/project --light   # skip sessions/ (repo already has it)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:?usage: compound-init.sh <project-dir> [--light]}"
LIGHT="${2:-}"

# WHAT: reject an unrecognized 2nd argument (e.g. a misspelled --light) instead of
#       silently falling back to full-scaffold mode.
if [ -n "$LIGHT" ] && [ "$LIGHT" != "--light" ]; then
  echo "Unknown option: '$LIGHT'" >&2
  echo "usage: compound-init.sh <project-dir> [--light]" >&2
  exit 1
fi

[ -d "$TARGET/.git" ] || { echo "Not a git repo: $TARGET" >&2; exit 1; }
cd "$TARGET"

# WHAT: resolve slug for the next-steps message (helpers re-resolve at runtime).
SLUG=""
for p in gstack-slug "$HOME/.claude/skills/gstack/bin/gstack-slug" "$HOME/Projects/gstack/bin/gstack-slug"; do
  if command -v "$p" >/dev/null 2>&1 || [ -x "$p" ]; then eval "$("$p" 2>/dev/null)" || true; break; fi
done

emit_block() {
cat <<'BLOCK'
<!-- COMPOUND:START -->
## Compound Engineering Setup

Learnings are captured by gstack into `~/.gstack/projects/<slug>/learnings.jsonl` and
auto-loaded into context at session start. This repo commits only the human-readable
digest below — the gstack store is the source of truth.

- **View learnings offline:** `./show-learnings.sh` (also `high`, or a type filter)
- **Record a constraint:** `/gstack-learn add` (write constraints, not observations)
- **Refresh the table below** after a session's Compound step: `./refresh-digest.sh`
- **Session logs:** copy `sessions/TEMPLATE.md` → `sessions/SESSION-NNN-<title>.md` and
  follow Brainstorm → Plan → Work → Review → Compound.

## Known Patterns

<!-- LEARNINGS:START -->
_No learnings yet. Run `./refresh-digest.sh` after your first Compound step._
<!-- LEARNINGS:END -->
<!-- COMPOUND:END -->
BLOCK
}

# --- CLAUDE.md ---------------------------------------------------------------
if [ ! -f CLAUDE.md ]; then
  BASENAME="$(basename "$PWD")"
  {
    echo "# CLAUDE.md — ${BASENAME}"
    echo ""
    echo "## Project Purpose"
    echo ""
    echo "TODO(james): one sentence on what this project does."
    echo ""
    echo "## Key Commands"
    echo ""
    echo '```bash'
    echo "# TODO(james): how to run / test / build this project"
    echo '```'
    echo ""
    emit_block
  } > CLAUDE.md
  echo "  + created CLAUDE.md (fill Project Purpose / Key Commands)"
elif grep -q '<!-- COMPOUND:START -->' CLAUDE.md; then
  echo "  = CLAUDE.md already has the compound block (left as-is)"
else
  { echo ""; emit_block; } >> CLAUDE.md
  echo "  + appended compound block to existing CLAUDE.md"
fi

# --- sessions/ ---------------------------------------------------------------
if [ "$LIGHT" = "--light" ]; then
  echo "  · --light: skipped sessions/ scaffold"
else
  mkdir -p sessions
  [ -f sessions/TEMPLATE.md ] || cp "$SCRIPT_DIR/sessions-TEMPLATE.md" sessions/TEMPLATE.md
  [ -f sessions/.gitkeep ] || : > sessions/.gitkeep
  echo "  + sessions/ (TEMPLATE.md)"
fi

# --- helper scripts (always refresh to latest) -------------------------------
cp "$SCRIPT_DIR/show-learnings.sh" ./show-learnings.sh
cp "$SCRIPT_DIR/refresh-digest.sh" ./refresh-digest.sh
chmod +x ./show-learnings.sh ./refresh-digest.sh
echo "  + show-learnings.sh, refresh-digest.sh"

# --- CodeRabbit review policy (don't clobber an existing one) ----------------
if [ -f .coderabbit.yaml ] || [ -f .coderabbit.yml ]; then
  echo "  = .coderabbit.yaml already present (left as-is)"
else
  cp "$SCRIPT_DIR/.coderabbit.yaml" ./.coderabbit.yaml
  echo "  + .coderabbit.yaml (CodeRabbit review policy)"
fi

echo ""
echo "Done: $(basename "$PWD")  (slug: ${SLUG:-<unresolved>})"
echo "Next: ./refresh-digest.sh && ./show-learnings.sh"
