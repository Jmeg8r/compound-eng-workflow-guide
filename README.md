# Compound Engineering Workflow Guide

**A GitHub template demonstrating Compound Engineering for solo builders.**

This repo is not empty. It starts with:
- **14 learnings** from 3 simulated sessions
- **3 session logs** showing the full Brainstorm → Compound cycle
- **A working demo project** (`pulse` — a personal health metrics CLI)
- **An example skill** showing a minimal Claude Code skill file

Fork it. Replace `pulse` with your project. Start Session 4.

---

## Quick Start

```bash
git clone <your-fork>
cd compound-eng-workflow-guide

# See what the previous sessions learned
./show-learnings.sh

# Run the demo CLI
pip install rich
python demo/src/pulse.py demo/sample-data.csv

# Run the tests
python -m pytest demo/tests/ -v
```

No gstack required. `show-learnings.sh` needs only `jq`.

---

## What Is Compound Engineering?

Every Claude Code session starts fresh. The agent re-explains context, re-debates
architecture, re-discovers bugs you already fixed. Compound Engineering solves this:

```
Brainstorm → Plan → Work → Review → Compound
                                        ↓
                              learnings.jsonl
                                        ↓
                    Next session loads learnings automatically
                                        ↓
                         Better decisions without re-deliberation
```

The **Compound step** (after every session) writes non-obvious decisions, gotchas,
and patterns into `learnings.jsonl`. The next session reads them. Decisions
persist. Cognitive load decreases. Your codebase gets smarter about itself.

---

## Repo Structure

```
compound-eng-workflow-guide/
├── CLAUDE.md                          # Claude Code context — evolves across sessions
├── show-learnings.sh                  # View learnings without gstack (jq only)
│
├── .claude/projects/compound-eng-demo/
│   ├── learnings.jsonl                # 14 pre-seeded learnings from 3 sessions
│   └── timeline.jsonl                 # Session timeline log
│
├── demo/                              # The pulse CLI (teaching vehicle)
│   ├── src/pulse.py                   # Python CLI — read in session order to see compound payoff
│   ├── tests/test_pulse.py            # 15 tests, traces from _KNOWN_BUG → fixed
│   └── sample-data.csv                # Ready to use immediately
│
├── sessions/                          # Full Brainstorm → Compound cycle logs
│   ├── SESSION-001-bootstrap.md       # Naive baseline, 7 initial learnings
│   ├── SESSION-002-add-filter.md      # argparse, rich, error handling, 5 new learnings
│   └── SESSION-003-refactor.md        # Plugin architecture, compound payoff
│
├── docs/
│   ├── compound-cycle.md              # The 5-step loop explained
│   ├── learnings-schema.md            # learnings.jsonl field reference
│   └── local-llm-routing.md           # Ollama + Claude Code hybrid workflow
│
└── skills/pulse-review/SKILL.md       # Minimal example skill (~50 lines)
```

---

## The Three-Session Story

Read `demo/src/pulse.py` in git history order to see compound engineering in action.

**Session 1:** Naive CSV reader. Intentional gaps (no error handling, `sys.argv`). Tests
document bugs with `_KNOWN_BUG` suffix. 7 learnings recorded.

**Session 2:** Opens with CLAUDE.md's Known Patterns table. Three learnings directly drive
design: `csv-blank-line-handling` → rewrite CSV parsing; `flat-main-before-argparse` →
refactor to argparse; `date-parsing-local-vs-utc` → parse dates at load time.
Result: `--filter`, `--days`, rich output, error handling. 5 new learnings.

**Session 3:** Opens CLAUDE.md. The last note says: *"Key learning to apply:
`date-parsing-local-vs-utc` already done — plugins receive `(datetime.date, float)` tuples.
No date parsing inside plugins needed."* That sentence was written in Session 2.
Session 3 designs the plugin interface correctly on the first attempt because the
constraint was already decided. That's the compound payoff.

---

## Using This Template

### 1. Fork and rename

```bash
gh repo create my-project --template <this-repo> --public
cd my-project
```

### 2. Replace the demo project

- Replace `demo/` with your actual project
- Update `demo/src/pulse.py` → your code
- Update `demo/tests/test_pulse.py` → your tests
- Clear `demo/sample-data.csv`

### 3. Reset the learnings

Keep the schema, clear the data:

```bash
echo "" > .claude/projects/compound-eng-demo/learnings.jsonl
echo "" > .claude/projects/compound-eng-demo/timeline.jsonl
```

Rename `compound-eng-demo` to match your project slug.

### 4. Update CLAUDE.md

Edit `CLAUDE.md`:
- Project purpose: one sentence about your project
- Key commands: how to run and test your project
- Compound Engineering Setup: update the learnings path

### 5. Start Session 1

Copy `sessions/SESSION-001-bootstrap.md` as a template. Work through:
- Brainstorm (read CLAUDE.md first, even if it's mostly empty)
- Plan (steps + verify checks)
- Work
- Review
- Compound (write your first learnings — even 3-4 entries is enough to start)

### 6. Start Session 2

Open CLAUDE.md. Read the Known Patterns table. Notice which learnings are relevant
to what you're building. Then build.

---

## With Gstack

If you have gstack installed:

```bash
# At session end, run the compound step via skill
/gstack-learn

# Review and prune learnings
/gstack-learn show
/gstack-learn prune

# At session start, gstack's preamble injects the top learnings automatically
```

The learnings in `.claude/projects/<slug>/learnings.jsonl` are read by gstack's
preamble injection. Future sessions get the learnings loaded into context without
any manual action.

---

## Rolling Out to Existing Projects (`scaffold/`)

The fork-and-rename flow above is for *new* projects. To add this workflow to a repo that
**already exists**, use the idempotent scaffolder in [`scaffold/`](scaffold/):

```bash
scaffold/compound-init.sh /path/to/project          # full setup
scaffold/compound-init.sh /path/to/project --light   # skip sessions/ if the repo already has one
```

It installs only the **committed half** of the loop — a managed `<!-- COMPOUND -->` block in
`CLAUDE.md` (with a regenerating "Known Patterns" digest table), a `sessions/` cycle template,
and slug-aware `show-learnings.sh` + `refresh-digest.sh`. The **working store stays in gstack**
(`~/.gstack/projects/<slug>/learnings.jsonl`, auto-loaded at session start), so there is no
second learnings file to keep in sync.

Re-running is safe (the managed block is inserted once, never duplicated). At a session's
Compound step, record constraints with `/gstack-learn add`, then `./refresh-digest.sh` to
refresh the committed table. See [`scaffold/README.md`](scaffold/README.md) for details.

> First rolled out to 15 active projects on 2026-06-20.

---

## Reading List

- [`docs/compound-cycle.md`](docs/compound-cycle.md) — the 5-step loop explained
- [`docs/learnings-schema.md`](docs/learnings-schema.md) — field reference for learnings.jsonl
- [`docs/local-llm-routing.md`](docs/local-llm-routing.md) — Ollama + Claude hybrid for Mac Studio
- [ASTGL — "The AI Dev Workflow That Gets Smarter Every Session"](#) — Part 1 of the series
- [Ken Huang: Compound Engineering vs. Karpathy's Autoresearch](https://kenhuangus.substack.com/p/compound-engineering-vs-gstack-vs) — the conceptual foundation

---

## License

MIT. Fork freely, compound aggressively.
