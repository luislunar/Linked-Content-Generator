# Testing the video pipeline locally

You can validate the scroll recording + Gotham/neon overlay end-to-end without touching Notion, Blotato, or GitHub Actions. The seed draft at `drafts/2026-04-19/` is there for this.

## Prereqs (one-time)

```bash
# macOS
brew install ffmpeg node

# in the repo root
cd scripts
npm init -y >/dev/null
npm install playwright
npx playwright install chromium
cd ..
```

## Test with any public Notion page

Pick any public Notion page (your own, or one you've shared publicly). Then:

```bash
cd "/Users/luislunar/Desktop/LinkedIn Skills/Linked-Content-Generator"

# 1. Record the scroll (raw webm, 640x800)
node scripts/record-magnet.js \
  "https://www.notion.so/<your-public-page-slug>" \
  drafts/2026-04-19/raw-scroll.webm

# 2. Burn the overlay
./scripts/overlay-text.sh \
  drafts/2026-04-19/raw-scroll.webm \
  drafts/2026-04-19/video.mp4 \
  "MOST BUSINESSES\NTHAT DON'T QUALIFY\NFOR GSA..." \
  "actually do."

# 3. Play it
open drafts/2026-04-19/video.mp4
```

The `\N` sequences are ASS subtitle line breaks — that's how you control where the text wraps inside the neon-green box.

## What to compare against

Play `LinkedinExample.mp4` (in the parent directory) side-by-side with `video.mp4`. Match on:

- **Scroll pace** — should feel continuous, not choppy. Adjust `DURATION_MS` / `STEPS` in `scripts/record-magnet.js` if needed.
- **Overlay position** — defaults to bottom ~14% of the frame. Change `MarginV` values in `assets/overlay-template.ass` to move it.
- **Font weight** — `HookMain` is Montserrat Black, `HookSub` is Montserrat Medium. The reference video uses Gotham Ultra/Medium — Montserrat is the closest free equivalent. Side-by-side they should read nearly identical on mobile.
- **Box/stroke** — neon green box with black stroke. Tweak `Outline` (stroke thickness) and `BackColour` / `OutlineColour` in the .ass file.

## Iterate on overlay styling

The overlay is fully controlled by `assets/overlay-template.ass`. Open that file, tweak sizes/margins, and re-run step 2 above — no need to re-record the scroll.

## Debug tips

- Playwright silent failure → check `chromium` was installed (`npx playwright install chromium`)
- ffmpeg error about fonts → libass needs the `.ttf` files to be discoverable. `overlay-text.sh` passes `fontsdir=assets/fonts` — that should be enough; if not, install the fonts system-wide.
- Text bleeds out of the frame → reduce font size in `overlay-template.ass` or shorten `overlay_text.main` in `post.meta.json`.
