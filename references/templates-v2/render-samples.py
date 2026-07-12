"""Render the 3 sample templates to JPG / PDF for review."""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
OUT = HERE / "samples"
OUT.mkdir(exist_ok=True)

SINGLES = [
    ("single-01-bold.html",        "single-01-bold.jpg",        (1080, 1080)),
    ("single-02-numbered.html",    "single-02-numbered.jpg",    (1080, 1080)),
    ("single-03-quote.html",       "single-03-quote.jpg",       (1080, 1080)),
    ("single-04-stat.html",        "single-04-stat.jpg",        (1080, 1080)),
    ("single-05-beforeafter.html", "single-05-beforeafter.jpg", (1080, 1080)),
    ("single-06-checklist.html",   "single-06-checklist.jpg",   (1080, 1080)),
    ("single-07-story.html",       "single-07-story.jpg",       (1080, 1080)),
]

CAROUSEL = ("carousel-01-myths.html", "carousel-01-myths.pdf", (1080, 1080))


def render_jpg(p, html_path, jpg_path, w, h):
    page = p.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
    page.goto(f"file://{html_path.resolve()}")
    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    # Give web fonts a moment to swap in
    page.wait_for_timeout(800)
    page.screenshot(path=str(jpg_path), type="jpeg", quality=94, full_page=False)
    page.close()


def render_pdf(p, html_path, pdf_path, w, h):
    page = p.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
    page.goto(f"file://{html_path.resolve()}")
    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    page.wait_for_timeout(800)
    page.pdf(
        path=str(pdf_path),
        width=f"{w}px",
        height=f"{h}px",
        print_background=True,
        margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
    )
    page.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for src, out, (w, h) in SINGLES:
            html = HERE / src
            jpg = OUT / out
            print(f"  → {jpg.name}")
            render_jpg(browser, html, jpg, w, h)

        src, out, (w, h) = CAROUSEL
        html = HERE / src
        pdf = OUT / out
        print(f"  → {pdf.name}")
        render_pdf(browser, html, pdf, w, h)

        browser.close()

    print(f"\nDone. Output: {OUT}")


if __name__ == "__main__":
    main()
