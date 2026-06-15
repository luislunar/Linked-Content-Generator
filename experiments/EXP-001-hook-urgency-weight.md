---
id: EXP-001
slug: hook-urgency-weight
status: active
created: 2026-06-15
test_window_start: 2026-06-15
test_window_end: 2026-06-21
baseline_period_start: 2026-06-01
baseline_period_end: 2026-06-14
variable: hook_pattern rotation weights
---

## Hypothesis

Concentrating on high-urgency hooks (`alert`, `myth-bust`, `blunt`) will increase the median engagement score by ≥15% compared to even rotation across all 8 patterns, because the GovCon audience responds more to content that prevents costly mistakes (SAM lapses, missed deadlines, pricing errors) than to neutral or narrative hooks.

## Variable

Hook pattern weighting.

## Baseline rule (pre-experiment)

Rotate freely among all 8 hook patterns. Only hard constraint: don't repeat the same pattern two days in a row.

## Variant rule (active during test window)

Use `alert`, `myth-bust`, or `blunt` on **at least 5 of 7 days**. On the remaining 2 days, any other pattern is allowed. Never repeat the same pattern two days in a row (existing cadence rule still applies).

Rationale for the three selected patterns:
- **alert** — creates urgency around real compliance/registration risks ("This one mistake is quietly costing…")
- **myth-bust** — corrects misconceptions that directly cost the audience money or time
- **blunt** — hard facts stated plainly, no hedging — signals expertise and earns trust quickly

## Expected score movement

Primary: comments and reactions (bottom-funnel engagement). Secondary: impressions (if hook drives more shares/saves).

## Baseline period reference

Posts from 2026-06-01 to 2026-06-14 (the two weeks before this experiment starts). Engagement scores drawn from Notion Posts DB.

---

## Decision (to be filled in by weekly-research on or after 2026-06-22)

decision:
baseline_median:
baseline_p75:
test_median:
test_p75:
n_test_posts:
commit_note:
