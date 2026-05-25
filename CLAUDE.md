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

## Known Patterns (Session 1)

> Updated at Compound step of each session. Reference these before making
> architectural decisions in subsequent sessions.

| Key | Type | Confidence | Insight summary |
|-----|------|-----------|-----------------|
| `csv-blank-line-handling` | pitfall | 7 | DictReader silently skips blank rows — always log skips with line numbers |
| `input-validation-silent-skip` | pitfall | 8 | Float cast gives no row context — validate before casting, surface row index |
| `terminal-color-fallback` | operational | 8 | Rich strips colors on pipe automatically — test with `\| cat` before shipping |
| `defaultdict-for-metric-grouping` | pattern | 8 | `defaultdict(list)` + `sorted(records.items())` for deterministic metric grouping |
| `date-parsing-local-vs-utc` | architecture | 9 | Parse dates to `datetime.date` at load time, not display time |
| `tests-document-known-bugs` | pattern | 9 | `_KNOWN_BUG` suffix + docstring fix plan = living migration guide |
| `flat-main-before-argparse` | preference | 6 | Use `sys.argv` in Session 1; refactor to `argparse` in Session 2 |

## Architecture (Session 1 state)

```
demo/src/pulse.py        — CLI entry point + all logic (monolithic, Session 1)
demo/tests/test_pulse.py — pytest suite, documents known bugs
```

Session 2 will add: `--filter` flag, `rich` output, `argparse`, error handling.
Session 3 will add: plugin architecture for metric types.
