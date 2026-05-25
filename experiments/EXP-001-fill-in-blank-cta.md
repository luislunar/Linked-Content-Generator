---
id: EXP-001
slug: fill-in-blank-cta
hypothesis: "Fill-in-the-blank CTA drives more comments than open-ended opinion questions because it reduces composition friction"
variable: cta_style
baseline_start: 2026-05-11
baseline_end: 2026-05-25
test_window_start: 2026-05-26
test_window_end: 2026-06-01
status: active
decision:
baseline_median:
test_median:
commit_sha:
---

## Hypothesis

Open-ended CTAs ("What's been your experience with...?") require readers to compose a response from scratch. Fill-in-the-blank CTAs ("Fill in the blank: ________ is the reason I haven't applied yet.") provide structure — the reader only needs to complete a sentence. This lower composition barrier is predicted to increase comment rate. Since comments carry a ×30 weight in the Engagement Score formula, even a modest lift translates to a large score delta.

## Variable

`cta_style`: From the rotation in `generator.md`, use **only** the fill-in-the-blank pattern for the test window.

## Variant rule

Every post published 2026-05-26 through 2026-06-01 must close with a fill-in-the-blank CTA using one of these two patterns:

- `"Fill in the blank: ________ is the reason I haven't [topic-relevant action] yet."`
- `"Fill in the blank: The biggest thing holding small businesses back from [topic] is ________."`

Tailor the blank to the post's topic. Do not use experience-share, action-prompt, myth-drop, honest-check, or opinion CTA styles during this window.

## Baseline

Baseline period: 2026-05-11 to 2026-05-25. Posts in this window used the full CTA rotation (experience-share, opinion, action-prompt). Baseline median will be computed at close from Notion engagement data.

**Note:** As of experiment creation (2026-05-25), engagement data has not been entered in Notion for most published posts — all scores show 0. Baseline and test medians require engagement numbers to be backfilled by Josh before the keep/revert rule can be applied meaningfully.

## Expected signal

Primary: comments (×30 in score formula)
Secondary: reactions (social validation of fill-in responses visible to network)

## Minimum sample

n ≥ 5 posts in the test window (2026-05-26 to 2026-06-01 = 7 days). Do not close early.
