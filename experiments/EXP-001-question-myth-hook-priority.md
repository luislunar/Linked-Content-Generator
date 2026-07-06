---
id: EXP-001
slug: question-myth-hook-priority
status: active
variable: hook_pattern
notion_page_id: 3950ac80-577a-81fe-9a37-c886e0c7dea8
hypothesis: >
  Forcing response-inviting hook patterns (question, myth-bust) for the topics
  where they are most natural increases comments because these hooks activate
  curiosity and recognition, generating first-hour engagement that signals
  LinkedIn's algorithm.
variant_rule: >
  For topics myths and certifications: hook_pattern MUST be myth-bust.
  For topics vehicles and pipeline: hook_pattern MUST be question.
  All other topic/post-type combinations: use existing rotation rules from generator.md.
baseline_period_start: 2026-06-29
baseline_period_end: 2026-07-06
test_window_start: 2026-07-07
test_window_end: 2026-07-13
generator_sha: TBD
---

# EXP-001 — question-myth-hook-priority

## Hypothesis

Forcing response-inviting hook patterns (`question` and `myth-bust`) for the topics where they are most natural increases **comments** and **reactions** relative to the even hook rotation in use during the baseline period.

- `myth-bust` activates recognition: "I thought this too" → comment
- `question` activates consideration: "Hmm, what IS my answer?" → comment or save

Both patterns front-load engagement cues in the first line, which LinkedIn's feed algorithm weights heavily.

## Variable

Hook pattern selection rules — forced assignment for 4 high-frequency topics.

**One variable only.** Template, format, topic rotation, and CTA style are unchanged.

## Baseline

- Period: 2026-06-29 to 2026-07-06 (last 7 published posts)
- Hook distribution: 1 each of story / alert / blunt / truth / question / contrarian / myth-bust (perfectly even)
- question + myth-bust combined: 2/7 posts (29%)
- Engagement data: pending Notion Posts DB population (see PR notes)

## Variant rule

During 2026-07-07 to 2026-07-13:

| Topic | Required hook_pattern |
|---|---|
| `myths` | `myth-bust` |
| `certifications` | `myth-bust` |
| `vehicles` | `question` |
| `pipeline` | `question` |
| All other topics | existing rotation rules |

Expected outcome: question + myth-bust appears in ~3–4 of 7 test-window posts (~43–57% vs. 29% baseline).

## Test window

- Start: 2026-07-07
- End: 2026-07-13
- Minimum posts required to evaluate: 5 (per scoring.md keep/revert rule)

## Keep / revert criterion (from scoring.md)

Keep if:
- n ≥ 5 posts in test window, AND
- median(test) > median(baseline) by ≥ 15%, OR p75(test) > p75(baseline) AND median not worse by > 10%

## Result (filled by weekly research on 2026-07-14)

- baseline_median: ?
- baseline_p75: ?
- test_median: ?
- test_p75: ?
- n_test: ?
- decision: pending
- commit_note: pending
