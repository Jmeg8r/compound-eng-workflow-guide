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

| `plugin-interface-over-conditionals` | pattern | 8 | NEW S3: Route by prefix in code; don't add type fields to data |
| `data-format-vs-routing-separation` | architecture | 9 | NEW S3: Format changes break files; routing changes stay in code |
| `learnings-as-constraints-not-observations` | pattern | 9 | NEW S3: Write constraints, not observations — constraints become guardrails |

## Architecture (Session 3 — final state)

```
demo/src/pulse.py
  ├── MetricPlugin (ABC)        — base class: label(), extra_rows(), threshold_warning()
  ├── SleepPlugin               — prefix "sleep": nights-below-threshold, low-sleep warning
  ├── StepsPlugin               — prefix "steps": goal %, days hit goal
  ├── DefaultPlugin             — fallback for unregistered metrics
  ├── get_plugin(metric_name)   — prefix router
  ├── load_log()                — raw line parsing, blank-line safe, date objects at load time
  ├── filter_records()          — --filter (substring) and --days (timedelta) support
  ├── compute_stats()           — count, mean, min/max, rolling 7-day avg
  └── print_report()            — plugin-aware rich Table output

demo/tests/test_pulse.py — 15 tests, all passing
skills/pulse-review/SKILL.md — minimal example skill (~50 lines)
```

**To add a new metric plugin:**
1. Subclass `MetricPlugin`
2. Set `prefix = "your_metric_prefix"`
3. Implement `label()` and optionally `extra_rows()` / `threshold_warning()`
4. Add instance to `_PLUGINS` list

No data format changes needed.
