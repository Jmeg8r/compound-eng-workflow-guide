---
name: pulse-review
description: Code review skill for the pulse demo project
version: 1.0.0
triggers:
  - /pulse-review
  - "review the pulse code"
---

# pulse-review Skill

WHAT: A minimal example gstack-style skill. Reviews the pulse CLI for common
      issues and suggests next improvements based on current learnings.

WHY: Skills are reusable Claude Code commands that encode project-specific
     knowledge. This one is intentionally small (~50 lines) so you can read
     the whole thing before deciding to adapt it.

## Trigger

```
/pulse-review
```

## What This Skill Does

1. Reads `demo/src/pulse.py`
2. Reads `.claude/projects/compound-eng-demo/learnings.jsonl`
3. Checks for common issues against the known pitfalls
4. Suggests the next plugin to add based on metrics in `sample-data.csv`

## Checklist

When invoked, check the following (reference learnings by key):

### Data loading (`csv-blank-line-handling`, `input-validation-silent-skip`)
- [ ] `load_log()` uses raw line iteration (not DictReader) for blank-line visibility
- [ ] Every field is validated before casting — no bare `float(row["value"])`
- [ ] Skipped rows emit a warning with line number

### Date handling (`date-parsing-local-vs-utc`)
- [ ] Dates are `datetime.date` objects in records (not strings)
- [ ] No date parsing inside plugins or stats functions

### Plugin correctness
- [ ] Every plugin has a non-empty `prefix` (DefaultPlugin excepted)
- [ ] `extra_rows()` returns `list[tuple[str, str]]` — both elements are strings
- [ ] `threshold_warning()` returns `None` when no warning needed

### Test coverage
- [ ] Every `MetricPlugin` subclass has at least one test for `extra_rows()`
- [ ] Session bugs are documented in tests (not just in session logs)

## Output Format

After running checks, output:
```
pulse-review: N issues found

[PASS/FAIL] <check description>
...

Suggested next plugin: <metric name from sample-data.csv not yet covered>
Relevant learnings: <key>, <key>
```

## How to Adapt This Skill

1. Copy `skills/pulse-review/` to `skills/<your-project>-review/`
2. Update the checklist items to match your project's known pitfalls
3. Reference your project's `learnings.jsonl` key names in the checklist
4. Add your trigger phrase to `triggers:`

That's it. Skills don't need to be long to be useful.
