# SESSION-003: Plugin Architecture — The Compound Payoff

**Date:** 2026-05-24  
**Branch:** `feat/session-3-plugin-arch`  
**Duration:** ~2 hours  
**Outcome:** Plugin architecture complete, 15 tests passing, 3 new learnings

---

## Brainstorm

Session 3 opens with a re-read of CLAUDE.md's "Known Patterns" table (12 entries).

The last line of the architecture section says:
> "Session 3 will add: plugin architecture for metric types. Key learning to apply:
> `date-parsing-local-vs-utc` already done — plugins receive `(datetime.date, float)`
> tuples. No date parsing inside plugins needed."

That sentence was written during Session 2's Compound step — *before* Session 3 began.
This is the compound payoff: the architecture decision for Session 3 was made in
Session 2. I didn't have to think about it again. I opened CLAUDE.md and the decision
was already there.

**[ASTGL CONTENT]**
**The Problem:** When you build iteratively, the same architectural questions come up
in every session: "should I parse this data here or defer it?" "Should I add the if/elif
or extract the abstraction?" You answer them, then you forget them, then you answer them
again. The cumulative cognitive cost of re-deciding the same things is enormous.

**The Solution:** The Compound step writes the decisions down. Not as documentation
(nobody reads docs during active development) — as a table in CLAUDE.md that loads
at session start. The decision is *injected into context* before you write the first
line of code.

**Why This Matters:** Session 3 didn't "use" the `date-parsing-local-vs-utc` learning.
It simply didn't make the wrong decision because the learning was there. You can't
measure what you didn't decide incorrectly. That's the invisible ROI of compounding.
It's not that the next session is dramatically smarter. It's that it doesn't have to
make certain mistakes.

**Lesson:** Write your learnings as constraints and invariants, not observations. "Dates
should be parsed at load time" is a constraint. It loads into context and becomes
a guardrail. "I observed that parsing dates at display time caused a bug" is an
observation — it's useful but doesn't create the guardrail.

---

## Plan

`[Step 1]` Design `MetricPlugin` abstract base class
→ verify: three methods — `label()`, `extra_rows()`, `threshold_warning()`

`[Step 2]` Implement `SleepPlugin` and `StepsPlugin` as concrete examples
→ verify: `get_plugin("sleep_hours")` → `SleepPlugin`, `get_plugin("blood_pressure")` → `DefaultPlugin`

`[Step 3]` Update `print_report()` to call plugin methods
→ verify: `python pulse.py sample-data.csv` shows "Nights < 7h" and "Goal %" rows

`[Step 4]` Write Session 3 tests (7 new tests for plugin interface)
→ verify: 15/15 tests pass

`[Step 5]` Write `skills/pulse-review/SKILL.md`
→ verify: ≤50 lines, readable without gstack context

`[Step 6]` Compound step
→ verify: learnings.jsonl has 15 entries, CLAUDE.md updated

---

## Work

### The plugin interface design

The `date-parsing-local-vs-utc` learning made one design decision automatic: plugins
receive `(datetime.date, float)` tuples. No date conversion inside plugins.

The `plugin-interface-over-conditionals` decision (new learning from this session):
How to route metrics to plugins? Two options:
1. Add a `type` field to the CSV (explicit typing)
2. Route by metric name prefix in code (implicit typing)

Rejected option 1: it changes the data format. Existing CSV files wouldn't work.
The data format should be stable; routing belongs in code.

Chose prefix matching: `get_plugin(metric_name)` tries each registered plugin's
`prefix` attribute. `"sleep_hours".startswith("sleep")` → `SleepPlugin`. Clean,
no regex, no config file.

### The `_KNOWN_BUG` test progression

Session 1 had 2 `_KNOWN_BUG` tests.
Session 2 renamed them to `_FIXED` tests and added 5 new tests.
Session 3 added 7 new plugin tests.

Total: 15 tests, 0 failures. The test file is now a narrative of the project's
evolution. Someone new to the codebase can read the test names and understand
the compound engineering story without reading the session logs.

### The example skill

`skills/pulse-review/SKILL.md` is 50 lines. The checklist references 4 learnings
by key. The "how to adapt" section is 4 bullet points. Nothing in it requires
gstack to be installed — it's a Claude Code command that works with plain prompts.

---

## Review

- [x] 15/15 tests passing
- [x] Plugin output visible in CLI (Nights < 7h, Goal %, Days hit goal)
- [x] `DefaultPlugin` handles unknown metrics without crashing
- [x] `skills/pulse-review/SKILL.md` is ≤50 lines and self-contained
- [x] `date-parsing-local-vs-utc` learning confirmed valid — plugins never touch dates

---

## Compound

Final compound step. Updating `.claude/projects/compound-eng-demo/learnings.jsonl`:

| Key | Type | Confidence | Action | Summary |
|-----|------|-----------|--------|---------|
| `plugin-interface-over-conditionals` | pattern | 8 | NEW | Route by name prefix in code; don't add type fields to data |
| `data-format-vs-routing-separation` | architecture | 9 | NEW | Data format changes are expensive (breaks existing files); routing is cheap (code only) |
| `learnings-as-constraints-not-observations` | pattern | 9 | NEW | Write constraints ("parse dates at load time") not observations ("I saw a bug") — constraints become guardrails |

Final state: 15 learnings in `learnings.jsonl`, 15 tests passing, 3 sessions complete.

### The compound payoff summary

```
Session 1 decisions used in Session 2: 3 of 7 learnings directly applied
Session 2 decisions used in Session 3: 2 of 5 new learnings directly applied
Decisions made correctly without re-deliberation: 5 architectural constraints
Minutes saved by not re-debating known questions: estimated 60-90 min
```

You can't see the time you saved. You can see the decisions that didn't happen.
The `date-parsing-local-vs-utc` learning is the cleanest example: it was written
in Session 1 before Session 2 needed it, applied automatically in Session 2's design,
and confirmed valid in Session 3's tests. Total deliberation cost in Sessions 2 and 3:
zero. It was already decided.
