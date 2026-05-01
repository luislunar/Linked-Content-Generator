# Generator — content strategy

This file is read by the daily agent to decide what to write each day.
Only `/weekly-research` may edit this file based on experiment results.

---

## Topic rotation

Rotate through these topics. Avoid repeating the same topic within 5 days.

| Topic | Description | Frequency |
|---|---|---|
| `gsa_basics` | What GSA Schedule is, how it works, when it makes sense | 2x/week |
| `sam` | SAM.gov registration, renewal, NAICS codes, common errors | 1x/week |
| `myths` | Misconceptions that stop small businesses from pursuing GovCon | 1x/week |
| `teaming` | Prime/sub relationships, teaming agreements, building past performance | 1x/week |
| `certifications` | 8(a), WOSB, SDVOSB, HUBZone — what they do and how to use them | 1x/week |
| `pricing` | GSA pricing strategy, Basis of Award, negotiation mistakes | 1x/week |
| `compliance` | Schedule renewal, Trade Agreements Act, terms and conditions | 1x/week |
| `vehicles` | GSA MAS vs SEWP vs CIO-SP4 vs OASIS+ — when to use each | 1x/week |
| `pipeline` | Finding opportunities, recompetes, sources sought, industry days | 1x/week |

---

## Hook patterns

Pick the hook pattern that best fits the topic. Rotate — don't use the same pattern two days in a row.

| Pattern | Structure | Best for |
|---|---|---|
| `myth-bust` | `"[Common myth]." Here's what's actually true.` | myths, certifications, past performance |
| `contrarian` | `"Wrong question. Here's the right one."` | vehicles, pricing, SAM |
| `alert` | `"This one mistake is quietly costing small businesses..."` | SAM, compliance, renewals |
| `truth` | `"Nobody talks enough about [uncomfortable reality]."` | pipeline, long game, teaming |
| `blunt` | `"[Hard fact]. I know that sounds blunt, but..."` | SAM, basics, any checklist topic |
| `question` | `"Before you [common action]... read this."` | vehicles, certifications, pricing |
| `story` | Personal origin story or community validation moment | community, milestones, wins |
| `checklist` | `"[Topic] health check: here's what most people miss."` | SAM, compliance, capability statement |

---

## Format rules

| Format | Structure | When to use |
|---|---|---|
| `bullets` | 3–6 bullet points with `→`, each = one actionable insight | Most posts |
| `checklist` | Numbered items with clear Yes/No action | SAM, compliance, renewal topics |
| `comparison` | Two columns or side-by-side (Myth vs Reality, Option A vs B) | Myth-bust, vehicle comparison |
| `story` | Short narrative arc, 2–3 paragraphs, no bullets | Community or personal posts |
| `qa` | Self-posed question → structured answer | Vehicles, certifications |

---

## CTA rules (community questions)

Every post ends with an open-ended question. Rotate styles:

- **Experience-share:** `"What's been your experience with [topic]?"`
- **Fill-in-the-blank:** `"Fill in the blank: ________ is the reason I haven't [action] yet."`
- **Action prompt:** `"Which of these are you already doing? Which one are you adding this week?"`
- **Myth drop:** `"Drop the biggest myth you believed about GovCon when you first started."`
- **Honest check:** `"When did you last [action]? Be honest. 😅"`
- **Opinion:** `"What's the one thing nobody warned you about in GovCon?"`

Never use: "Comment X to receive Y" or any lead magnet CTA.

---

## Image prompt guidelines

Every post needs an `image_prompt` in post.meta.json for gpt-image-2.
The prompt must be specific to the post content. Include:
- The layout type (checklist, myth-vs-reality, story scene, alert)
- The specific content elements to visualize (bullet points, labels, characters)
- The illustrated character action (pointing at a board, reviewing documents, etc.)
- The specific text callouts to include in the image

Example for a SAM.gov checklist post:
> "Infographic checklist layout. Bold headline: 'SAM.GOV IS NOT OPTIONAL.' Six numbered checklist items with green checkmarks: Registration Active, NAICS Codes Current, Business Size Accurate, Points of Contact Updated, Representations & Certifications, Exclusions Check. Right side shows illustrated professional woman reviewing documents with APPROVED stamp visible. Bottom banner: 'Don't let admin be the reason you lose.' Footer: Josh Ladick · GSA Focus."

---

## Active experiment

None. (Weekly research will propose the first experiment after week 1 data is collected.)

---

## Rotation tracker (updated by agent each run)

Last 5 (topic, format, hook):
- (none yet — first run)
