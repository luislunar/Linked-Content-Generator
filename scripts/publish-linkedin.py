"""publish-linkedin.py — upload an image/PDF + publish a LinkedIn post via the versioned REST API.

Usage:
  python scripts/publish-linkedin.py <media_path> <drafts_dir> [--dry-run] [--upload-only]

  <media_path>   e.g. drafts/2026-04-30/card.jpg (image) or card.pdf (carousel)
  <drafts_dir>   e.g. drafts/2026-04-30  (must contain post.md)
  --upload-only  upload the media but do NOT create the post (safe end-to-end auth test)

Env:
  LINKEDIN_ACCESS_TOKEN    OAuth 2.0 access token (scope: w_member_social)
  LINKEDIN_PERSON_URN      e.g. urn:li:person:AbCdEfGhIj

Token renewal (every ~55 days): .venv/bin/python scripts/linkedin-token.py

API flow (versioned REST API — the legacy /v2/assets + /v2/ugcPosts was sunset mid-2026):
  Step 1: POST /rest/images?action=initializeUpload    → upload URL + image URN
          (or /rest/documents for PDF carousels)
  Step 2: PUT  <upload_url>                            → upload bytes
  Step 3: POST /rest/posts                             → create post with media
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

import requests

API_BASE = "https://api.linkedin.com/rest"
# LinkedIn API versions sunset ~1 year after release. If publishing fails with
# 426 NONEXISTENT_VERSION, bump this to a currently active YYYYMM version.
API_VERSION = "202606"

# Characters reserved by LinkedIn's "Little Text Format" in post commentary.
LITTLE_TEXT_RESERVED = "\\|{}@[]()<>#*_~"


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        print(f"error: missing env var {name}", file=sys.stderr)
        sys.exit(2)
    return v


def auth_headers(content_type: str | None = None) -> dict:
    h = {
        "Authorization": f"Bearer {env('LINKEDIN_ACCESS_TOKEN')}",
        "LinkedIn-Version": API_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }
    if content_type:
        h["Content-Type"] = content_type
    return h


def escape_commentary(text: str) -> str:
    for ch in LITTLE_TEXT_RESERVED:
        text = text.replace(ch, "\\" + ch)
    return text


def initialize_upload(person_urn: str, kind: str) -> tuple[str, str]:
    """Step 1: initialize an upload. `kind` is "images" or "documents".
    Returns (upload_url, media_urn).
    """
    payload = {"initializeUploadRequest": {"owner": person_urn}}
    r = requests.post(
        f"{API_BASE}/{kind}?action=initializeUpload",
        headers=auth_headers("application/json"),
        json=payload,
        timeout=30,
    )
    if r.status_code >= 400:
        print(f"error initializing upload {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    value = r.json()["value"]
    return value["uploadUrl"], value["image" if kind == "images" else "document"]


def upload_binary(upload_url: str, file_path: str, content_type: str) -> None:
    """Step 2: PUT the file bytes to the presigned upload URL."""
    with open(file_path, "rb") as f:
        data = f.read()
    r = requests.put(
        upload_url,
        data=data,
        headers={
            "Authorization": f"Bearer {env('LINKEDIN_ACCESS_TOKEN')}",
            "Content-Type": content_type,
        },
        timeout=120,
    )
    if r.status_code >= 400:
        print(f"error uploading file {r.status_code}: {r.text[:500]}", file=sys.stderr)
        sys.exit(1)


def create_post(person_urn: str, text: str, media_urn: str, doc_title: str = "") -> str:
    """Step 3: Create the post. Returns the post URN."""
    media: dict = {"id": media_urn}
    if doc_title:
        media["title"] = doc_title
    payload = {
        "author": person_urn,
        "commentary": escape_commentary(text),
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {"media": media},
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    r = requests.post(
        f"{API_BASE}/posts",
        headers=auth_headers("application/json"),
        json=payload,
        timeout=60,
    )
    if r.status_code >= 400:
        print(f"error creating post {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    return r.headers.get("x-restli-id") or r.headers.get("X-RestLi-Id") or "<no id>"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("media_path", help="Path to card.jpg (image) or card.pdf (carousel)")
    ap.add_argument("drafts_dir")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print payload without calling the API")
    ap.add_argument("--upload-only", action="store_true",
                    help="Upload media but skip post creation (auth/endpoint test)")
    args = ap.parse_args()

    person_urn = env("LINKEDIN_PERSON_URN")
    post_text = Path(args.drafts_dir, "post.md").read_text().strip()

    media_path = Path(args.media_path)
    if media_path.suffix.lower() == ".pdf":
        kind, content_type = "documents", "application/pdf"
        meta_for_title = Path(args.drafts_dir, "post.meta.json")
        doc_title = ""
        if meta_for_title.exists():
            try:
                m = json.loads(meta_for_title.read_text())
                doc_title = (m.get("template_data", {})
                              .get("cover", {})
                              .get("edition", "")) or m.get("topic", "")
            except Exception:
                pass
        doc_title = doc_title or "Guide"
    else:
        kind, content_type = "images", "image/jpeg"
        doc_title = ""

    if args.dry_run:
        print("=== DRY RUN ===")
        print(f"person_urn:  {person_urn}")
        print(f"media_path:  {args.media_path}  ({kind})")
        print(f"post_text:\n{post_text[:300]}...")
        print(f"Would call: initializeUpload({kind}) → PUT {content_type} → POST /rest/posts")
        return

    print(f"Initializing {kind} upload...", flush=True)
    upload_url, media_urn = initialize_upload(person_urn, kind)

    print(f"Uploading {content_type}...", flush=True)
    upload_binary(upload_url, args.media_path, content_type)

    if args.upload_only:
        print(f"upload OK — media URN: {media_urn} (post NOT created, --upload-only)")
        return

    print("Creating post...", flush=True)
    post_urn = create_post(person_urn, post_text, media_urn, doc_title=doc_title)

    linkedin_url = f"https://www.linkedin.com/feed/update/{post_urn}/"
    print(f"post URN: {post_urn}")
    print(f"URL:      {linkedin_url}")

    meta_path = Path(args.drafts_dir, "post.meta.json")
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        meta["linkedin_post_urn"] = post_urn
        meta["linkedin_url"] = linkedin_url
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")


if __name__ == "__main__":
    main()
