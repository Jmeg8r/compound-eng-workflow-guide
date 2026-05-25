# Learnings Schema Reference

## File Location

```
.claude/projects/<project-slug>/learnings.jsonl
```

One JSON object per line (JSONL format). Latest entry with matching `key+type` wins
(deduplication by key prefix match in gstack; manual dedup otherwise).

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `skill` | string | The gstack skill that generated this learning. Use `gstack-review` for manual entries. |
| `type` | string | One of the allowed types (see below) |
| `key` | string | Kebab-case unique identifier. Stable — updating a learning keeps the same key. |
| `insight` | string | The constraint or invariant. Write as an imperative: "always X" or "never Y". |
| `confidence` | integer | 1-10. See confidence guide below. |
| `source` | string | One of: `observed`, `user-stated`, `inferred`, `cross-model` |

## Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `files` | array of strings | Repo-relative paths where this learning applies |
| `trusted` | boolean | If `true`, gstack won't prune this learning even at low confidence |

## Allowed Types

| Type | When to use |
|------|-------------|
| `pattern` | A reusable solution to a recurring problem |
| `pitfall` | Something that looks reasonable but causes bugs or wasted time |
| `preference` | A style or approach preference with a reasoned justification |
| `architecture` | A structural constraint that should apply to the whole codebase |
| `tool` | How a specific tool behaves (library, framework, CLI) |
| `operational` | How to run, deploy, test, or observe the system |
| `investigation` | An unresolved question — use when you've discovered a problem but haven't solved it |

## Confidence Guide

| Score | Meaning |
|-------|---------|
| 9-10 | Tested across multiple sessions; high confidence in generalization |
| 7-8 | Observed in one session; assumed to generalize |
| 5-6 | Preliminary; verify before applying blindly |
| ≤4 | Prune unless there's a specific reason to retain |

## Example Entries

### Pitfall (confidence 8)
```json
{
  "skill": "gstack-investigate",
  "type": "pitfall",
  "key": "dictreader-drops-blank-rows",
  "insight": "Python's csv.DictReader never yields blank-line rows — use raw line iteration + csv.reader([line]) for per-line control.",
  "confidence": 9,
  "source": "observed",
  "files": ["demo/src/pulse.py"]
}
```

### Architecture (confidence 9)
```json
{
  "skill": "gstack-review",
  "type": "architecture",
  "key": "date-parsing-local-vs-utc",
  "insight": "Parse all date fields to datetime.date objects at load time. Deferring to display or filter time causes inconsistency across functions.",
  "confidence": 9,
  "source": "observed",
  "files": ["demo/src/pulse.py"]
}
```

### Pattern (manually recorded)
```json
{
  "skill": "gstack-review",
  "type": "pattern",
  "key": "tests-document-known-bugs",
  "insight": "Name test functions with _KNOWN_BUG suffix + fix plan in docstring. Creates a living migration guide — grep for _KNOWN_BUG to find everything to fix next session.",
  "confidence": 9,
  "source": "user-stated",
  "files": ["demo/tests/test_pulse.py"]
}
```

## Updating a Learning

When a learning turns out to be partially wrong or more nuanced than originally
captured, **update the insight** rather than creating a new entry:

1. Find the entry by `key`
2. Replace the `insight` text with the corrected understanding
3. Adjust `confidence` (up if confirmed, down if disproved)
4. Add a note in the session log that the learning was updated

Never duplicate entries — the gstack dedup logic keys on `key+type`.

## Pruning

Delete learnings that:
- Turned out to be wrong
- Were superseded by a more specific learning
- Apply to code that no longer exists
- Have confidence ≤4 with no `trusted: true`

Wrong learnings injected into future sessions cause wrong decisions. A smaller,
accurate `learnings.jsonl` is better than a large, stale one.
