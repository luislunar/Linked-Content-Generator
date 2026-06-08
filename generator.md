# Generator — content strategy

This file is read by the daily agent to decide what to write each day.
Only `/weekly-research` may edit this file based on experiment results.

---

## Post types (rotation pool)

Every post is exactly **one** of these 8 types. Pick a type that wasn't used in the **last 3 days** (read `logs/run-*.md` to check). Within any 7-day window, hit at least **5 different types** — variety is the goal.

| # | `post_type` | Words | Template (first choice → alternative) | Best for |
|---|---|---|---|---|
| 1 | `inspiration` | 50–150 | `single-03-quote` → `single-01-bold` | Hot truths, contrarian one-liners, mantras |
| 2 | `carousel` | varies | `carousel-01-myths` | Frameworks, lists, multi-part ideas. Max 1 every 4–5 days |
| 3 | `client_story` | 200–300 | `single-05-beforeafter` → `single-07-story` | Credibility, social proof, transformations |
| 4 | `personal_story` | 200–400 | `single-07-story` → `single-03-quote` | Humanizing the brand, trust building |
| 5 | `tips_list` | 150–280 | `single-06-checklist` → `single-02-numbered` | Educational, expertise positioning |
| 6 | `milestone` | 150–250 | `single-04-stat` → `single-01-bold` | Big numbers, launches, anniversaries |
| 7 | `hot_take` | 150–300 | `single-01-bold` → `single-03-quote` | Trending topics, contrarian analysis |
| 8 | `behind_scenes` | 100–200 | `single-07-story` → `single-03-quote` | Authenticity, process reveals |

### Cadence rules
- **No type 2 days in a row.** Hard rule.
- **Carousel:** max 1 every 4 days. Save for genuinely multi-part ideas.
- **If last 3 posts all started with a statement**, today's hook must be a question or story.
- **Length variation is mandatory:** if last 3 posts averaged > 200 words, today must be under 180.
- **Color contrast in the feed:** if last 2 templates were both dark-bg (`single-01`, `single-04`, `single-06`), pick a cream-bg template today (`single-02`, `single-03`, `single-05`, `single-07`).

---

## Template data shapes

Every template needs specific keys in `template_data`. Produce ALL keys exactly as named (use `""` for any you don't fill). Fields ending in `_html` accept inline HTML for emphasis: wrap accent words in `<span class="accent">...</span>`, italics in `<em>...</em>`, line breaks with `<br>`, and bold inside context paragraphs with `<strong>...</strong>`. Everything else is plain text and will be HTML-escaped automatically.

### `single-01-bold` — Bold Statement (dark navy)
```json
{
  "tag": "Compliance Alert",                              // short coral pill, ALL CAPS-ish, 2-3 words
  "headline_html": "SAM<br>EXPIRED<br><span class='accent'>SILENTLY?</span>",   // 3 lines max, last line usually accent
  "sub": "Lapsed registrations freeze every active payment...",                  // 1–2 sentences, max 130 chars
  "issue": "Issue 014"                                    // editorial label, e.g. "Issue 014" or "No. 028"
}
```

### `single-02-numbered` — Numbered Breakdown (cream)
```json
{
  "section_label": "Pricing Mistakes",                    // category, ALL CAPS-ish, 2-3 words
  "index": "Vol. 09 · Pricing",
  "headline_html": "Four numbers that <span class='accent'>silently kill</span> your GSA margins.",
  "items": [                                              // EXACTLY 4 items
    { "num": "01", "title": "Wrong commercial price", "desc": "Quote what you'd give a private client and lose room with the CO." },
    { "num": "02", "title": "...", "desc": "..." },
    { "num": "03", "title": "...", "desc": "..." },
    { "num": "04", "title": "...", "desc": "..." }
  ]
}
```

### `single-03-quote` — Pull Quote (cream + serif)
```json
{
  "section_label": "Field Note",
  "index": "No. 028 · Pipeline",
  "quote_html": "The Schedule doesn't sell. <em>Your follow-up does.</em>",   // 1 sentence, max 110 chars
  "footer_left": "One Hard Truth",
  "footer_right": "Weekly Field Notes"
}
```

### `single-04-stat` — Big Stat (dark navy)
```json
{
  "section_label": "Federal Market",
  "snapshot": "Snapshot · FY2024",
  "label_above": "Total federal contract spend, FY2024",
  "big_number_html": "$<span class='accent'>685B</span>",          // dollar/% prefix + number, max ~5 chars in accent
  "context_html": "Small businesses captured <strong>28% of it</strong> — the rest went to primes who don't actually want it.",
  "source": "Source · USAspending.gov",
  "by_line": "By the Numbers"
}
```

### `single-05-beforeafter` — Before / After (cream + navy split)
```json
{
  "section_label": "11-Month Shift",
  "case_num": "Case · 042",
  "headline_html": "What changes when the <span class='accent'>Schedule lands.</span>",
  "before_items": ["No federal revenue line", "Cold outreach failing", "Stuck on commercial only"],  // EXACTLY 3, max 35 chars each
  "after_items":  ["First award month 11", "Inbound RFQs landing", "Pipeline rolling forward"],       // EXACTLY 3, max 35 chars each
  "footer_left": "One Real Transformation",
  "footer_right": "Field Case Series"
}
```

### `single-06-checklist` — Visual Checklist (dark navy)
```json
{
  "section_label": "Eligibility Check",
  "module": "Module 03 · Readiness",
  "headline_html": "Five boxes you must <span class='accent'>already</span> tick.",
  "items": [                                              // EXACTLY 5 items
    { "title": "Two years in business", "sub": "Hard line — federal requires the runway" },
    { "title": "...", "sub": "..." },
    { "title": "...", "sub": "..." },
    { "title": "...", "sub": "..." },
    { "title": "...", "sub": "..." }
  ],
  "footer_left": "Quick Self-Audit",
  "footer_right": "Page 1 of 1"
}
```

### `single-07-story` — Story Card (cream + serif lead)
```json
{
  "section_label": "Field Report",
  "year_client": "Year One · Client 017",
  "lead_html": "Eight months from <em>\"this is impossible\"</em> to first federal award.",
  "rows": [                                               // EXACTLY 3 rows
    { "when": "Month 01–03", "what_html": "<strong>Paperwork & pricing audit</strong> <span class='light'>— the part everyone underestimates</span>" },
    { "when": "Month 04–06", "what_html": "<strong>...</strong> <span class='light'>— ...</span>" },
    { "when": "Month 07–08", "what_html": "<strong>...</strong> <span class='light'>— ...</span>" }
  ],
  "closer": "THE SLOW PART WAS THE PREP, NOT THE WAIT."  // 1 line, ALL CAPS, max 60 chars
}
```

### `carousel-01-myths` — 5-Slide Carousel (cover + 3 myths + close)
```json
{
  "cover": {
    "top_label": "Field Guide / Vol. 03",
    "headline_html": "5 myths that <span class='accent'>kill</span> new GovCon shops.",   // max 8 words
    "edition": "Myths Edition"
  },
  "myths": [                                              // EXACTLY 3 myth/reality pairs
    {
      "label": "The Past-Performance Lie",                // short subtitle shown at bottom of slide
      "myth_text": "You need past performance before you can win anything.",   // max 90 chars
      "reality_text": "Teaming agreements let new shops piggy-back on a prime's history..."   // max 200 chars
    },
    { "label": "...", "myth_text": "...", "reality_text": "..." },
    { "label": "...", "myth_text": "...", "reality_text": "..." }
  ],
  "close": {
    "close_tag": "Your turn",
    "close_headline": "Which one almost stopped you?",
    "close_question": "Drop the myth you believed when you started..."
  }
}
```

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

**EXP-001 — alert-hook-weight** (2026-06-08 → 2026-06-14)

Variable: hook pattern frequency. Variant rule: select `alert` on any day where
it hasn't been used in the last 3 days AND the topic is `sam`, `compliance`,
`pricing`, or `gsa_basics`. Target ≥3 alert-hook posts this week.
All other hook-pattern and topic rotation rules remain unchanged.

---

## Rotation tracker (updated by agent each run)

Last 5 (topic, format, hook):
- (none yet — first run)
