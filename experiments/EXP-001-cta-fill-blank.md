---
id: EXP-001
slug: cta-fill-blank
status: active
hypothesis: "Posts ending with a fill-in-the-blank CTA generate more comments than the 6-style rotation."
variable: cta_style
baseline_period_start: 2026-05-01
baseline_period_end: 2026-05-07
test_window_start: 2026-06-30
test_window_end: 2026-07-06
generator_commit: ""
decision: ""
baseline_median: ""
test_median: ""
commit_note: ""
---

# EXP-001: Fill-in-the-blank CTA

## Hypothesis

Posts ending with a **fill-in-the-blank CTA** ("Fill in the blank: ________ is [X]") generate more
comments than the current 6-style rotation because blank-filling lowers the cognitive barrier to
responding — readers supply one word or phrase rather than formulating a full opinion from scratch.

LinkedIn algorithms also surface posts with early comment activity; a low-friction CTA that
triggers faster first responses may compound into higher impressions.

## Variable

**CTA style** — one of the 6 styles in `generator.md > CTA rules`.

| | Baseline | Variant |
|---|---|---|
| CTA style | 6-style rotation (equal weight) | Fill-in-the-blank only |

## Variant rule

Every post in the test window must close with a fill-in-the-blank CTA in one of these forms:

> "Fill in the blank: ________ is the reason I haven't [topic-action] yet."
> "Fill in the blank: ________ was the part of [topic] I didn't expect."
> "Fill in the blank: The one thing nobody warned me about GovCon was ________."

Examples by topic:
- SAM: "Fill in the blank: ________ is why I haven't renewed my SAM registration yet."
- GSA basics: "Fill in the blank: ________ was the part of the GSA process I didn't expect."
- Pricing: "Fill in the blank: The pricing mistake I almost made was ________."
- Pipeline: "Fill in the blank: ________ is what I wish I knew before chasing federal contracts."

Do NOT use experience-share, action prompt, myth drop, honest check, or opinion CTA styles
during the test window.

## Expected movement

Higher comment rate → higher Engagement Score (comments = 30× weight).
No expected impact on impressions or reactions.

## Keep/revert rule (from scoring.md)

- **Keep** if: median(test) > median(baseline) by ≥15%, OR p75(test) > p75(baseline) AND median
  not worse by >10%.
- **Revert** if: test median not better, or worse than baseline by >10%.

## Data notes

Baseline period (May 1–7, 2026): 7 published posts in Notion, all showing score=0 —
engagement metrics (impressions, reactions, comments) have not yet been entered into Notion.
Experiment evaluation will require those fields to be populated before or by 2026-07-06.

If n < 5 posts in the test window by 2026-07-06, the weekly-research agent must extend
`test_window_end` by 7 days rather than closing the experiment.
