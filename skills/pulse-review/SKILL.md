---
name: pulse-review
description: Code review skill for the pulse demo project
version: 1.0.0
triggers:
  - /pulse-review
  - "review the pulse code"
---

# pulse-review Skill

WHAT: Reviews `demo/src/pulse.py` against known pitfalls in `learnings.jsonl`.
WHY: A minimal example skill — readable in 5 minutes, adaptable in 10.

## Checklist (reference learnings by key)

**Data loading** (`csv-blank-line-handling`, `input-validation-silent-skip`)
- [ ] `load_log()` uses raw line iteration, not DictReader
- [ ] Every field validated before casting — no bare `float(row["value"])`
- [ ] Skipped rows emit a warning with line number

**Dates** (`date-parsing-local-vs-utc`)
- [ ] Dates are `datetime.date` objects in records (not strings)
- [ ] No date parsing inside plugins or stats functions

**Plugins** (`plugin-interface-over-conditionals`)
- [ ] Every plugin has a non-empty `prefix` (DefaultPlugin excepted)
- [ ] `extra_rows()` returns `list[tuple[str, str]]`
- [ ] `threshold_warning()` returns `None` when no warning needed

**Tests** (`tests-document-known-bugs`)
- [ ] No `_KNOWN_BUG` tests remaining unfixed
- [ ] Each `MetricPlugin` subclass has at least one `extra_rows()` test

## Adapting This Skill

1. Copy `skills/pulse-review/` to `skills/<your-project>-review/`
2. Replace the checklist items with your project's known pitfalls
3. Reference your `learnings.jsonl` key names in the checklist
4. Update `triggers:` with your command phrase
