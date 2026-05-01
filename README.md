# Linked-Content-Generator

Daily LinkedIn lead-magnet machine for Josh Ladick / GSA Focus.

Every day an autonomous agent drafts one lead magnet (Notion page), writes a LinkedIn post, records a 7-second scroll-through video with a branded overlay, and queues it in Blotato for publishing. A weekly "autoresearch" pass reads engagement data from Notion and mutates the generator to improve over time.

Modeled after [`karpathy/autoresearch`](https://github.com/karpathy/autoresearch):

| autoresearch | this repo |
|---|---|
| `prepare.py` (fixed constants) | [`brand-context.md`](brand-context.md) |
| `train.py` (agent-edited) | [`generator.md`](generator.md) |
| `program.md` (behavior) | [`program.md`](program.md) |
| Validation bits-per-byte | Engagement score — see [`scoring.md`](scoring.md) |

## How it runs

```
┌─ daily cron (06:00 ET) ──────────────────────────────┐
│  .github/workflows/daily-magnet.yml                  │
│    → claude -p .claude/commands/daily-magnet.md      │
│    → writes drafts/YYYY-MM-DD/, Notion magnet page   │
│    → opens PR "Draft: YYYY-MM-DD"                    │
└───────────────┬──────────────────────────────────────┘
                │  Josh reviews on phone, merges PR
                ▼
┌─ publish workflow (on merge to main) ────────────────┐
│  .github/workflows/publish.yml                       │
│    → Playwright records Notion page scroll           │
│    → ffmpeg burns Gotham/neon overlay                │
│    → Blotato API publishes to LinkedIn               │
│    → Notion row flips to status=published            │
└──────────────────────────────────────────────────────┘

┌─ weekly cron (Sun 20:00 ET) ─────────────────────────┐
│  .github/workflows/weekly-research.yml               │
│    → reads last 14d engagement from Notion           │
│    → claude -p .claude/commands/weekly-research.md   │
│    → edits generator.md, writes experiments/EXP-N    │
│    → opens PR "Research: EXP-N <hypothesis>"         │
└──────────────────────────────────────────────────────┘
```

## Secrets (GitHub repo → Settings → Secrets and variables → Actions)

- `ANTHROPIC_API_KEY`
- `NOTION_TOKEN`, `NOTION_POSTS_DB_ID`, `NOTION_MAGNETS_DB_ID`, `NOTION_EXPERIMENTS_DB_ID`
- `BLOTATO_API_KEY`, `BLOTATO_LINKEDIN_ACCOUNT_ID`

## Local dev

```bash
# copy example env
cp .env.example .env
# fill in the same values as GitHub secrets

# run one cycle locally
./scripts/run-claude.sh daily
```

See [`program.md`](program.md) for the full operational spec.
