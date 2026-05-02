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

### Rules for text in the image
- **Max 4-5 words per label.** AI models hallucinate long text. Keep labels short.
- **Never copy full bullet points into the image.** The post text carries the information; the image carries the visual impact.
- **Headline only:** one bold 4-6 word statement, ALL CAPS. This is the only long text the model needs to render.
- **Section labels:** 1-3 words max (e.g. "THE MYTH" / "THE REALITY", "PRIME" / "SUB", "WRONG" / "RIGHT")
- **No sentences in callout boxes.** Use 2-3 word labels with icons instead.

### What to describe in the prompt
1. **Layout type** — myth-vs-reality split, checklist grid, flowchart, alert banner, story scene
2. **Visual elements** — illustrated character (what they're doing), icons, arrows, color zones
3. **Short labels only** — 2-4 words per section/callout, not full sentences
4. **Color structure** — which zones are dark navy, which are light/white, where green highlights go
5. **Footer** — always end with: `Footer text: 'Josh Ladick · GSA Focus'`

### Examples by hook pattern

**myth-bust / contrarian:**
> "Split-panel infographic. Left panel dark navy, bold label 'THE MYTH' with red X icon. Three short myth labels (2-3 words each). Right panel white/light, bold label 'THE REALITY' with green checkmarks. Three short reality labels (2-3 words each). Center: illustrated professional woman in suit walking from dark to light side. Bold headline top: '[4-6 WORD HEADLINE]'. Footer: 'Josh Ladick · GSA Focus'."

**checklist / alert:**
> "Infographic alert layout. Bold warning headline top: '[4-6 WORD HEADLINE]' with caution icon. Left column: illustrated professional woman in blazer holding clipboard, reviewing a laptop screen. Right column: 5 checklist rows, each with a green checkmark and a SHORT 3-word label (no full sentences). Bottom: dark navy banner with 1-line callout. Footer: 'Josh Ladick · GSA Focus'."

**story / truth:**
> "Infographic story layout. Left side: illustrated timeline or journey path with 4 milestone icons, each labeled with 1-2 words. Right side: illustrated professional character looking confident. Bold headline: '[4-6 WORD HEADLINE]'. One highlighted callout box with a SHORT punchy phrase (4-5 words). Footer: 'Josh Ladick · GSA Focus'."

---

## Active experiment

None. (Weekly research will propose the first experiment after week 1 data is collected.)

---

## Rotation tracker (updated by agent each run)

Last 5 (topic, format, hook):
- (none yet — first run)
