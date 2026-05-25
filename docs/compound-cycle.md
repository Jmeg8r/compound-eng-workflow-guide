# The Compound Engineering Cycle

## The 5-Step Loop

Every session follows the same structure. The loop is what makes it compound.

```
Brainstorm → Plan → Work → Review → Compound
                                        ↓
                              learnings.jsonl
                                        ↓
                              Next session preamble
                                        ↓
                              Better decisions, faster
```

### Step 1: Brainstorm

Open `CLAUDE.md`. Read the Known Patterns table. Let it constrain your design
before you write the first line of code.

Ask:
- What did I learn last session that applies here?
- What are the highest-confidence learnings in this area?
- Are there any constraints that save me from a bad decision?

### Step 2: Plan

Write your plan as `[Step N] → verify: [check]`. This transforms the session from
a vague goal into a series of verifiable outcomes.

### Step 3: Work

Build. Run tests. Discover things. Note surprises in the session log as you go —
especially when something is harder than expected or when an assumption was wrong.

### Step 4: Review

Go through a checklist:
- Does it do what it promised?
- Are there rough edges that are acceptable for this session?
- Are there rough edges that are NOT acceptable?

### Step 5: Compound (the differentiator)

This is the step most developers skip. It takes 10-15 minutes. It pays back in
every future session.

Write your learnings to `learnings.jsonl`. The schema:

```json
{
  "skill": "gstack-review",
  "type": "pattern|pitfall|preference|architecture|tool|operational|investigation",
  "key": "kebab-case-unique-key",
  "insight": "The constraint or invariant, not just the observation.",
  "confidence": 6,
  "source": "observed|user-stated|inferred|cross-model",
  "files": ["optional/list/of/relevant/files.py"]
}
```

**Write constraints, not observations.** "Parse dates at load time" is a constraint.
"I saw a bug with date parsing" is an observation. Constraints become guardrails in
the next session. Observations require re-interpretation.

---

## How Learnings Compound

### Confidence scores decay over time

A confidence 8 learning from 3 months ago is still relevant. A confidence 6 learning
from 2 weeks ago might already be superseded. When you update a learning in a later
session, increase the confidence if confirmed, decrease if disproved, or delete if
obsolete.

**Confidence guide:**
- 9-10: High confidence — strong evidence, tested in multiple sessions
- 7-8: Medium confidence — observed in one session, assumed to generalize
- 5-6: Low confidence — inferred or preliminary, verify before applying
- ≤4: Questionable — prune on next review unless you have a reason to keep it

### The compound payoff is invisible

You cannot measure the decisions you didn't make incorrectly. The ROI of the Compound
step shows up as:
- Sessions that stay on-track without re-debating architecture
- Fewer "wait, didn't we already solve this?" moments
- New contributors (or future-you) who read CLAUDE.md and understand the project
  without needing a walkthrough

The `date-parsing-local-vs-utc` learning in this project is the clearest example:
written in Session 1, applied in Session 2 without deliberation, confirmed valid in
Session 3's tests. Total re-deliberation cost across Sessions 2 and 3: zero.

---

## Pruning

Learnings that turn out to be wrong should be **deleted**, not kept with a note.
Wrong learnings injected into future sessions cause wrong decisions.

Learnings that were right in Session 1 but superseded by Session 3 should be updated
with the new insight, not duplicated. The `csv-blank-line-handling` learning was
updated in Session 2 when we learned the actual mechanism was DictReader dropping
rows rather than silencing exceptions. The key stayed the same; the insight changed.

---

## The Three Frameworks (Where Compound Engineering Fits)

| | Compound Engineering | Karpathy's Autoresearch | Full RSI |
|---|---|---|---|
| **Loop** | Brainstorm → Work → **Compound** | Modify → Evaluate → Keep/Revert | System-defined |
| **Memory** | `learnings.jsonl` | Git history | Self-generated |
| **Human role** | Reflection + compound step | Designs metric + constraint | None |
| **Suitable for** | Multi-session project development | Single-file optimization loops | Theoretical |

Compound Engineering is Autoresearch with a longer time horizon and a human in the
reflection step. Both are safe instances of Recursive Self-Improvement (RSI). Full
RSI (where the system modifies its own goals) remains theoretical.
