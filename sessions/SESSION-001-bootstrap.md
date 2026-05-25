# SESSION-001: Bootstrap — pulse CLI Baseline

**Date:** 2026-05-24  
**Branch:** `feat/initial-structure`  
**Duration:** ~3 hours  
**Outcome:** Working CLI baseline, 7 learnings recorded, tests green

---

## Brainstorm

What is `pulse`? A personal health metrics CLI that reads a daily CSV log and
prints summary stats. The simplest possible demo project that still generates
genuine learnings about CSV parsing, data modeling, and terminal output.

Why CSV? Because it's what systems engineers already have. Nobody starts their
health tracking by designing a schema — they open a spreadsheet.

What will Session 1 deliver?
- `pulse.py` reads a CSV, groups by metric, prints basic stats (count, mean, min, max)
- Tests that document both the happy path AND the known bugs
- `learnings.jsonl` with 5-7 entries from what we discover during the build

What won't Session 1 deliver?
- Color terminal output (Session 2)
- `--filter` flag (Session 2)
- Date arithmetic / rolling averages (Session 2)
- Plugin architecture (Session 3)

**[ASTGL CONTENT]**
**The Problem:** When you start a new Claude Code session, the agent doesn't know
what decisions you made last time. You re-explain the same context. It makes the
same suggestions you already tried and rejected. Every session starts from scratch.

**The Solution:** Compound Engineering. After each session, you run a "Compound
step" — you write the non-obvious decisions, the gotchas, and the patterns you
discovered into a `learnings.jsonl` file. The next session loads those learnings
automatically via gstack's preamble injection. Your agent gets smarter every session
instead of starting over.

**Why This Matters:** This isn't magic — it's structured memory. The same reason
a runbook exists: so the next person (or the next session) doesn't have to discover
the same things you already found. The difference is this runbook writes itself.

**Lesson:** Start every project with an empty `learnings.jsonl`. By session 3, you'll
have 10-15 entries. By session 10, your agent will be making architectural decisions
that would have taken hours to re-establish from scratch.

---

## Plan

`[Step 1]` Write `demo/src/pulse.py` with naive CSV parsing (no error handling)
→ verify: `python pulse.py sample.csv` prints a report without crashing on clean data

`[Step 2]` Write `demo/tests/test_pulse.py` covering happy path and known edge cases
→ verify: `pytest -v` shows 3-4 passing tests + 1-2 failing "known bug" tests

`[Step 3]` Run the tests, observe which known bugs manifest
→ verify: understand the actual failure mode of blank-line handling

`[Step 4]` Write the Compound step — record learnings from what we discovered
→ verify: `show-learnings.sh` prints the entries in readable form

---

## Work

Built `demo/src/pulse.py`. Intentionally left error handling out — Session 1 is
the "before" state. Key design decisions:

**Why `defaultdict(list)` for records?**
Considered a flat list of dicts first. Rejected: every stats function would have to
filter by metric name before computing. `defaultdict(list)` with metric as key means
the stats functions are clean — they just get a list of `(date, value)` tuples.

**Why `float()` with no try/except?**
Because Session 1 is honest. The naive implementation IS the bug. If we add
error handling in Session 1, we lose the teaching moment. The test suite documents
the gap; Session 2 closes it.

**Why `sys.argv` instead of argparse?**
`argparse` adds ceremony before the interface is stable. In Session 1, the command
takes exactly one argument. That's one `sys.argv[1]` — not a `parser.add_argument`.
Refactor in Session 2 when `--filter` is added.

### Test results

```
PASSED  test_load_log_basic
PASSED  test_compute_stats_basic
PASSED  test_blank_line_handling_KNOWN_BUG   (documents silent skip behavior)
PASSED  test_non_numeric_value_KNOWN_BUG     (confirms ValueError on bad cast)
```

**Discovery:** Python 3.13's `DictReader` silently skips blank lines rather than
raising. This is actually worse than a crash — a crash is loud. Silent skip means
the user gets a summary that's missing data and has no idea. Added to learnings.

---

## Review

Does this do what Session 1 promised?

- [x] CSV reader works on clean data
- [x] Stats compute correctly
- [x] Tests pass (including the "known bug" documentation tests)
- [x] Code comments explain WHAT and WHY
- [x] No dependencies beyond stdlib (Session 1 has zero `requirements.txt` except `rich` placeholder)

What's rough and acceptable for Session 1?

- `print_report` is one big function — fine for now, will refactor in Session 2
- No date parsing — dates are strings in records; acceptable until we need date math
- `sys.argv` instead of argparse — deliberate; flag it for Session 2

What's rough and NOT acceptable even for Session 1?

- Nothing. Session 1 is clean enough for its stated scope.

---

## Compound

> This is the step that makes the next session smarter. Writing learnings is not
> optional. It takes 10 minutes. It saves 45 minutes in Session 2.

Learnings written to `.claude/projects/compound-eng-demo/learnings.jsonl`:

| Key | Type | Confidence | Summary |
|-----|------|-----------|---------|
| `csv-blank-line-handling` | pitfall | 7 | DictReader silently skips blank rows in Python 3.13 |
| `input-validation-silent-skip` | pitfall | 8 | float() gives no row context on ValueError |
| `terminal-color-fallback` | operational | 8 | Rich strips colors on pipe — test with `\| cat` |
| `defaultdict-for-metric-grouping` | pattern | 8 | defaultdict(list) + sorted() for deterministic grouping |
| `date-parsing-local-vs-utc` | architecture | 9 | Parse to datetime.date at load time, not display time |
| `tests-document-known-bugs` | pattern | 9 | `_KNOWN_BUG` suffix = living migration guide |
| `flat-main-before-argparse` | preference | 6 | sys.argv in Session 1; argparse in Session 2 |

CLAUDE.md "Known Patterns" table updated with all 7 entries.

**Next session setup:**
Before Session 2 starts, I'll open CLAUDE.md and re-read the Known Patterns table.
Two entries drive Session 2's design immediately:
- `csv-blank-line-handling` → wrap CSV parsing in try/except, log skipped rows
- `flat-main-before-argparse` → refactor entry point to argparse, add `--filter`
