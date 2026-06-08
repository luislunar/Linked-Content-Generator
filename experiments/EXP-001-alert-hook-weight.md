---
id: EXP-001
slug: alert-hook-weight
status: active
variable: hook_pattern_weight
hypothesis: >
  Increasing the frequency of the `alert` hook pattern to at least 3 posts per
  7-day window (vs. current ~1 in 8 uniform rotation) will raise median
  Engagement Score by ≥15% because GovCon professionals respond to urgency
  and compliance-risk framing — a SAM lapse or missed deadline has real
  financial consequences that make alert hooks viscerally compelling.
variant_rule: >
  During this experiment, select the `alert` hook pattern on any day where
  (a) it has not been used in the last 3 days, AND (b) the topic is one of
  `sam`, `compliance`, `pricing`, or `gsa_basics`.
  Maintain all other hook-pattern and topic rotation rules unchanged.
  Target: ≥3 alert-hook posts in the 7-day test window.
baseline_period_start: "2026-05-26"
baseline_period_end: "2026-06-07"
test_window_start: "2026-06-08"
test_window_end: "2026-06-14"
score_component_expected: comments + reactions (bottom-funnel)
generator_md_commit: ""
decision: ""
baseline_median: null
test_median: null
commit_note: ""
---

## Rationale

The `alert` hook pattern has appeared 0 times in the last 7 published posts
(Jun 1–7). The current rotation treats all 8 patterns equally, but LinkedIn
engagement research consistently shows that urgency/loss-aversion framing
outperforms informational framing for professional audiences with real
compliance stakes.

For the GSA Focus ICP — small business owners actively managing Schedule
registrations, SAM renewals, and certification maintenance — the cost of a
missed deadline is concrete (frozen payments, disqualification from bids).
The `alert` pattern speaks directly to that fear.

The expected mechanism: a higher share of `alert` hooks will increase
the stop-and-read rate, which should lift reactions (10× weight) and
comments (30× weight) more than impressions alone.

## Baseline note

Week 1 engagement data (Jun 1–7) has been published but metrics have not yet
been entered into the Notion Posts DB. The baseline median will be populated
once Josh enters the engagement fields for those 7 posts. If baseline n < 5
when the test window ends on 2026-06-14, extend the window by 7 days.
