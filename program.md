# Program — agent behavior

This file tells the agent HOW to run. It is edited by humans. The agent must not modify this file during daily runs.

## Invariants

1. **Never edit `brand-context.md`** — fixed constants.
2. **Only `/weekly-research` may edit `generator.md`** — daily runs read it, never write it.
3. **Only one variable changes per experiment.** Isolate so we can attribute score deltas.
4. **Every draft lists its hypothesis.** `drafts/YYYY-MM-DD/hypothesis.md` names the active experiment ID and the variable under test.
5. **Scoring is fixed** — defined in `scoring.md`. Do not change mid-experiment.

## Daily run (`/daily-magnet`)

Inputs: `brand-context.md`, `reference-posts.md`, `generator.md`, the most recent open experiment (if any), last 5 published posts (to avoid repetition), latest `research/reddit-trends-*.md` (if exists).

Steps:
1. Read `brand-context.md`, `reference-posts.md`, and `generator.md`.
2. Read the most recent `research/reddit-trends-*.md` file for trending topic inspiration (if one exists from the last 7 days).
3. Query Notion Experiments DB for `Status = active`. If one exists, apply its variant to the generation run.
4. Pick today's (topic, format, hook-pattern) from the rotation rules in `generator.md`, avoiding any (topic, format) combination used in the last 5 days.
5. Draft the LinkedIn post (hook, body bullets, community question). Follow the style in `reference-posts.md`: short hook, 3–6 bullet points with `→`, close with an open-ended community question. No lead magnet CTA — the goal is reactions and comments.
6. Draft the **image headline** — ≤8 words in ALL CAPS, punchy, designed for the 1080×1080 card. This is the hook distilled to a visual tagline. Store in `post.meta.json` as `image_headline`.
7. Write everything to `drafts/YYYY-MM-DD/`:
   - `post.md` — LinkedIn post text
   - `post.meta.json` — `{ image_headline, hook_pattern, format, topic, experiment_id }`
   - `hypothesis.md` — one paragraph: what is this draft testing, why, and which score components we expect to move
8. Via `notion-sync.py`: insert a Posts DB row with `status = draft` and all metadata populated.
9. Append a run log to `logs/run-YYYY-MM-DD.md`.

**The publish step is NOT part of the daily run.** It fires when Josh merges the PR, via `publish.yml`.

**No lead magnets.** Do not generate `magnet.md`. Do not call `notion-sync.py create-magnet`. The CTA is always a community question — never "comment X to get a PDF."

## Weekly research run (`/weekly-research`)

Inputs: last 14 days of Posts DB rows (via Notion API), current `generator.md`, all experiments with `Status = active` whose test-period end is ≤ today.

Steps:
1. For any experiment whose test window has ended, apply the keep/revert rule from `scoring.md`. Write the decision into its Experiments DB row.
2. If an experiment is to be reverted: revert the relevant `generator.md` commit on a new branch.
3. Propose ONE new hypothesis. Candidates (prioritize the one with the most noisy baseline):
   - Hook pattern rotation weights (contrarian vs. list vs. story)
   - Format rotation weights (checklist vs. template vs. teardown)
   - Topic focus (e.g., "double-weight pricing topics for 2 weeks")
   - CTA style (comment-keyword vs. direct link vs. "reply with X")
   - Overlay text pattern (one-line punch vs. 2-line curiosity tease)
   - Magnet length (1-page vs. 3-page)
4. Write `experiments/EXP-NNN-<slug>.md`: hypothesis, variable, variant rule, test window (propose 7 days), baseline period reference.
5. Edit `generator.md` minimally to encode the variant.
6. Insert an Experiments DB row with `Status = active`.
7. Open a PR titled `Research: EXP-NNN <slug>` with the `generator.md` diff, the new experiment file, and a summary of the prior week's score distribution.

## Safety rails

- **Never publish from the agent directly.** Publishing only happens after Josh merges the PR.
- **Never write to `main`.** Always branch + PR.
- **Never touch `brand-context.md`, `reference-posts.md`, or `scoring.md` in any run** — if the agent thinks either needs to change, it must open a PR with a human-written commit message explaining why, and stop. These changes are human-only.
- **If Notion API fails, fail the run loudly** — do not silently continue. The git commit + PR should not be created without confirmed Notion state.
- **Never generate lead magnets or magnet pages.** The `magnet.md` file and Notion Magnets DB are deprecated. If a prior run log references magnets, ignore that pattern.
