# CLAUDE.md — compound-eng-workflow-guide

> This file is the Claude Code context for the `pulse` demo project inside the
> Compound Engineering Workflow Guide. It evolves across sessions — each session
> updates the "Known Patterns" section with newly codified learnings.

## Project Purpose

A GitHub template demonstrating Compound Engineering patterns for solo builders
using Claude Code, gstack skills, and local LLMs. The `demo/` directory contains
`pulse` — a personal health metrics CLI used as the teaching vehicle.

## Key Commands

```bash
# Run the demo CLI
python demo/src/pulse.py demo/sample-data.csv

# Run tests
python -m pytest demo/tests/ -v

# View compounded learnings (requires jq)
./show-learnings.sh

# Add a learning manually (requires gstack)
# /gstack-learn add
```

## Compound Engineering Setup

Learnings are stored at `.claude/projects/compound-eng-demo/learnings.jsonl`.
Use `/gstack-learn` to review, prune, and export learnings.
Use `/gstack-learn add` to manually record a learning after any session.
At session start, gstack's preamble loads the top learnings automatically.
Without gstack: run `./show-learnings.sh` to read learnings directly.

Session logs live in `sessions/` — always write the full Brainstorm → Plan →
Work → Review → Compound cycle. The Compound step writes to learnings.jsonl.

## Conventions

- Python: `snake_case` functions/vars, `PascalCase` classes
- Comments: `# WHAT:` + `# WHY:` on non-obvious blocks
- Commits: conventional (`feat:`, `fix:`, `docs:`, `chore:`)
- Tests: `_KNOWN_BUG` suffix on tests documenting unfixed issues
- Never suppress errors silently — log or raise with context

## Known Patterns (Session 2 — 12 learnings)

> Updated at Compound step of each session. Reference these before making
> architectural decisions in subsequent sessions.

| Key | Type | Confidence | Insight summary |
|-----|------|-----------|-----------------|
| `csv-blank-line-handling` | pitfall | 8↑ | DictReader drops blank rows entirely — use raw line iteration + csv.reader |
| `dictreader-drops-blank-rows` | pitfall | 9 | NEW: DictReader never yields blank rows; cannot intercept via try/except |
| `input-validation-silent-skip` | pitfall | 8 | Float cast gives no row context — validate before casting, surface row index |
| `terminal-color-fallback` | operational | 8 | Rich strips colors on pipe — test with `\| cat` before shipping |
| `defaultdict-for-metric-grouping` | pattern | 8 | `defaultdict(list)` + `sorted(records.items())` for deterministic grouping |
| `date-parsing-local-vs-utc` | architecture | 9 | Parse dates to `datetime.date` at load time — confirmed critical for --days filter |
| `tests-document-known-bugs` | pattern | 9 | `_KNOWN_BUG` suffix + docstring fix plan = living migration guide |
| `flat-main-before-argparse` | preference | 6 | `sys.argv` in Session 1; refactor to `argparse` in Session 2 |
| `confidence-score-predicts-fix-complexity` | pattern | 8 | NEW: ≤7 confidence on a pitfall = expect the fix to be harder than assumed |
| `date-today-in-tests` | operational | 8 | NEW: Use `timedelta` offsets in tests, never hardcoded dates |
| `rich-console-singleton` | tool | 7 | NEW: One `Console()` at module level — avoids pipe-detection disagreement |

## Architecture (Session 2 state)

```
demo/src/pulse.py        — load_log(), filter_records(), compute_stats(), print_report(), main()
demo/tests/test_pulse.py — 9 tests, all passing (no _KNOWN_BUG remaining after Session 2)
```

Session 3 will add: plugin architecture for metric types (replaces if/elif in stats).
Key learning to apply: `date-parsing-local-vs-utc` already done — plugins receive
`(datetime.date, float)` tuples. No date parsing inside plugins needed.
