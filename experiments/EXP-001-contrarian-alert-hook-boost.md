---
id: EXP-001
slug: contrarian-alert-hook-boost
status: active
created: 2026-06-22
---

# EXP-001 — Contrarian + Alert Hook Boost

## Hypothesis

LinkedIn posts that open with interrupt-style hook patterns (`contrarian` or `alert`) generate
higher Engagement Score than the current equal-rotation baseline across all 8 hook patterns.

Interrupt patterns force a cognitive reaction — readers must either agree, disagree, or check
whether the "mistake" applies to them. That friction converts scrollers into commenters, which
is the highest-weight input in the scoring formula (comments × 30).

## Variable

`hook_pattern` selection weight (one variable only — all other generator rules unchanged).

## Variant rule

During the test window, when selecting a hook pattern the agent must:
- Give `contrarian` and `alert` **2× weight** each (2 shares each in the selection pool)
- Leave all other patterns at 1× weight
- Effective pool: contrarian(2) + alert(2) + myth-bust(1) + truth(1) + blunt(1) + question(1) + story(1) + checklist(1) = 10 shares
- Combined probability of contrarian or alert: ~40% vs ~25% at equal rotation

The cadence constraint ("don't use same pattern two days in a row") still applies.

## Windows

- **Baseline period:** 2026-06-01 to 2026-06-14 (n=14 published posts; engagement data to be entered by Josh in Notion)
- **Test window start:** 2026-06-22
- **Test window end:** 2026-06-29

## Expected impact

Primary movers: `reactions` and `comments` components of Engagement Score.
Impression count expected to be neutral (reach is algorithm-driven).

## Decision

decision: (pending — close after 2026-06-29 with n≥5 test posts)
baseline_median: (TBD — requires Josh to fill in Notion engagement fields for Jun 1–14 posts)
test_median: (TBD)
commit_note: (TBD)

## Generator commit

SHA of the generator.md change encoding this variant: (set when PR merges)
