# Local LLM Routing Guide — Mac Studio Hybrid Workflow

## The Principle

> "Claude reads the playbook. Local models do the work."

Claude Code handles orchestration and the Compound step (judgment-heavy work).
Local models via Ollama handle generation (cheap, fast, iterative work).

This hybrid splits the cost curve: ~90% of token generation runs locally for free;
~10% — the judgment, review, and compound steps — routes to Claude via API.

---

## Model Routing Table

| Task type | Model | Why |
|-----------|-------|-----|
| Security/content checks | `qwen3:8b` | Fast, deterministic, low memory |
| Quick drafts, first-pass code | `qwen3:32b-fast` | Primary workhorse — good quality/speed balance |
| Code review, refactoring suggestions | `qwen2.5-coder:32b` | Code-specialized, strong at explaining decisions |
| Multi-step reasoning, overnight jobs | `deepseek-r1:70b` | Slow but deep — use for background tasks only |
| Orchestration, compound step, final review | Claude (API) | Judgment, not generation — keep this expensive but infrequent |

---

## Mac Studio Setup

### Memory requirements

| Model | Memory needed | Notes |
|-------|--------------|-------|
| `qwen3:8b` | ~6 GB | Fast load, low impact |
| `qwen3:32b-fast` | ~22 GB | Fits comfortably in 48 GB unified memory |
| `qwen2.5-coder:32b` | ~22 GB | Same footprint as qwen3:32b |
| `deepseek-r1:70b` | ~45 GB | Needs 64 GB+ for comfortable operation |

M3 Ultra with 192 GB can run multiple 32B models simultaneously. M2 Ultra (76 GB)
handles `qwen3:32b` + `qwen2.5-coder:32b` concurrently.

### Install Ollama

```bash
brew install ollama
```

### Pull the recommended models

```bash
ollama pull qwen3:8b
ollama pull qwen3:32b-fast    # alias for the speed-optimized Qwen3 32B
ollama pull qwen2.5-coder:32b
# deepseek-r1:70b only if you have 64 GB+ RAM:
# ollama pull deepseek-r1:70b
```

### Auto-start Ollama on login (launchctl)

```bash
# Start Ollama now
ollama serve &

# Or configure as a launchd service for auto-start:
# ~/.config/systemd/user/ollama.service (Linux)
# On macOS, Ollama has a menu bar app that handles auto-start.
# Just open Ollama.app and it starts serving.
```

### Verify models are running

```bash
ollama list
curl http://localhost:11434/api/tags | jq '.models[].name'
```

---

## Compound Engineering Integration

In a Compound Engineering workflow, local models handle the **Work** step.
Claude handles the **Compound** step.

```
Session Start
    └── Claude (via Claude Code) reads CLAUDE.md + learnings.jsonl
                                    ↓
          Brainstorm + Plan (Claude + human)
                                    ↓
               Work (route to local model via Ollama)
                  - qwen3:32b-fast for code generation
                  - qwen2.5-coder:32b for code review
                                    ↓
              Review (human + Claude Code)
                                    ↓
           Compound step (Claude judges what to record)
              - Writes learnings.jsonl entries
              - Updates CLAUDE.md Known Patterns table
```

**Why Claude for the Compound step?**

The Compound step requires judgment: deciding whether a pattern is general enough
to keep, whether a learning supersedes an existing one, and whether a confidence
score should go up or down. This is exactly the task where frontier models have a
significant edge. Local 32B models can generate; Claude can judge.

---

## The Karpathy Bridge: Overnight Autoresearch Loops

Karpathy's Autoresearch pattern — one file, one metric, fixed time budget, keep/revert
— maps cleanly onto local model overnight jobs.

Instead of optimizing a training script, apply the same loop to your **skill files**:

```bash
# Run an overnight loop: optimize pulse-review/SKILL.md
# Each iteration: modify → evaluate (does the review catch real issues?) → keep/revert

# Pseudocode for the autoresearch loop
while budget_remaining:
    variant = local_model.generate_variant(skill_file)
    score = evaluate_skill(variant, test_cases)
    if score > baseline:
        git_add(variant)
        baseline = score
    else:
        git_reset()
```

**What model to use:** `deepseek-r1:70b` for overnight loops. It's slow (~30s/response)
but its reasoning depth produces better variants. Budget: 8 hours × 30s per attempt =
~960 attempts max on one skill file.

**The metric:** Did the skill catch the issues in a known-bad code sample?
Define a small set of "test cases" — files with known problems — and score each
variant on recall (how many issues does it find?).

---

## Your Weekend Workflow

| Time | Task | Model |
|------|------|-------|
| Morning: planning | Read CLAUDE.md, brainstorm, write plan | Claude Code |
| Morning: first code | Initial implementation, first draft | `qwen3:32b-fast` |
| Afternoon: iteration | Bug fixing, refactoring, variants | `qwen3:32b-fast` |
| Afternoon: code review | Check conventions, catch edge cases | `qwen2.5-coder:32b` |
| Evening: compound | Write learnings, update CLAUDE.md | Claude Code |
| Overnight (optional) | Autoresearch loop on a skill or prompt file | `deepseek-r1:70b` |

Total API spend per weekend session: 2-3 Claude Code sessions ≈ a few cents.
Total local compute: everything else.

---

## Cost Reference

API cost estimates (Claude Sonnet 4.6, mid-2026 pricing):
- One Claude Code planning session (~50K tokens in + 10K out): ~$0.15-$0.25
- One compound step (~5K tokens): ~$0.02-$0.05
- Typical weekend (3-4 sessions + compound steps): ~$1-2 total

Local model cost: electricity. An M3 Ultra drawing 60W for 8 hours = ~$0.05 at
typical US electricity rates.

The hybrid approach isn't just cost savings — it's latency. `qwen3:8b` responds in
under 1 second. `qwen3:32b-fast` responds in 3-8 seconds. That's interactive.
Claude API latency is similar, but the cost adds up fast at that iteration speed.
