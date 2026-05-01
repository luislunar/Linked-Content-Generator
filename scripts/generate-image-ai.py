"""generate-image-ai.py — generate a high-quality LinkedIn infographic image.

Provider priority:
  1. gpt-image-2 (ChatGPT Images 2.0, released Apr 21 2026) — near-perfect text rendering
  2. gpt-image-1 — fallback if gpt-image-2 unavailable
  3. DALL-E 3 — older fallback
  4. HuggingFace FLUX.1-schnell — free fallback
  5. HTML template + Playwright — always available, zero cost

All OpenAI models require OPENAI_API_KEY from platform.openai.com.
NOTE: ChatGPT Plus subscription does NOT include API access — API billing is separate.

Usage:
  python scripts/generate-image-ai.py <drafts_dir>

Env:
  OPENAI_API_KEY          platform.openai.com/api-keys
  HUGGINGFACE_API_TOKEN   Free fallback at huggingface.co (optional)

Output: <drafts_dir>/card.jpg
"""

from __future__ import annotations
import io
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

DALLE3_MODEL = "dall-e-3"
_openai_client = None  # created once on first use

OUTPUT_FILENAME = "card.jpg"

# Base style injected into every prompt for brand consistency
STYLE_SUFFIX = (
    "Professional LinkedIn infographic. Color palette: dark navy blue (#0b1f3a) background, "
    "bright blue (#1a6fff) accents, white text, green (#00cc76) highlights. "
    "Bold typography, clean corporate design, structured layout. "
    "Include an illustrated business professional character in corporate attire. "
    "Bottom footer text: 'Josh Ladick · GSA Focus'. "
    "High resolution, landscape 16:9 format. No watermarks, no logos other than footer text."
)

LAYOUT_HINTS = {
    "myth-bust": (
        "Infographic split layout: LEFT dark column titled 'THE MYTH' with red X marks and wrong beliefs listed, "
        "RIGHT light column titled 'THE REALITY' with green checkmarks and correct information. "
        "Bold headline spanning the full width at the top. "
    ),
    "contrarian": None,  # resolved after dict definition
    "checklist": (
        "Infographic checklist layout: bold headline at top, "
        "numbered items with large green checkmarks in a two-column grid, "
        "each item has a short bold title and brief description, "
        "blue CTA banner at the bottom. "
    ),
    "alert": (
        "Infographic alert layout: bold warning headline at top with exclamation icon, "
        "bullet points with arrow indicators highlighting key warnings, "
        "highlighted callout box with the main takeaway, blue CTA banner at bottom. "
    ),
    "story": (
        "Infographic story layout: large bold pull quote or headline, "
        "3-4 supporting narrative points with person/story icons, "
        "illustrated professional character on one side, blue CTA banner at bottom. "
    ),
    "question": (
        "Infographic Q&A layout: large bold question as headline, "
        "structured answer with decision tree or flowchart element, "
        "bullet points with numbered steps, blue CTA banner at bottom. "
    ),
    "community": (
        "Infographic community layout: warm bold headline, "
        "3 short story examples with illustrated person icons, "
        "supportive closing message, blue CTA banner at bottom. "
    ),
}
LAYOUT_HINTS["contrarian"] = LAYOUT_HINTS["myth-bust"]


def build_prompt(image_prompt: str, post_text: str, hook_pattern: str) -> str:
    layout = LAYOUT_HINTS.get(hook_pattern, (
        "Professional infographic layout: bold headline at top, "
        "3-5 key points with icons, structured two-column content area, blue CTA banner at bottom. "
    ))
    first_line = post_text.strip().splitlines()[0][:120] if post_text else ""
    return (
        f"{layout}"
        f"Topic: {image_prompt}. "
        f"Post hook: \"{first_line}\". "
        f"{STYLE_SUFFIX}"
    )


# ─── Provider 1: HuggingFace (free) ──────────────────────────────────────────

HF_MODEL = "black-forest-labs/FLUX.1-schnell"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"


def generate_huggingface(prompt: str, output_path: Path) -> bool:
    token = os.environ.get("HUGGINGFACE_API_TOKEN")
    if not token:
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 4,
            "guidance_scale": 0.0,
            "width": 1344,
            "height": 768,
        },
    }).encode()

    # Retry up to 3 times — model may be loading (503)
    for attempt in range(3):
        try:
            req = urllib.request.Request(HF_API_URL, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=120) as resp:
                image_bytes = resp.read()
                if len(image_bytes) < 1000:
                    print(f"  HuggingFace attempt {attempt+1}: response too small, retrying...", file=sys.stderr)
                    time.sleep(20)
                    continue
                _save_image_bytes(image_bytes, output_path)
                return True
        except urllib.error.HTTPError as e:
            if e.code == 503:
                print(f"  HuggingFace model loading (503), waiting 30s... (attempt {attempt+1}/3)", file=sys.stderr)
                time.sleep(30)
            else:
                print(f"  HuggingFace HTTP error {e.code}: {e.read()[:200]}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"  HuggingFace error: {e}", file=sys.stderr)
            return False

    print("  HuggingFace: max retries exceeded", file=sys.stderr)
    return False


# ─── Provider 2: DALL-E 3 (OpenAI, ~$0.04/image) ─────────────────────────────

def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI()
    return _openai_client


def _openai_generate(model: str, prompt: str, size: str, quality: str, output_path: Path) -> bool:
    """Shared helper for any OpenAI image generation model."""
    try:
        import base64
        client = _get_openai_client()

        if model == DALLE3_MODEL:
            response = client.images.generate(
                model=model, prompt=prompt, n=1, size=size,
                quality=quality, response_format="url",
            )
            image_url = response.data[0].url
            with urllib.request.urlopen(image_url, timeout=60) as resp:
                image_bytes = resp.read()
        else:
            response = client.images.generate(
                model=model, prompt=prompt, n=1, size=size,
                quality=quality,
            )
            image_bytes = base64.b64decode(response.data[0].b64_json)

        _save_image_bytes(image_bytes, output_path)
        return True
    except Exception as e:
        print(f"  {model} error: {e}", file=sys.stderr)
        return False


def generate_gpt_image_2(prompt: str, output_path: Path) -> bool:
    """gpt-image-2 — ChatGPT Images 2.0 (Apr 2026). Near-perfect text rendering, 4K support."""
    return _openai_generate(
        model="gpt-image-2",
        prompt=prompt,
        size="1536x1024",  # landscape 3:2, great for LinkedIn infographics
        quality="medium",  # balanced quality/cost; use "high" for premium posts
        output_path=output_path,
    )


def generate_gpt_image_1(prompt: str, output_path: Path) -> bool:
    """gpt-image-1 — fallback if gpt-image-2 unavailable."""
    return _openai_generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1536x1024",
        quality="medium",
        output_path=output_path,
    )


def generate_dalle3(prompt: str, output_path: Path) -> bool:
    """DALL-E 3 HD — older fallback."""
    return _openai_generate(
        model=DALLE3_MODEL,
        prompt=prompt,
        size="1792x1024",
        quality="hd",
        output_path=output_path,
    )


# ─── Provider 3: HTML template fallback ──────────────────────────────────────

def fallback_html_template(drafts_dir: Path) -> None:
    print("Using HTML template fallback (generate-image.py)...", file=sys.stderr)
    result = subprocess.run(
        [sys.executable, "scripts/generate-image.py", str(drafts_dir)],
    )
    if result.returncode != 0:
        print("error: HTML template fallback failed", file=sys.stderr)
        sys.exit(1)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _save_image_bytes(image_bytes: bytes, output_path: Path) -> None:
    """Save image bytes as JPEG, converting if necessary."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img.save(output_path, "JPEG", quality=92, optimize=True)
    except ImportError:
        # No Pillow — write raw bytes (might be PNG, LinkedIn accepts it)
        output_path.write_bytes(image_bytes)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python scripts/generate-image-ai.py <drafts_dir>", file=sys.stderr)
        sys.exit(1)

    drafts_dir = Path(sys.argv[1])
    if not drafts_dir.is_dir():
        print(f"error: {drafts_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    meta_path = drafts_dir / "post.meta.json"
    post_path = drafts_dir / "post.md"

    if not meta_path.exists():
        print(f"error: {meta_path} not found", file=sys.stderr)
        sys.exit(1)

    meta = json.loads(meta_path.read_text())
    image_prompt = meta.get("image_prompt", "").strip()
    hook_pattern = meta.get("hook_pattern", "bullets")
    post_text = post_path.read_text() if post_path.exists() else ""
    output_path = drafts_dir / OUTPUT_FILENAME

    if not image_prompt:
        print("warning: no image_prompt in post.meta.json — using HTML template")
        fallback_html_template(drafts_dir)
        return

    full_prompt = build_prompt(image_prompt, post_text, hook_pattern)
    print(f"Generating image...")

    if os.environ.get("OPENAI_API_KEY"):
        print("  Provider: gpt-image-2 (ChatGPT Images 2.0, medium quality)")
        if generate_gpt_image_2(full_prompt, output_path):
            print(f"card saved: {output_path}")
            return
        print("  gpt-image-2 unavailable — trying gpt-image-1...")
        if generate_gpt_image_1(full_prompt, output_path):
            print(f"card saved: {output_path}")
            return
        print("  gpt-image-1 unavailable — trying DALL-E 3...")
        if generate_dalle3(full_prompt, output_path):
            print(f"card saved: {output_path}")
            return

    if os.environ.get("HUGGINGFACE_API_TOKEN"):
        print("  Provider: HuggingFace (FLUX.1-schnell, free)")
        if generate_huggingface(full_prompt, output_path):
            print(f"card saved: {output_path}")
            return

    print("  No AI provider available — using HTML template")
    fallback_html_template(drafts_dir)
    print(f"card saved: {output_path}")


if __name__ == "__main__":
    main()
