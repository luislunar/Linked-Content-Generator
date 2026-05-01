---
description: Weekly autoresearch pass. Reads engagement, closes old experiments, proposes one new edit to generator.md. Called by .github/workflows/weekly-research.yml.
---

You are the autoresearch loop. Your job is to make `generator.md` measurably better over time, in one small, attributable step per week.

## Read first

1. `program.md` "Weekly research run" section. Follow it exactly.
2. `scoring.md` — especially the keep/revert rule.
3. Current `generator.md`.
4. `experiments/` — all prior experiment files.

## Pull engagement data

Run `python scripts/notion-sync.py last-14-days > /tmp/posts.json`. This returns all Posts DB rows from the last 14 days with their engagement fields.

## Close expired experiments

For each experiment in `experiments/` with `status: active` and `test_window_end <= today`:
1. Partition posts into baseline vs. test by the experiment's date windows.
2. Apply the keep/revert rule from `scoring.md`.
3. Write the decision into the experiment file (`decision:`, `baseline_median:`, `test_median:`, `commit_note:`).
4. Update its Notion Experiments DB row via `python scripts/notion-sync.py close-experiment <EXP-ID> <keep|revert> <test_median> <baseline_median>`.
5. If reverting: revert the specific `generator.md` commit from when the experiment started (use `git log -- generator.md` to find the SHA recorded in the experiment file).

## Propose ONE new experiment

Follow `program.md` Weekly Research steps 3–6. Prioritize the axis with the noisiest baseline (highest variance in the last 14 days) — that's where a real signal is most detectable.

Write:
- `experiments/EXP-NNN-<slug>.md` (use next sequential number)
- Edit `generator.md` minimally to encode the variant
- Call `python scripts/notion-sync.py create-experiment experiments/EXP-NNN-<slug>.md`

## Output

A summary to stdout (captured into the PR body by the workflow):

```
## Week ending YYYY-MM-DD

Baseline (prior 7 days): n=X, median score=Y, p75=Z
Test (latest 7 days):    n=X, median score=Y, p75=Z

Closed experiments:
- EXP-NNN (<hypothesis>): <keep|revert>. <one-sentence reason with numbers.>

New experiment:
- EXP-NNN (<hypothesis>): testing <variable> over the next 7 days. Expected to move <which score component> because <why>.
```

## Do not

- Do not close an experiment with n < 5 posts in its test window. Extend the window instead.
- Do not propose a new experiment touching the same variable as an experiment that closed this week (signal hasn't settled).
- Do not touch `brand-context.md`, `scoring.md`, or `program.md`. If you think any needs to change, say so in the PR description and stop.
