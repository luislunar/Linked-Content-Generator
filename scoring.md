# Scoring — the single metric

Autoresearch works because experiments collapse to one number. Every `generator.md` edit is judged against **Engagement Score**.

## Formula

```
score = impressions
      + 10 * reactions
      + 30 * comments
      + 50 * opt_ins
```

Rationale: impressions are free (reach signal); reactions are low-cost commitment; comments require real intent; opt-ins are the business outcome. Weights bias the metric toward bottom-funnel action without ignoring top-of-funnel reach.

Implemented as a **Notion formula property** on the Posts DB so every row computes automatically once the five count fields are entered.

## Baselines (to be set after week 1)

| Percentile | Score |
|---|---|
| p50 |  ? |
| p75 |  ? |
| p90 |  ? |

Filled in after the first 7 published posts. Weekly research compares the trailing 7-day median against the baseline p50.

## Keep / revert rule for `generator.md` edits

A `/weekly-research` edit is **kept** iff:
- test period n ≥ 5 posts, AND
- median(test) > median(baseline) by ≥ 15%, OR
- p75(test) > p75(baseline) AND median not worse by > 10%

Otherwise the Experiments row is marked `Decision = revert` and the commit is reverted via a PR.

## Secondary signals (not optimized, but logged)

- Unsubscribe / hide rate (quality floor — if >2% on any post, flag that variant)
- Comment sentiment (qualitative review weekly)
- Downstream: downloads per opt-in, demo bookings (Josh tracks separately)

The autoresearch loop only optimizes **Engagement Score**. Everything else is a guardrail.
