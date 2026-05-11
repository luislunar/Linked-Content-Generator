---
id: EXP-001
slug: fillin-cta
status: active
hypothesis: Using the "fill-in-the-blank" CTA style exclusively drives more comments than the default rotating CTA mix, because it lowers the cognitive barrier to respond (reader fills in one phrase vs. composing a full reply).
variable: cta_style
variant: fill-in-the-blank exclusively — every post ends with "Fill in the blank: ________ is the reason I haven't [relevant action] yet."
baseline_period_start: 2026-05-01
baseline_period_end: 2026-05-10
test_window_start: 2026-05-11
test_window_end: 2026-05-17
decision:
baseline_median:
test_median:
commit_note:
generator_sha: pending
---

## Experiment: EXP-001 — Fill-in-the-blank CTA

**Axis tested:** CTA style (community question pattern)

**Baseline:** Posts from 2026-05-01 to 2026-05-10 using the default CTA rotation (experience-share, fill-in-the-blank, action prompt, myth drop, honest check, opinion).

**Variant:** For 2026-05-11 through 2026-05-17, every post ends with the fill-in-the-blank pattern:
> "Fill in the blank: ________ is the reason I haven't [relevant action for the post topic] yet."

**Why this axis:** Comments are weighted 30× in the Engagement Score formula. The fill-in-the-blank structure provides a concrete prompt with a low completion threshold — the reader only needs to supply a short phrase. Other CTA styles (experience-share, opinion) require more composition effort and typically yield fewer responses.

**Expected movement:** Increase in `Comments` count → higher Engagement Score. No expected impact on Impressions or Reactions.

**Keep/revert decision:** Applied per `scoring.md` after test_window_end. Requires n ≥ 5 posts.
