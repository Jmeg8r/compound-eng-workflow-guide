# SESSION-002: Filter + Color — argparse, rich, error handling

**Date:** 2026-05-24  
**Branch:** `feat/session-2-filter-color`  
**Duration:** ~2 hours  
**Outcome:** _KNOWN_BUG tests flipped to passing, --filter and --days working, 5 new learnings

---

## Brainstorm

Session 2 opens with reading CLAUDE.md's "Known Patterns" table.

Two learnings drive the agenda immediately:

- `csv-blank-line-handling` (pitfall, 7): wrap CSV parsing, log skipped rows
- `flat-main-before-argparse` (preference, 6): now we know the flags — time to refactor

One learning shapes the architecture for the `--filter` flag:

- `date-parsing-local-vs-utc` (architecture, 9): parse dates at load time, not display time.
  Without this, `--days` filtering (date arithmetic) would be broken or fragile.

The fact that I wrote down `date-parsing-local-vs-utc` in Session 1 before writing
any filtering code is the compound payoff. That architectural decision was made
correctly because the learning existed. Without it, I would have stored dates as
strings, and the `--days` filter would have been written against string comparison.
It would have "worked" for ISO dates but been a lurking bug.

**[ASTGL CONTENT]**
**The Problem:** I've been building CLI tools for years and I still make the same
mistake: deferring date parsing to wherever I first need it. The problem isn't that
I don't know better — it's that there's no forcing function. Without a written
learning from last session saying "parse dates at load time," my instinct is to parse
them wherever they're first used (usually in a display function). Then filtering
breaks because two different places parse dates with two different assumptions.

**The Solution:** The `learnings.jsonl` entry for `date-parsing-local-vs-utc` was
written in Session 1 *before* Session 2 needed it. When Session 2 opened and I read
the Known Patterns table, the decision was already made. I wrote `datetime.strptime()`
at load time without thinking about it — because past-me already did the thinking.

**Why This Matters:** This is what "compounding" actually means. It's not that AI
gets smarter. It's that your *decisions persist*. The cognitive load of Session 2 is
lower because Session 1 did the hard thinking. At 10 sessions, you're not starting
from scratch — you're standing on 50+ preserved decisions.

**Lesson:** The Compound step isn't journaling. It's debt reduction. Every learning
you write is a decision you never have to make again.

---

## Plan

`[Step 1]` Refactor `load_log()` to pre-scan raw lines for blank row detection
→ verify: `test_blank_line_handling_FIXED` passes (was _KNOWN_BUG in Session 1)

`[Step 2]` Add `filter_records()` function with metric name and `--days` support
→ verify: `test_filter_by_metric_name`, `test_filter_days_*` pass

`[Step 3]` Replace `print_report()` plain text with rich `Table` output
→ verify: `python pulse.py sample-data.csv` shows formatted tables, `| cat` strips colors

`[Step 4]` Refactor `main()` to argparse with `--filter` and `--days` flags
→ verify: `python pulse.py sample.csv --filter sleep` shows only sleep metrics

---

## Work

### The blank line discovery

Session 1's `csv-blank-line-handling` learning said "Python 3.13 DictReader silently
skips blank rows." The fix plan was: wrap CSV parsing in try/except, log skipped rows.

When I went to implement the fix, I learned something deeper: DictReader doesn't
just silence the error — it **never yields the row at all**. You can't detect a blank
line inside a DictReader loop because blank lines simply don't appear.

This required abandoning DictReader entirely for manual line-by-line parsing:

```python
# Read raw lines for blank-line visibility
with open(filepath, newline="") as f:
    raw_lines = f.readlines()

for line_num, raw_line in enumerate(raw_lines[1:], start=2):
    stripped = raw_line.strip()
    if not stripped:
        warnings.warn(f"Line {line_num}: blank row skipped", stacklevel=2)
        skipped += 1
        continue
    # Then parse non-blank lines via csv.reader for quoting/escaping
    parsed_row = next(csv.reader([stripped]))
```

The Session 1 learning was right about the symptom (silent data loss) but wrong about
the mechanism (it's DictReader skipping, not float() silencing). The fix required
going one level deeper than anticipated.

**This is exactly what confidence scores are for.** The `csv-blank-line-handling`
learning had confidence 7, not 9. A 7 means "I observed this behavior but may not
understand the full mechanism." The lower confidence was a flag that said "verify
the mechanism before assuming the fix is trivial." It paid off.

### Rolling 7-day average

Added to `compute_stats()`. Takes the last 7 values (or all if fewer than 7).
Uses stdlib `statistics.mean()` — no new dependencies.

### Rich output

`rich.console.Console()` handles color stripping automatically on pipe.
Tested with `python pulse.py sample-data.csv | cat` — clean text, no escape codes.
`terminal-color-fallback` learning confirmed valid, confidence stays at 8.

---

## Review

- [x] All 9 tests pass (including the formerly _KNOWN_BUG tests)
- [x] `--filter` works case-insensitively
- [x] `--days` filters by date (works because dates were parsed at load time)
- [x] Blank lines produce warnings, not silent data loss
- [x] Non-numeric values produce warnings, not crashes
- [x] Rich tables display on terminal; colors strip cleanly on pipe

One rough edge: `--days` calculates from `date.today()`. This means test results
depend on what day tests run. The tests use `timedelta` offsets from `today` so
they're stable, but any hardcoded date comparison in tests would break over time.
Added to learnings.

---

## Compound

Updating `.claude/projects/compound-eng-demo/learnings.jsonl`:

| Key | Type | Confidence | Action | Summary |
|-----|------|-----------|--------|---------|
| `csv-blank-line-handling` | pitfall | 7→8 | UPDATE | Fixed, but mechanism deeper than expected — DictReader drops blank rows entirely |
| `dictreader-drops-blank-rows` | pitfall | 9 | NEW | DictReader in Python 3.13+ never yields blank-line rows; must use raw line parsing |
| `confidence-score-predicts-fix-complexity` | pattern | 8 | NEW | Low confidence (≤7) on a learning predicts the fix will be more complex than assumed |
| `date-today-in-tests` | operational | 8 | NEW | Avoid `date.today()` hardcoded in test expectations — use `timedelta` offsets from today |
| `rich-console-singleton` | tool | 7 | NEW | Single `Console()` instance at module level handles pipe detection globally |

CLAUDE.md "Known Patterns" table updated. Session 2 total: 12 learnings.
