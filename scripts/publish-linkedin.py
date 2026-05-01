"""publish-linkedin.py — upload an image + publish a LinkedIn post via the LinkedIn REST API v2.

Usage:
  python scripts/publish-linkedin.py <image_path> <drafts_dir> [--at ISO_8601]

  <image_path>   e.g. drafts/2026-04-30/card.jpg
  <drafts_dir>   e.g. drafts/2026-04-30  (must contain post.md)
  --at           ISO-8601 scheduled time (not supported natively by UGC Posts API —
                 if you need scheduling, use --at to print the payload for manual review)

Env:
  LINKEDIN_ACCESS_TOKEN    OAuth 2.0 access token (scope: w_member_social)
  LINKEDIN_PERSON_URN      e.g. urn:li:person:AbCdEfGhIj

Setup (one-time, done by Josh):
  1. Create a LinkedIn Developer App at developer.linkedin.com
  2. Add "Share on LinkedIn" product (grants w_member_social scope)
  3. Complete OAuth 2.0 Authorization Code Flow to get access token
  4. Token is valid for 60 days — refresh before expiry and update GitHub Secret

API flow:
  Step 1: POST /v2/assets?action=registerUpload   → upload URL + asset URN
  Step 2: PUT  <upload_url>                        → upload image bytes
  Step 3: POST /v2/ugcPosts                        → create post with image
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

import requests

API_BASE = "https://api.linkedin.com/v2"


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        print(f"error: missing env var {name}", file=sys.stderr)
        sys.exit(2)
    return v


def auth_headers(content_type: str | None = None) -> dict:
    h = {
        "Authorization": f"Bearer {env('LINKEDIN_ACCESS_TOKEN')}",
        "LinkedIn-Version": "202401",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    if content_type:
        h["Content-Type"] = content_type
    return h


def register_upload(person_urn: str) -> tuple[str, str]:
    """Step 1: Register an image upload. Returns (upload_url, asset_urn)."""
    payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": person_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent",
                }
            ],
        }
    }
    r = requests.post(
        f"{API_BASE}/assets?action=registerUpload",
        headers=auth_headers("application/json"),
        json=payload,
        timeout=30,
    )
    if r.status_code >= 400:
        print(f"error registering upload {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    data = r.json()
    upload_url = data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn = data["value"]["asset"]
    return upload_url, asset_urn


def upload_image(upload_url: str, image_path: str) -> None:
    """Step 2: PUT the image bytes to the presigned upload URL."""
    with open(image_path, "rb") as f:
        data = f.read()
    r = requests.put(
        upload_url,
        data=data,
        headers={"Content-Type": "image/jpeg"},
        timeout=120,
    )
    if r.status_code >= 400:
        print(f"error uploading image {r.status_code}: {r.text[:500]}", file=sys.stderr)
        sys.exit(1)


def create_post(person_urn: str, text: str, asset_urn: str) -> str:
    """Step 3: Create a UGC post. Returns the post URN."""
    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "description": {"text": ""},
                        "media": asset_urn,
                        "title": {"text": ""},
                    }
                ],
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }
    r = requests.post(
        f"{API_BASE}/ugcPosts",
        headers=auth_headers("application/json"),
        json=payload,
        timeout=60,
    )
    if r.status_code >= 400:
        print(f"error creating post {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    post_urn = r.headers.get("X-RestLi-Id") or r.json().get("id", "<no id>")
    return post_urn


def urn_to_url(post_urn: str, person_urn: str) -> str:
    """Convert post URN to LinkedIn URL (best-effort, URN format varies)."""
    ugc_id = post_urn.split(":")[-1] if ":" in post_urn else post_urn
    person_id = person_urn.split(":")[-1] if ":" in person_urn else person_urn
    return f"https://www.linkedin.com/feed/update/{post_urn}/"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("image_path")
    ap.add_argument("drafts_dir")
    ap.add_argument("--at", dest="scheduled_time", default=None,
                    help="ISO-8601 time (informational only — UGC Posts API posts immediately)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print payload without posting")
    args = ap.parse_args()

    person_urn = env("LINKEDIN_PERSON_URN")
    post_text = Path(args.drafts_dir, "post.md").read_text().strip()

    if args.dry_run:
        print("=== DRY RUN ===")
        print(f"person_urn:  {person_urn}")
        print(f"image_path:  {args.image_path}")
        print(f"post_text:\n{post_text[:300]}...")
        print("Would call: registerUpload → PUT image → ugcPosts")
        return

    if args.scheduled_time:
        print(f"note: --at is informational; LinkedIn UGC Posts API publishes immediately. "
              f"For scheduling, use LinkedIn's native scheduler or a wrapper service.")

    print("Registering image upload...", flush=True)
    upload_url, asset_urn = register_upload(person_urn)

    print("Uploading image...", flush=True)
    upload_image(upload_url, args.image_path)

    print("Creating post...", flush=True)
    post_urn = create_post(person_urn, post_text, asset_urn)

    linkedin_url = urn_to_url(post_urn, person_urn)
    print(f"post URN: {post_urn}")
    print(f"URL:      {linkedin_url}")

    # Persist to post.meta.json for Notion sync
    meta_path = Path(args.drafts_dir, "post.meta.json")
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        meta["linkedin_post_urn"] = post_urn
        meta["linkedin_url"] = linkedin_url
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")


if __name__ == "__main__":
    main()
