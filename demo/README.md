# pulse — Personal Health Metrics CLI

A teaching vehicle for Compound Engineering patterns. Three sessions, each
building on the last, with learnings compounding across sessions.

## Quick Start

```bash
cd demo
pip install -r requirements.txt
python src/pulse.py sample-data.csv
```

## Sessions

| Session | What changed | New learnings |
|---------|-------------|---------------|
| 1 (bootstrap) | Naive CSV reader, basic stats, sys.argv | 7 — pitfalls, patterns |
| 2 (filter + color) | argparse, rich output, error handling | +5 — architecture, operational |
| 3 (plugins) | Plugin architecture for metric types | +3 — patterns, architecture |

See `../sessions/` for full Brainstorm → Compound cycle logs.

## Log File Format

```csv
date,metric,value
2026-05-01,sleep_hours,7.5
2026-05-01,steps,8200
```

- `date`: YYYY-MM-DD
- `metric`: any string (snake_case recommended)
- `value`: numeric

## The Teaching Point

The bugs in Session 1 are intentional. They become the learnings.
The learnings become the design constraints for Session 2.
By Session 3, the agent is making architectural decisions that
reference Session 1's gotchas by name. That's compounding.
