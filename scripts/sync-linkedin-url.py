"""sync-linkedin-url.py — resolve Blotato submissions to LinkedIn URLs, write back to post.meta.json.

Usage:
  python scripts/sync-linkedin-url.py            # process all drafts
  python scripts/sync-linkedin-url.py <dir>      # just one

For each draft that has `blotato_submission_id` but no `linkedin_url`, GET the
Blotato post. When `status == "published"`, copy `publicUrl` into `linkedin_url`.
Skips already-resolved drafts. Safe to run every N min via cron.

Env:
  BLOTATO_API_KEY
  BLOTATO_API_BASE (optional, defaults to https://backend.blotato.com/v2)
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

import requests

API_BASE = os.environ.get("BLOTATO_API_BASE", "https://backend.blotato.com/v2")


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        print(f"missing env: {name}", file=sys.stderr)
        sys.exit(2)
    return v


def fetch_status(submission_id: str) -> dict:
    r = requests.get(
        f"{API_BASE}/posts/{submission_id}",
        headers={"blotato-api-key": env("BLOTATO_API_KEY")},
        timeout=30,
    )
    if r.status_code >= 400:
        print(f"status error {r.status_code}: {r.text[:300]}", file=sys.stderr)
        return {}
    return r.json()


def process_draft(draft: Path) -> None:
    meta_path = draft / "post.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    if meta.get("linkedin_url"):
        return  # already resolved
    sid = meta.get("blotato_submission_id")
    if not sid:
        return  # not published via Blotato yet

    status = fetch_status(sid)
    if status.get("status") == "published" and status.get("publicUrl"):
        meta["linkedin_url"] = status["publicUrl"]
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")
        print(f"{draft.name}: resolved → {status['publicUrl']}")
    else:
        print(f"{draft.name}: status={status.get('status', '?')} (not yet published)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("drafts_dir", nargs="?", default=None,
                    help="optional single draft path; default processes all drafts/")
    args = ap.parse_args()

    if args.drafts_dir:
        process_draft(Path(args.drafts_dir))
    else:
        for d in sorted(Path("drafts").iterdir()):
            if d.is_dir():
                process_draft(d)


if __name__ == "__main__":
    main()
