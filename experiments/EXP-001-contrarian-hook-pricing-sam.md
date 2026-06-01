# EXP-001 — Contrarian-first hook for pricing / SAM / vehicles topics

## Metadata

| Field | Value |
|---|---|
| `exp_id` | EXP-001 |
| `slug` | contrarian-hook-pricing-sam |
| `status` | active |
| `variable` | hook_pattern selection priority |
| `baseline_period` | 2026-05-19 – 2026-06-01 |
| `test_window_start` | 2026-06-02 |
| `test_window_end` | 2026-06-08 |
| `generator_commit` | (filled in after merge) |

## Hypothesis

Posts on `pricing`, `sam`, and `vehicles` topics default to `question` or `truth` hooks in the current rotation — both safe but low-friction. The `contrarian` hook ("Wrong question. Here's the right one.") creates cognitive challenge that forces a reaction: readers either nod hard or push back, and either response drives the Engagement Score (reactions + comments). Elevating `contrarian` to first-choice for these three high-stakes topics should lift median Engagement Score ≥15% in the 7-day test window vs. the 14-day baseline.

## Variable

**Baseline:** Hook pattern selected qualitatively per topic fit. In the 14-day baseline window (May 19 – June 1, 13 posts), `contrarian` appeared 1/13 times (8%).

**Variant:** For topics `pricing`, `sam`, `vehicles` — `contrarian` is the mandatory first-choice hook, unless the previous day's post also used `contrarian` (same-day-back-to-back still forbidden per cadence rules).

## Predicted mechanism

- `contrarian` hook reframes a common belief ("You don't need to negotiate your GSA price. ← Wrong question."), which creates pattern-interrupt.
- Pattern-interrupt on LinkedIn = thumb-stop = impressions growth, then reactions/comments from readers who either agree or disagree.
- Three of the nine topic slots (`pricing`, `sam`, `vehicles`) cover the most money-adjacent decisions in GovCon — the emotional stakes are highest, making contrarian framing most potent.

## Expected score component movement

Primary: `comments` (+1–2 per post avg), `reactions` (+3–5 per post avg)
Secondary: `impressions` (slight lift from higher-engagement signal)

## Keep / revert rule

Per `scoring.md`:
- **Keep** if: n ≥ 5 AND (median_test > median_baseline × 1.15 OR (p75_test > p75_baseline AND median_test ≥ median_baseline × 0.90))
- **Revert** otherwise

## Baseline data (as of 2026-06-01)

> **Note:** Notion engagement metrics (impressions, reactions, comments, opt-ins) are NULL for all posts in the baseline window — engagement data has not yet been entered into the Posts DB. Baseline medians below reflect formula output of 0 for all posts. Weekly research should re-evaluate once data is populated. The test-window close on 2026-06-08 should only proceed if baseline data has been entered.

| Metric | Value |
|---|---|
| `n_baseline` | 13 |
| `baseline_median` | 0 (data not yet entered) |
| `baseline_p75` | 0 (data not yet entered) |

## Decision (filled in at close)

| Field | Value |
|---|---|
| `decision` | (pending) |
| `test_median` | (pending) |
| `test_n` | (pending) |
| `commit_note` | (pending) |
