"""render-card.py — render the post image/PDF from post.meta.json using HTML templates.

Reads post.meta.json from <drafts_dir>, picks the template named in `meta.template`,
fills placeholders from `meta.template_data`, renders with Playwright.

- Single templates  → drafts_dir/card.jpg  (1080x1080)
- Carousel template → drafts_dir/card.pdf  (5 pages × 1080x1080)

Usage:
  python scripts/render-card.py <drafts_dir>
"""
from __future__ import annotations
import html
import json
import sys
import tempfile
from pathlib import Path

TEMPLATES_DIR = Path("assets/templates")
VIEWPORT = (1080, 1080)


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


# ── Per-template builders that produce a {placeholder: html_or_text} dict ──────

def build_single_01_bold(d: dict) -> dict:
    return {
        "TAG": esc(d.get("tag", "")),
        "HEADLINE_HTML": d.get("headline_html", ""),
        "SUB": esc(d.get("sub", "")),
        "ISSUE": esc(d.get("issue", "")),
    }


def build_single_02_numbered(d: dict) -> dict:
    items_html = ""
    for it in d.get("items", [])[:4]:
        items_html += (
            f'<div class="item">'
            f'<div class="num">{esc(it.get("num",""))}</div>'
            f'<div class="title">{esc(it.get("title",""))}</div>'
            f'<div class="desc">{esc(it.get("desc",""))}</div>'
            f'</div>'
        )
    return {
        "SECTION_LABEL": esc(d.get("section_label", "")),
        "INDEX": esc(d.get("index", "")),
        "HEADLINE_HTML": d.get("headline_html", ""),
        "ITEMS_HTML": items_html,
    }


def build_single_03_quote(d: dict) -> dict:
    return {
        "SECTION_LABEL": esc(d.get("section_label", "")),
        "INDEX": esc(d.get("index", "")),
        "QUOTE_HTML": d.get("quote_html", ""),
        "FOOTER_LEFT": esc(d.get("footer_left", "")),
        "FOOTER_RIGHT": esc(d.get("footer_right", "")),
    }


def build_single_04_stat(d: dict) -> dict:
    return {
        "SECTION_LABEL": esc(d.get("section_label", "")),
        "SNAPSHOT": esc(d.get("snapshot", "")),
        "LABEL_ABOVE": esc(d.get("label_above", "")),
        "BIG_NUMBER_HTML": d.get("big_number_html", ""),
        "CONTEXT_HTML": d.get("context_html", ""),
        "SOURCE": esc(d.get("source", "")),
        "BY_LINE": esc(d.get("by_line", "")),
    }


def build_single_05_beforeafter(d: dict) -> dict:
    def items(arr):
        return "".join(f'<div class="side-item">{esc(x)}</div>' for x in arr[:3])
    return {
        "SECTION_LABEL": esc(d.get("section_label", "")),
        "CASE_NUM": esc(d.get("case_num", "")),
        "HEADLINE_HTML": d.get("headline_html", ""),
        "BEFORE_ITEMS_HTML": items(d.get("before_items", [])),
        "AFTER_ITEMS_HTML": items(d.get("after_items", [])),
        "FOOTER_LEFT": esc(d.get("footer_left", "")),
        "FOOTER_RIGHT": esc(d.get("footer_right", "")),
    }


def build_single_06_checklist(d: dict) -> dict:
    check_svg = ('<svg viewBox="0 0 24 24" fill="none">'
                 '<polyline points="20 6 9 17 4 12" stroke="white" stroke-width="3" '
                 'stroke-linecap="round" stroke-linejoin="round"/></svg>')
    items_html = ""
    for it in d.get("items", [])[:5]:
        items_html += (
            f'<div class="item">'
            f'<div class="check">{check_svg}</div>'
            f'<div class="item-text">{esc(it.get("title",""))}'
            f'<span class="sub">{esc(it.get("sub",""))}</span></div>'
            f'</div>'
        )
    return {
        "SECTION_LABEL": esc(d.get("section_label", "")),
        "MODULE": esc(d.get("module", "")),
        "HEADLINE_HTML": d.get("headline_html", ""),
        "ITEMS_HTML": items_html,
        "FOOTER_LEFT": esc(d.get("footer_left", "")),
        "FOOTER_RIGHT": esc(d.get("footer_right", "")),
    }


def build_single_07_story(d: dict) -> dict:
    rows_html = ""
    for r in d.get("rows", [])[:3]:
        rows_html += (
            f'<div class="row">'
            f'<div class="when">{esc(r.get("when",""))}</div>'
            f'<div class="what">{r.get("what_html","")}</div>'
            f'</div>'
        )
    return {
        "SECTION_LABEL": esc(d.get("section_label", "")),
        "YEAR_CLIENT": esc(d.get("year_client", "")),
        "LEAD_HTML": d.get("lead_html", ""),
        "ROWS_HTML": rows_html,
        "CLOSER": esc(d.get("closer", "")),
    }


def build_carousel_01_myths(d: dict) -> dict:
    cover = d.get("cover", {})
    myths = d.get("myths", [])
    close = d.get("close", {})

    def m(idx):
        return myths[idx] if idx < len(myths) else {}

    return {
        "COVER_TOP_LABEL": esc(cover.get("top_label", "")),
        "COVER_HEADLINE_HTML": cover.get("headline_html", ""),
        "COVER_EDITION": esc(cover.get("edition", "")),
        "MYTH_1_TEXT": esc(m(0).get("myth_text", "")),
        "MYTH_1_REALITY": esc(m(0).get("reality_text", "")),
        "MYTH_1_LABEL": esc(m(0).get("label", "")),
        "MYTH_2_TEXT": esc(m(1).get("myth_text", "")),
        "MYTH_2_REALITY": esc(m(1).get("reality_text", "")),
        "MYTH_2_LABEL": esc(m(1).get("label", "")),
        "MYTH_3_TEXT": esc(m(2).get("myth_text", "")),
        "MYTH_3_REALITY": esc(m(2).get("reality_text", "")),
        "MYTH_3_LABEL": esc(m(2).get("label", "")),
        "CLOSE_TAG": esc(close.get("close_tag", "")),
        "CLOSE_HEADLINE": esc(close.get("close_headline", "")),
        "CLOSE_QUESTION": esc(close.get("close_question", "")),
    }


BUILDERS = {
    "single-01-bold": build_single_01_bold,
    "single-02-numbered": build_single_02_numbered,
    "single-03-quote": build_single_03_quote,
    "single-04-stat": build_single_04_stat,
    "single-05-beforeafter": build_single_05_beforeafter,
    "single-06-checklist": build_single_06_checklist,
    "single-07-story": build_single_07_story,
    "carousel-01-myths": build_carousel_01_myths,
}

CAROUSEL_TEMPLATES = {"carousel-01-myths"}


# ── Render ────────────────────────────────────────────────────────────────────

def fill(template_html: str, slots: dict) -> str:
    for k, v in slots.items():
        template_html = template_html.replace("{{" + k + "}}", str(v))
    return template_html


def render(drafts_dir: Path) -> Path:
    meta = json.loads((drafts_dir / "post.meta.json").read_text())
    template_name = meta.get("template")
    template_data = meta.get("template_data", {})

    if not template_name:
        print("error: post.meta.json missing 'template'", file=sys.stderr)
        sys.exit(1)
    if template_name not in BUILDERS:
        print(f"error: unknown template '{template_name}'", file=sys.stderr)
        sys.exit(1)

    template_path = TEMPLATES_DIR / f"{template_name}.html"
    if not template_path.exists():
        print(f"error: template not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    slots = BUILDERS[template_name](template_data)
    rendered_html = fill(template_path.read_text(), slots)

    is_carousel = template_name in CAROUSEL_TEMPLATES
    output_name = "card.pdf" if is_carousel else "card.jpg"
    output_path = drafts_dir / output_name

    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False) as f:
        f.write(rendered_html)
        tmp_path = Path(f.name)

    try:
        _screenshot(tmp_path, output_path, pdf=is_carousel)
    finally:
        tmp_path.unlink(missing_ok=True)

    return output_path


def _screenshot(html_path: Path, output_path: Path, pdf: bool) -> None:
    from playwright.sync_api import sync_playwright
    w, h = VIEWPORT
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
        page.goto(f"file://{html_path.resolve()}")
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
        page.wait_for_timeout(800)
        if pdf:
            page.pdf(
                path=str(output_path),
                width=f"{w}px",
                height=f"{h}px",
                print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            )
        else:
            page.screenshot(path=str(output_path), type="jpeg", quality=94, full_page=False)
        browser.close()


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python scripts/render-card.py <drafts_dir>", file=sys.stderr)
        sys.exit(1)
    drafts_dir = Path(sys.argv[1])
    if not drafts_dir.is_dir():
        print(f"error: {drafts_dir} is not a directory", file=sys.stderr)
        sys.exit(1)
    out = render(drafts_dir)
    print(f"card saved: {out}")


if __name__ == "__main__":
    main()
