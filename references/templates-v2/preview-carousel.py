"""Render each slide of the carousel as a separate JPG for preview."""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
OUT = HERE / "samples"
HTML = HERE / "carousel-01-myths.html"

# Hide all slides except slide #N (1-indexed)
def isolate_css(n: int) -> str:
    return f"""
    body > .slide {{ display: none !important; }}
    body > .slide:nth-of-type({n}) {{ display: flex !important; }}
    """

with sync_playwright() as p:
    browser = p.chromium.launch()
    for i in range(1, 6):
        page = browser.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=2)
        page.goto(f"file://{HTML.resolve()}")
        page.add_style_tag(content=isolate_css(i))
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
        page.wait_for_timeout(800)
        out = OUT / f"carousel-01-slide-{i:02d}.jpg"
        page.screenshot(path=str(out), type="jpeg", quality=94, full_page=False)
        print(f"  → {out.name}")
        page.close()
    browser.close()

print(f"\nDone. {OUT}")
