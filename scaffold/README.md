# scaffold/ — Compound Engineering rollout kit

Idempotent scaffolder that adds the **committed half** of the compound loop to any repo.
The working store (capture + auto-load) is already handled by gstack per project slug
(`~/.gstack/projects/<slug>/learnings.jsonl`); these scripts add only what gstack does
*not* commit: a visible digest, session logs, and offline viewers.

## Usage

```bash
# Full scaffold (CLAUDE.md block + sessions/ + helper scripts)
scaffold/compound-init.sh /path/to/project

# Light: skip sessions/ for repos that already have one (e.g. claudeclaw)
scaffold/compound-init.sh /path/to/project --light
```

`compound-init.sh` is safe to re-run — it inserts the managed block (delimited by
`<!-- COMPOUND:START -->` / `<!-- COMPOUND:END -->`) only once and never touches your
existing CLAUDE.md content.

## What lands in each project

| File | Purpose |
|------|---------|
| `CLAUDE.md` managed block | "Compound Engineering Setup" + a "Known Patterns" digest table (between `<!-- LEARNINGS:START -->` / `<!-- LEARNINGS:END -->` markers) |
| `sessions/TEMPLATE.md` | Brainstorm → Plan → Work → Review → Compound cycle template |
| `show-learnings.sh` | Offline viewer of this repo's gstack learnings (`high` / `<type>` filters) |
| `refresh-digest.sh` | Regenerates the CLAUDE.md digest from the gstack store (run at Compound step) |
| `.coderabbit.yaml` | CodeRabbit review policy (assertive profile, request-changes workflow); copied only if absent |

## The loop

1. Work a session using `sessions/TEMPLATE.md`.
2. At the **Compound** step, record constraints with `/gstack-learn add`.
3. Run `./refresh-digest.sh` to update the committed table.
4. Commit the session log + refreshed CLAUDE.md. Next session, gstack auto-loads the
   learnings and the digest is visible in-repo.

Digest threshold is confidence ≥ 7 (override with `DIGEST_MIN_CONFIDENCE`).
