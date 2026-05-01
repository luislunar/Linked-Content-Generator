"""publish-blotato.py — upload a video + publish/schedule a LinkedIn post via Blotato's REST API.

Usage:
  python scripts/publish-blotato.py <video_path> <drafts_dir> [--at ISO_8601]

  <drafts_dir>  e.g. drafts/2026-04-19   (must contain post.md)
  --at          ISO 8601 scheduled time, e.g. 2026-04-20T14:00:00+00:00
                if omitted, posts immediately.

Env:
  BLOTATO_API_KEY
  BLOTATO_LINKEDIN_ACCOUNT_ID   (from GET /users/me/accounts)
  BLOTATO_LINKEDIN_PAGE_ID      (optional — only for LinkedIn Company Pages)
  BLOTATO_API_BASE              (optional — defaults to https://backend.blotato.com/v2)

API shape (confirmed against help.blotato.com/api, April 2026):
  1. POST /media/uploads  body={"filename": "..."}  →  {presignedUrl, publicUrl}
  2. PUT  <presignedUrl>  body=<raw bytes>
  3. POST /posts          body={post: {accountId, content:{text, mediaUrls, platform},
                                       target:{targetType, pageId?}}, scheduledTime?}
                          → {postSubmissionId}
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

import requests

API_BASE = os.environ.get("BLOTATO_API_BASE", "https://backend.blotato.com/v2")


def env(name: str, required: bool = True) -> str | None:
    v = os.environ.get(name)
    if required and not v:
        print(f"missing env var: {name}", file=sys.stderr)
        sys.exit(2)
    return v


def auth_headers(json_body: bool = False) -> dict:
    h = {"blotato-api-key": env("BLOTATO_API_KEY")}
    if json_body:
        h["Content-Type"] = "application/json"
    return h


def upload_local_file(path: str) -> str:
    """Two-step presigned upload: ask Blotato for a signed URL, then PUT the bytes.
    Returns the public URL we pass to the post's mediaUrls."""
    filename = os.path.basename(path)
    r = requests.post(
        f"{API_BASE}/media/uploads",
        headers=auth_headers(json_body=True),
        json={"filename": filename},
        timeout=60,
    )
    if r.status_code >= 400:
        print(f"presigned-upload error {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    body = r.json()
    presigned = body["presignedUrl"]
    public = body["publicUrl"]

    with open(path, "rb") as f:
        data = f.read()
    put = requests.put(presigned, data=data, headers={"Content-Type": "video/mp4"}, timeout=300)
    if put.status_code >= 400:
        print(f"presigned PUT error {put.status_code}: {put.text[:500]}", file=sys.stderr)
        sys.exit(1)
    return public


def create_post(text: str, media_url: str, scheduled_time: str | None) -> dict:
    target = {"targetType": "linkedin"}
    page_id = env("BLOTATO_LINKEDIN_PAGE_ID", required=False)
    if page_id:
        target["pageId"] = page_id

    payload = {
        "post": {
            "accountId": env("BLOTATO_LINKEDIN_ACCOUNT_ID"),
            "content": {
                "text": text,
                "mediaUrls": [media_url],
                "platform": "linkedin",
            },
            "target": target,
        }
    }
    if scheduled_time:
        payload["scheduledTime"] = scheduled_time

    r = requests.post(
        f"{API_BASE}/posts",
        headers=auth_headers(json_body=True),
        json=payload,
        timeout=60,
    )
    if r.status_code >= 400:
        print(f"post-create error {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    return r.json()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video_path")
    ap.add_argument("drafts_dir")
    ap.add_argument("--at", dest="scheduled_time", default=None,
                    help="ISO-8601 scheduled publish time (e.g. 2026-04-20T14:00:00+00:00). "
                         "If omitted, publishes immediately.")
    args = ap.parse_args()

    post_text = Path(args.drafts_dir, "post.md").read_text().strip()

    media_url = upload_local_file(args.video_path)
    result = create_post(post_text, media_url, args.scheduled_time)

    submission_id = result.get("postSubmissionId", "<no id returned>")
    print(f"submissionId: {submission_id}")
    print(f"mediaUrl:     {media_url}")
    if args.scheduled_time:
        print(f"scheduled:    {args.scheduled_time}")
    else:
        print("published:    now")

    # Persist the submission id into post.meta.json so sync-linkedin-url.py can resolve
    # the published LinkedIn URL later via GET /v2/posts/{id}.
    meta_path = Path(args.drafts_dir, "post.meta.json")
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        meta["blotato_submission_id"] = submission_id
        if args.scheduled_time:
            meta["blotato_scheduled_time"] = args.scheduled_time
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")


if __name__ == "__main__":
    main()
