# SESSION-ARTICLES.md
# Three [ASTGL CONTENT] blocks — one per article in the Compound Engineering series.
# Run /astgl-publish SESSION-ARTICLES.md to process through the pipeline.

---

[ASTGL CONTENT]

**Series:** Compound Engineering for Solo Builders — Part 1 of 3
**Title:** The AI Dev Workflow That Gets Smarter Every Session
**Subtitle:** Why your Claude Code sessions should compound — and how three frameworks stack up

**The Problem:**

Every Claude Code session I start, I'm doing the same thing: re-explaining context.
"This project uses snake_case. We decided to parse dates at load time. We switched away
from DictReader because of how it handles blank lines."

The agent doesn't know any of this. Last session's decisions don't carry over. Last
session's mistakes don't carry over either — so they get made again. Same architectural
debates. Same gotchas. You are, functionally, the only memory in the room.

I've been a systems engineer for 25 years. We had a name for this problem. We called it
"hero dependency" — when one person holds all the knowledge and everything falls apart
when they leave, or when they forget. The fix was always the same: write it down in the
runbook. Enforce the runbook. Update the runbook.

We have the same problem with AI sessions, and the fix is the same. But now the runbook
can write itself.

**The Setup:**

Three frameworks have emerged for building AI systems that improve over time:

**Karpathy's Autoresearch** is a bounded autonomous loop. One file, one metric, fixed
time budget. The agent generates variants of a training script, runs them for exactly
5 minutes, evaluates against a single metric, and keeps or reverts via `git`. Karpathy
ran this overnight and got 118 experiments, 26 keepers, a 17.6% improvement in validation
loss. The genius isn't the agent — it's the metric design. The agent does what agents do
well (generate variants at volume). The human does what humans do well (decide what to
measure and set the stopping conditions).

**Compound Engineering** (Ken Huang, Nico Bailon) is human-in-the-loop RSI. Every session
ends with a Compound step: you write what you learned — patterns, pitfalls, architectural
constraints — into a structured `learnings.jsonl` file. The next session loads those
learnings at startup via preamble injection. The agent walks into the session already
knowing what the last session figured out.

**Recursive Self-Improvement (RSI)** is the theoretical frame. Both patterns above are
safe instances of RSI. Autoresearch is bounded RSI — one file, one metric, no goal
modification. Compound Engineering is human-guided RSI — the loop includes a human
reflection step. Full RSI (system modifies its own goals) stays theoretical because
it's unsafe and uncontrolled.

**The Solution:**

For solo builders, Compound Engineering is the practical choice. Here's why the others
don't fully fit:

Autoresearch requires a precisely defined metric. That works brilliantly for ML
benchmarks. It's harder for "is this code good?" or "does this API design make sense?"
You can't always quantify the thing you care about.

Full RSI modifies goals. That's not a thing we want for our development tools.

Compound Engineering keeps humans at the judgment step — the Compound step — and
automates the memory. The agent doesn't decide what to remember. You do. You write the
constraint, the guardrail, the non-obvious decision. The agent reads it in every future
session.

The core mechanic is `learnings.jsonl`. Each entry has a type (`pattern`, `pitfall`,
`architecture`, `preference`, `tool`, `operational`), a confidence score (1-10), and an
insight written as a constraint rather than an observation.

"Parse dates at load time" — constraint. Useful.
"I saw a bug with date parsing" — observation. Requires re-interpretation every session.

Constraints become guardrails. Observations require homework.

**Why This Matters:**

In 25 years of sysadmin work, the highest-leverage thing I could do on any project was
write the runbook. Not because I was going to use it — because someone else might, and
because "future me" is as unreliable as any contractor.

Compound Engineering is that instinct applied to AI development. Every session is a
contractor. Brief them well. Leave them a runbook. Collect what they learned before they
leave.

The difference is that now the contractor helps write the runbook. At the Compound step,
Claude reviews the session and proposes what should go in `learnings.jsonl`. You decide
what stays. The runbook improves without you having to write every line.

**Lesson:**

The 15 minutes you spend on the Compound step aren't documentation time. They're debt
reduction. Every learning you write is a decision you never have to make again, a mistake
you never have to re-discover, a context re-establishment you never have to do.

At session 10 on the same codebase, you're not starting from scratch. You're standing on
50+ preserved decisions. That's compound interest on thinking.

I built a working demo that shows this across three explicit sessions. The GitHub template
is in the next article. For now: the pattern works, it's not complicated, and you can
start with a single entry in an empty `learnings.jsonl` after your very next session.

**Quick Reference:**
- Compound step happens at the END of every session (15 min)
- Write constraints, not observations ("never X" beats "I saw Y")
- Confidence 7-8 = observed once; 9-10 = confirmed across sessions
- Low confidence (≤6) = the fix will be harder than you think
- Wrong learnings cause wrong decisions — delete them, don't just note them

---

[ASTGL CONTENT]

**Series:** Compound Engineering for Solo Builders — Part 2 of 3
**Title:** Building the GitHub Template That Teaches Compound Engineering
**Subtitle:** Fork this repo and start from a real baseline — 14 learnings, 3 session logs, zero empty files

**The Problem:**

I hate repos that start empty. You fork them, you get a directory tree and a README that
says "getting started," and then you have to figure out what a populated version looks
like. The template exists to show you the structure; it doesn't show you the structure
working.

For Compound Engineering, that's especially bad. The whole point is that learnings
accumulate over sessions. An empty `learnings.jsonl` doesn't show you anything. You
need to see it with actual entries, written across actual sessions, to understand what
you're building toward.

So I built the template differently. It starts full.

**The Setup:**

The repo (`compound-eng-workflow-guide`) contains a working demo project called `pulse`
— a personal health metrics CLI that reads a CSV log and prints a rich terminal dashboard.
Simple enough to understand in 10 minutes. Complex enough to generate genuine learnings.

Three sessions are pre-built:

- **Session 1:** Naive CSV reader, `sys.argv`, no error handling. Tests document bugs
  with a `_KNOWN_BUG` suffix. 7 learnings recorded.
- **Session 2:** Opens with CLAUDE.md's Known Patterns table. Three Session 1 learnings
  drive the Session 2 design. The `csv-blank-line-handling` learning reveals a fix that
  requires abandoning `DictReader` entirely — exactly what the confidence score of 7 (not 9)
  was warning about. 5 learnings added/updated.
- **Session 3:** Opens CLAUDE.md, reads the architecture note left in Session 2: *"plugins
  receive `(datetime.date, float)` tuples — no date parsing inside plugins needed."* That
  decision was made in Session 2's Compound step. Session 3 implements the plugin
  architecture correctly on the first attempt because the constraint was already there.

That last point is the compound payoff. Session 3 didn't re-deliberate the date parsing
decision. It was already decided. You can't measure the time you didn't spend. You can
observe that 3 sessions and 14 learnings produced 15 passing tests and a plugin architecture
with zero date-parsing bugs.

**The Solution:**

Here's the repo structure that matters most:

```
.claude/projects/compound-eng-demo/
├── learnings.jsonl    ← 14 entries across 3 sessions
└── timeline.jsonl     ← session event log

sessions/
├── SESSION-001-bootstrap.md    ← Brainstorm → Compound, Session 1
├── SESSION-002-add-filter.md   ← Brainstorm → Compound, Session 2
└── SESSION-003-refactor.md     ← Brainstorm → Compound, Session 3

CLAUDE.md              ← evolves across sessions; Known Patterns table
```

The `learnings.jsonl` is the artifact. Everything else is the story of how it got there.

Two sample entries to understand what you're looking at:

```json
{
  "skill": "gstack-review",
  "type": "pitfall",
  "key": "csv-blank-line-handling",
  "insight": "Python 3.13 DictReader silently drops blank rows — they never appear in the iteration loop. Real fix: read raw lines first, detect blanks by checking stripped content, then parse via csv.reader. Try/except won't help; there's nothing to catch.",
  "confidence": 8,
  "source": "observed",
  "files": ["demo/src/pulse.py"]
}
```

That entry started at confidence 7. Session 2 upgraded it to 8 after the fix was confirmed.
The upgrade is the signal that the pattern generalized.

```json
{
  "skill": "gstack-review",
  "type": "pattern",
  "key": "learnings-as-constraints-not-observations",
  "insight": "Write constraints ('parse dates at load time'), not observations ('I saw a bug with dates'). Constraints inject into next-session planning as guardrails. Observations require re-interpretation.",
  "confidence": 9,
  "source": "observed"
}
```

That one came out of Session 3's Compound step after we confirmed that the
`date-parsing-local-vs-utc` constraint (written in Session 1) applied cleanly to
the Session 3 plugin interface without any re-deliberation. The constraint worked.
Hence confidence 9.

**The `_KNOWN_BUG` pattern:**

The test file progression is worth reading. Session 1 has this:

```python
def test_blank_line_handling_KNOWN_BUG():
    """
    WHAT: Blank lines cause data loss or crash.
    KNOWN: 'csv-blank-line-handling' pitfall learning.
    FIX: Session 2 — wrap CSV parsing, log skipped rows.
    """
```

Session 2 renames it:

```python
def test_blank_line_handling_FIXED():
```

Session 3 adds plugin tests that reference the contract established in Session 1:

```python
def test_plugin_interface_stable_with_date_objects():
    """
    WHY: date-parsing-local-vs-utc learning — this is the Session 3 payoff.
    Plugin interface was designed assuming load_log() already parsed dates.
    """
```

The test file is a changelog you can run.

**Why This Matters:**

An example skill is included at `skills/pulse-review/SKILL.md`. It's 50 lines. It has a
checklist that references 4 learnings by key. A "how to adapt" section that's 4 bullet
points. Nothing in it requires gstack — it's a plain Claude Code command file.

That's the template showing its own pattern: you don't need a framework to start. You
need a structure and the discipline to fill it session by session.

**Lesson:**

To adapt this template to your own project:

1. Fork the repo
2. Replace `demo/` with your actual project
3. Clear `learnings.jsonl` (keep the schema; clear the entries)
4. Update `CLAUDE.md` with your project purpose and key commands
5. Copy a session log template and run Session 1

At session end, write 3-5 learnings. That's all. By session 5, you'll have 20+
entries and your agent will be making decisions that took you an hour to reach in
session 1, in seconds.

**Quick Reference:**
- `./show-learnings.sh` — view all learnings (no gstack needed, just jq)
- `./show-learnings.sh pitfall` — filter by type
- `./show-learnings.sh high` — show high-confidence (≥8) only
- Session logs go in `sessions/SESSION-NNN-description.md`
- CLAUDE.md Known Patterns table gets updated at every Compound step
- Tests with `_KNOWN_BUG` suffix = migration guide for next session

---

[ASTGL CONTENT]

**Series:** Compound Engineering for Solo Builders — Part 3 of 3
**Title:** Local LLMs + Claude Code: The Mac Studio Hybrid Workflow
**Subtitle:** Which models to run in Ollama, when to use them, and how Claude stays the orchestrator

**The Problem:**

Every time I talk about using Claude Code for a project, someone asks: "Isn't that
expensive?" And the honest answer is: it depends on how you route the work.

If you use Claude for everything — every code generation, every draft, every refactor
iteration — yes, it adds up fast. But that's not how I actually work, and it's not how
the Mac Studio was designed to be used.

I have an M3 Ultra with 192 GB unified memory. That machine can run a 70B parameter model
locally with room to spare. At 60 watts under load, eight hours of overnight autoresearch
costs me about five cents in electricity. The same run on a frontier API would cost $15-30.

The economics aren't even the main reason to run locally. The latency is. `qwen3:8b`
responds in under a second. That's interactive. You can iterate on code at conversational
speed with a local model, then bring Claude in for the judgment calls.

**The Setup:**

The hybrid workflow has one rule:

> "Claude reads the playbook. Local models do the work."

Local models handle generation — the fast, cheap, iterative part. Claude handles
orchestration and the Compound step — the judgment-heavy part where you're deciding
what's worth keeping and what should be codified as a constraint.

The model routing table:

| Task | Model | Why |
|------|-------|-----|
| Security/content checks | `qwen3:8b` | Fast, deterministic, low memory |
| Code generation, first drafts | `qwen3:32b-fast` | Primary workhorse |
| Code review, refactoring suggestions | `qwen2.5-coder:32b` | Code-specialized |
| Multi-step reasoning, overnight jobs | `deepseek-r1:70b` | Background only — slow but deep |
| Orchestration, compound step, final review | Claude API | Judgment, not generation |

This table lives at `docs/local-llm-routing.md` in the template repo.

**The Solution:**

Setting up Ollama on a Mac Studio is genuinely simple:

```bash
brew install ollama
ollama pull qwen3:8b
ollama pull qwen3:32b-fast
ollama pull qwen2.5-coder:32b
```

Open the Ollama menu bar app once to enable auto-start. Done. It runs as a local HTTP
server at `localhost:11434`.

For the hybrid workflow, the session structure looks like this:

```
Morning: Planning
  └── Claude Code (reads CLAUDE.md + learnings, brainstorms, writes plan)

Morning/Afternoon: Work
  └── qwen3:32b-fast (code generation, feature building)
  └── qwen2.5-coder:32b (code review, "catch the edge cases I missed")

Evening: Compound Step
  └── Claude Code (reviews session, proposes learnings, updates CLAUDE.md)

Optional overnight: Autoresearch loop
  └── deepseek-r1:70b (variant generation against a defined metric)
```

The Compound step is where the two frameworks connect. Karpathy's Autoresearch
pattern — one file, one metric, keep/revert — can run as a local overnight job using
`deepseek-r1:70b`. Instead of optimizing a training script, you optimize a skill file
or a prompt file from your `.claude/commands/` directory.

Define a small set of test cases (files with known issues your skill should catch).
Run 50-100 variants overnight. Keep the variants that catch more issues; revert the rest.
In the morning, run the Compound step on the winning variant with Claude.

The output of the overnight loop feeds directly into `learnings.jsonl` the next day.
Autoresearch becomes the Work step in a Compound Engineering session.

**Why This Matters:**

I've been running this stack — Mac Studio + Ollama + Claude Code — for several months
now. The thing that surprised me most wasn't the cost savings. It was the workflow change.

When generation is local and free, you iterate differently. You don't compose the perfect
prompt. You generate 10 variants in 30 seconds and pick the best one. The economics change
the psychology.

The Compound step stays expensive (Claude API) on purpose. That's the judgment layer. I
want a frontier model deciding what goes into my `learnings.jsonl` — what's worth
remembering, what's a real pattern versus a one-time quirk. That's not a task I want to
run on a 32B model.

The real learning from the stoicism-agent project applies here directly. I wrote this
in my learnings after the first overnight autoresearch run:

> *"The fork between MLX and Ollama for autoresearch comes down to one question: do you
> need to modify model weights? MLX if yes. Ollama if you're doing prompt-level
> optimization only. For skill file autoresearch, Ollama is the right choice."*

Same principle scales to any overnight optimization loop. Pick the tool that matches
the task. Don't reach for fine-tuning when prompt optimization will do.

**Lesson:**

Your weekend workflow on a Mac Studio:

1. **Friday night:** set up the overnight autoresearch loop on one skill or prompt file.
   Define your metric (what does a good version of this skill catch or produce?). Let
   `deepseek-r1:70b` run variants while you sleep.

2. **Saturday morning:** review the overnight results with Claude Code. Run the Compound
   step on the best performers. Write 2-3 learnings to `learnings.jsonl`.

3. **Saturday/Sunday:** build. Route generation to `qwen3:32b-fast`. Route code review
   to `qwen2.5-coder:32b`. Bring Claude in for planning and the compound step.

4. **Sunday evening:** run the Compound step for the weekend. Update CLAUDE.md Known
   Patterns. Check the test suite. Commit.

Total Claude API spend for a full weekend of this: $2-3. Total local compute: whatever
your electricity bill looks like for 60W over a weekend.

The Mac Studio paid for itself in API savings after about 14 months of this workflow.
More importantly, the learnings file from 6 months of consistent Compound Engineering
sessions is now the most valuable artifact in my projects. Not the code — the learnings.

The code can be rewritten. The 200+ preserved decisions cannot.

**Quick Reference:**
- `brew install ollama` → `ollama pull qwen3:32b-fast` → done
- Ollama serves at `http://localhost:11434`
- Use local models for generation; Claude for judgment + compound step
- M3 Ultra (192 GB): can run multiple 32B models simultaneously
- M2 Ultra (76 GB): comfortable with one 32B + one 8B concurrently
- `deepseek-r1:70b` needs 64 GB+ — overnight jobs only, too slow for interactive use
- Route Autoresearch overnight loops to `deepseek-r1:70b` for skill/prompt optimization
- Full model routing table: `docs/local-llm-routing.md` in the template repo
