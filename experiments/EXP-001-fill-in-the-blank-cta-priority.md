---
id: EXP-001
slug: fill-in-the-blank-cta-priority
status: active
created: 2026-07-13
test_window_start: 2026-07-14
test_window_end: 2026-07-20
baseline_start: 2026-07-01
baseline_end: 2026-07-13
generator_md_sha: (to be set when generator.md commit is made)
---

## Hypothesis

Exclusively using the "fill-in-the-blank" CTA style for 7 days will increase the comment rate per post compared to the current equal-rotation across 6 CTA styles.

**Why this should work:** Comments are weighted 30× in the Engagement Score formula — the highest leverage component before opt-ins. Fill-in-the-blank CTAs lower cognitive friction (the reader completes a sentence rather than generating an open-ended response), which is commonly associated with higher comment rates on LinkedIn. The GovCon niche audience (compliance-focused small business owners) is especially likely to respond to structured prompts like "Fill in the blank: ________ is why I haven't pursued my GSA Schedule yet."

## Variable

- **What changes:** CTA style — override to `fill-in-the-blank` exclusively during the test window. All other variables (hook pattern, format, topic, template) follow normal rotation rules.
- **What stays constant:** hook pattern rotation, topic rotation, format rotation, image template.

## Variant rule (for generator.md)

During the test window (2026-07-14 to 2026-07-20), the daily run MUST use the "fill-in-the-blank" CTA:

> `"Fill in the blank: ________ is [relevant blocker/action for the day's topic]."`

Do not pick any other CTA style from the rotation list while this experiment is active.

## Test window

- Start: 2026-07-14
- End: 2026-07-20 (7 days)
- Minimum posts required to close: 5

## Baseline period

- Start: 2026-07-01
- End: 2026-07-13
- Note: Engagement scores for the baseline period must be entered in Notion before this experiment can be evaluated. If n < 5 scored baseline posts exist at evaluation time, extend the window.

## Keep / revert rule

Per `scoring.md`:
- **Keep** if: n_test ≥ 5 AND (median_test > median_baseline × 1.15 OR (p75_test > p75_baseline AND median_test > median_baseline × 0.90))
- **Revert** otherwise

## Results (filled in by `/weekly-research` when closing)

```
decision:
baseline_n:
baseline_median:
baseline_p75:
test_n:
test_median:
test_p75:
commit_note:
```
