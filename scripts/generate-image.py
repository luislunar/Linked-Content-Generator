"""generate-image.py — render a branded infographic (1200×628 JPEG) using Playwright.

Reads post.md + post.meta.json from the drafts dir, chooses the right HTML template
based on post format, injects real content, and screenshots at 1200×628.

Usage:
  python scripts/generate-image.py <drafts_dir>

Templates (assets/):
  card-checklist.html  — for bullets/checklist/comparison/qa posts
  card-myth.html       — for myth-bust posts (splits bullets into myth vs reality)

Output: <drafts_dir>/card.jpg
"""

from __future__ import annotations
import json
import re
import sys
import tempfile
from pathlib import Path

ASSETS_DIR = Path("assets")
OUTPUT_FILENAME = "card.jpg"
VIEWPORT = {"width": 1200, "height": 628}

CHECKMARK_SVG = """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <polyline points="20 6 9 17 4 12" stroke="white" stroke-width="3"
    stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""


# ─── Post parsing ──────────────────────────────────────────────────────────────

def parse_post(post_md: str) -> dict:
    """Extract hook, bullets, closing line, and community question from post.md."""
    lines = [l.rstrip() for l in post_md.strip().splitlines()]
    bullets: list[str] = []
    hook_lines: list[str] = []
    closing_lines: list[str] = []
    question: str = ""

    # Find the last line ending with "?" before hashtags — that's the community question
    hashtag_start = len(lines)
    for i, line in enumerate(lines):
        if line.startswith("#"):
            hashtag_start = i
            break

    content_lines = lines[:hashtag_start]

    # Bullets are lines starting with → or digit. or -
    bullet_indices = [i for i, l in enumerate(content_lines) if re.match(r"^(→|[-•]|\d+\.)\s", l)]

    # Hook = everything before the first bullet (skip blanks at end)
    if bullet_indices:
        first_bullet = bullet_indices[0]
        hook_lines = [l for l in content_lines[:first_bullet] if l.strip()]
    else:
        # No bullets — use first non-blank lines as hook
        hook_lines = [l for l in content_lines[:3] if l.strip()]

    # Collect bullets
    for i in bullet_indices:
        raw = re.sub(r"^(→|[-•]|\d+\.)\s+", "", content_lines[i])
        bullets.append(raw.strip())

    # Community question = last non-blank line that ends with ?
    for line in reversed(content_lines):
        if line.strip().endswith("?") and not line.startswith("#"):
            question = line.strip()
            break

    # Closing = non-blank lines after last bullet and before question (if any)
    if bullet_indices:
        after_bullets = [l for l in content_lines[bullet_indices[-1]+1:] if l.strip()]
        closing_lines = [l for l in after_bullets if not l.endswith("?")]

    hook = " ".join(hook_lines)
    closing = " ".join(closing_lines)

    return {
        "hook": hook,
        "bullets": bullets,
        "closing": closing,
        "question": question,
    }


def split_bullets_myth_reality(bullets: list[str]) -> tuple[list[str], list[str]]:
    """For myth-bust posts: split bullets roughly in half for myth vs. reality columns."""
    mid = (len(bullets) + 1) // 2
    return bullets[:mid], bullets[mid:]


# ─── HTML generation ───────────────────────────────────────────────────────────

def make_checklist_item(title: str, desc: str = "") -> str:
    return f"""<div class="item">
      <div class="check">{CHECKMARK_SVG}</div>
      <div class="item-text">
        <div class="item-title">{_esc(title)}</div>
        {"<div class='item-desc'>" + _esc(desc) + "</div>" if desc else ""}
      </div>
    </div>"""


def make_myth_item(text: str) -> str:
    return f"""<div class="myth-item">
      <span class="myth-x">✗</span>
      <span class="myth-text">{_esc(text)}</span>
    </div>"""


def make_reality_item(text: str) -> str:
    return f"""<div class="reality-item">
      <span class="reality-check">✓</span>
      <span class="reality-text">{_esc(text)}</span>
    </div>"""


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _split_bullet(text: str) -> tuple[str, str]:
    """Split 'Title: description' or 'Title — description' into (title, desc)."""
    for sep in (":", "—", "-", "–"):
        if sep in text:
            parts = text.split(sep, 1)
            return parts[0].strip(), parts[1].strip()
    return text, ""


def render_checklist_html(template: str, headline: str, parsed: dict) -> str:
    words = headline.split()
    if len(words) >= 2:
        main_words = " ".join(words[:-1])
        last_word = words[-1]
        html_headline = f"{_esc(main_words)} <span class='accent'>{_esc(last_word)}</span>"
    else:
        html_headline = _esc(headline)

    subheadline = parsed["closing"] or parsed["hook"][:80]
    if len(subheadline) > 80:
        subheadline = subheadline[:77] + "…"

    items_html = ""
    for bullet in parsed["bullets"][:6]:
        title, desc = _split_bullet(bullet)
        items_html += make_checklist_item(title, desc)

    cta = parsed["question"] or "Share your experience below ↓"
    if cta.startswith('"') and cta.endswith('"'):
        cta = cta[1:-1]

    return (template
            .replace("{{HEADLINE}}", html_headline)
            .replace("{{SUBHEADLINE}}", _esc(subheadline))
            .replace("{{ITEMS}}", items_html)
            .replace("{{CTA}}", _esc(cta[:100])))


def render_myth_html(template: str, headline: str, parsed: dict) -> str:
    words = headline.split()
    # For myth template: try to highlight "NOT" or last word
    if "NOT" in words:
        idx = words.index("NOT")
        before = " ".join(words[:idx])
        after = " ".join(words[idx+1:])
        html_headline = f"{_esc(before)} <span class='accent'>NOT</span> {_esc(after)}"
    elif len(words) >= 2:
        main_words = " ".join(words[:-1])
        last_word = words[-1]
        html_headline = f"{_esc(main_words)} <span class='accent'>{_esc(last_word)}</span>"
    else:
        html_headline = _esc(headline)

    subheadline = parsed["hook"][:90] if len(parsed["hook"]) <= 90 else parsed["hook"][:87] + "…"

    myths, realities = split_bullets_myth_reality(parsed["bullets"])
    myth_html = "".join(make_myth_item(b) for b in myths[:4])
    reality_html = "".join(make_reality_item(b) for b in realities[:4])

    footer_msg = parsed["closing"] or parsed["question"] or "The barrier isn't what you think."
    if len(footer_msg) > 90:
        footer_msg = footer_msg[:87] + "…"

    return (template
            .replace("{{HEADLINE}}", html_headline)
            .replace("{{SUBHEADLINE}}", _esc(subheadline))
            .replace("{{MYTH_ITEMS}}", myth_html)
            .replace("{{REALITY_ITEMS}}", reality_html)
            .replace("{{FOOTER_MESSAGE}}", _esc(footer_msg)))


# ─── Main ──────────────────────────────────────────────────────────────────────

def render_card(drafts_dir: Path) -> Path:
    meta_path = drafts_dir / "post.meta.json"
    post_path = drafts_dir / "post.md"

    if not meta_path.exists():
        print(f"error: {meta_path} not found", file=sys.stderr)
        sys.exit(1)
    if not post_path.exists():
        print(f"error: {post_path} not found", file=sys.stderr)
        sys.exit(1)

    meta = json.loads(meta_path.read_text())
    headline = meta.get("image_headline", "").strip()
    if not headline:
        print("error: post.meta.json missing 'image_headline'", file=sys.stderr)
        sys.exit(1)

    hook_pattern = meta.get("hook_pattern", "bullets")
    parsed = parse_post(post_path.read_text())

    # Choose template
    use_myth = hook_pattern in ("myth-bust", "contrarian") and len(parsed["bullets"]) >= 4
    template_name = "card-myth.html" if use_myth else "card-checklist.html"
    template_path = ASSETS_DIR / template_name

    if not template_path.exists():
        print(f"error: template not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    template_html = template_path.read_text()
    if use_myth:
        rendered = render_myth_html(template_html, headline, parsed)
    else:
        rendered = render_checklist_html(template_html, headline, parsed)

    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False) as f:
        f.write(rendered)
        tmp_path = Path(f.name)

    output_path = drafts_dir / OUTPUT_FILENAME
    _screenshot(tmp_path, output_path)
    tmp_path.unlink(missing_ok=True)
    return output_path


def _screenshot(html_path: Path, output_path: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("error: playwright not installed.\n  pip install playwright && playwright install chromium",
              file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT)
        page.goto(f"file://{html_path.resolve()}")
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        page.screenshot(path=str(output_path), type="jpeg", quality=92, full_page=False)
        browser.close()


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python scripts/generate-image.py <drafts_dir>", file=sys.stderr)
        sys.exit(1)

    drafts_dir = Path(sys.argv[1])
    if not drafts_dir.is_dir():
        print(f"error: {drafts_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    output_path = render_card(drafts_dir)
    print(f"card saved: {output_path}")


if __name__ == "__main__":
    main()
