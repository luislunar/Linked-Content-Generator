"""publish-zapier.py — trigger a Zapier webhook to publish a LinkedIn post with image.

GitHub Actions commits card.jpg to the repo, then calls this script.
Zapier receives: post text + public image URL → posts to LinkedIn.

Usage:
  python scripts/publish-zapier.py <drafts_dir> --image-url <url>

Env:
  ZAPIER_WEBHOOK_URL   The "Catch Hook" URL from Zapier (Webhooks by Zapier trigger)
  GITHUB_REPOSITORY    Auto-set by GitHub Actions (e.g. "joshladick/gsa-content")
  GITHUB_REF_NAME      Auto-set by GitHub Actions (branch name, e.g. "main")
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path


def env(name: str, required: bool = True) -> str:
    v = os.environ.get(name, "")
    if required and not v:
        print(f"error: missing env var {name}", file=sys.stderr)
        sys.exit(2)
    return v


def send_webhook(webhook_url: str, post_text: str, image_url: str) -> dict:
    """POST to Zapier webhook. Field names match Zapier's LinkedIn action: comment (required), content_image_url."""
    payload = json.dumps({
        "comment": post_text,
        "content_image_url": image_url,
    }).encode()

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def build_image_url(drafts_dir: Path, image_filename: str = "card.jpg") -> str:
    """Build the raw GitHub URL for the committed image."""
    repo = env("GITHUB_REPOSITORY")
    branch = env("GITHUB_REF_NAME", required=False) or "main"
    rel_path = str(drafts_dir / image_filename)
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{rel_path}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("drafts_dir")
    ap.add_argument("--image-url", default=None,
                    help="Override the image URL (auto-built from GitHub repo if omitted)")
    args = ap.parse_args()

    drafts_dir = Path(args.drafts_dir)
    webhook_url = env("ZAPIER_WEBHOOK_URL")
    post_text = (drafts_dir / "post.md").read_text().strip()

    image_url = args.image_url or build_image_url(drafts_dir)

    print(f"Sending to Zapier...")
    print(f"  image_url: {image_url}")
    result = send_webhook(webhook_url, post_text, image_url)
    print(f"  response:  {result}")

    meta_path = drafts_dir / "post.meta.json"
    try:
        meta = json.loads(meta_path.read_text())
        meta["content_image_url"] = image_url
        meta["zapier_status"] = result.get("status", "sent")
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    except FileNotFoundError:
        pass

    print("Done — Zapier will publish to LinkedIn.")


if __name__ == "__main__":
    main()
