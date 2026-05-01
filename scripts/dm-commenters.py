"""dm-commenters.py — poll a LinkedIn post for trigger-word comments, DM the Notion magnet link.

Usage:
  python scripts/dm-commenters.py <drafts_dir> [--trigger GSA] [--dry-run]

  <drafts_dir>  e.g. drafts/2026-04-21 — must contain post.meta.json with:
                  - linkedin_url           (populated after Blotato publishes)
                  - notion_public_url
                  - overlay_text.main      (used to personalize DM)

Env:
  UNIPILE_DSN                e.g. apiXX.unipile.com:1XXXX     (shown on dashboard)
  UNIPILE_ACCESS_TOKEN       generated at dashboard.unipile.com/access-tokens
  UNIPILE_LINKEDIN_ACCOUNT_ID   the connected account id (GET /accounts)

Dedupe state lives at <drafts_dir>/dms-sent.json — list of commenter provider IDs
already messaged. Safe to re-run every 15 min via cron.
"""

from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        print(f"missing env: {name}", file=sys.stderr)
        sys.exit(2)
    return v


def api_base() -> str:
    return f"https://{env('UNIPILE_DSN')}/api/v1"


def headers() -> dict:
    return {"X-API-KEY": env("UNIPILE_ACCESS_TOKEN"), "accept": "application/json"}


POST_URN_RE = re.compile(r"(?:activity|ugcPost)[-:](\d+)")


def extract_post_urn(linkedin_url: str) -> str:
    """LinkedIn post URLs embed the activity id, e.g.
       /feed/update/urn:li:activity:7332661864792854528/  →  urn:li:activity:7332...
    """
    m = POST_URN_RE.search(linkedin_url)
    if not m:
        print(f"can't extract activity id from {linkedin_url!r}", file=sys.stderr)
        sys.exit(1)
    # Unipile accepts the activity-form URN for LinkedIn posts.
    return f"urn:li:activity:{m.group(1)}"


def list_comments(post_urn: str, account_id: str) -> list[dict]:
    r = requests.get(
        f"{api_base()}/posts/{post_urn}/comments",
        headers=headers(),
        params={"account_id": account_id},
        timeout=30,
    )
    if r.status_code >= 400:
        print(f"list-comments error {r.status_code}: {r.text[:500]}", file=sys.stderr)
        sys.exit(1)
    body = r.json()
    # Unipile list endpoints typically wrap results in {items: [...]}.
    return body.get("items") if isinstance(body, dict) else body


def commenter_id(c: dict) -> str | None:
    # Defensive: try the common shapes. First run with --dry-run to eyeball.
    for path in (
        ("author", "id"),
        ("author", "provider_id"),
        ("author", "public_identifier"),
        ("author", "urn"),
        ("provider_internal_id",),
    ):
        v: object = c
        ok = True
        for key in path:
            if isinstance(v, dict) and key in v:
                v = v[key]
            else:
                ok = False
                break
        if ok and isinstance(v, str) and v:
            return v
    return None


def commenter_first_name(c: dict) -> str:
    author = c.get("author") or {}
    for key in ("first_name", "firstName", "name"):
        v = author.get(key)
        if v:
            return str(v).split()[0]
    return "there"


def send_dm(account_id: str, attendee_id: str, text: str) -> dict:
    r = requests.post(
        f"{api_base()}/chats",
        headers={**headers(), "Content-Type": "application/json"},
        json={"account_id": account_id, "attendees_ids": [attendee_id], "text": text},
        timeout=30,
    )
    if r.status_code >= 400:
        print(f"send-dm error {r.status_code}: {r.text[:500]}", file=sys.stderr)
        # Don't exit — one bad DM shouldn't kill the batch.
        return {}
    return r.json()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("drafts_dir")
    ap.add_argument("--trigger", default="GSA", help="case-insensitive keyword in comment text")
    ap.add_argument("--dry-run", action="store_true", help="print DMs instead of sending")
    args = ap.parse_args()

    draft = Path(args.drafts_dir)
    meta = json.loads((draft / "post.meta.json").read_text())
    linkedin_url = meta.get("linkedin_url")
    if not linkedin_url:
        print(f"{draft}/post.meta.json has no linkedin_url yet — post not published?", file=sys.stderr)
        sys.exit(0)  # soft-exit; cron will retry tomorrow
    magnet_url = meta["notion_public_url"]

    account_id = env("UNIPILE_LINKEDIN_ACCOUNT_ID")
    post_urn = extract_post_urn(linkedin_url)
    comments = list_comments(post_urn, account_id)

    sent_path = draft / "dms-sent.json"
    already = set(json.loads(sent_path.read_text())) if sent_path.exists() else set()

    trigger = args.trigger.lower()
    new_sent: list[str] = []
    for c in comments:
        text = (c.get("text") or "").lower()
        if trigger not in text:
            continue
        pid = commenter_id(c)
        if not pid or pid in already:
            continue

        first = commenter_first_name(c)
        dm = (
            f"Hey {first} — here's the magnet you asked about: {magnet_url}\n\n"
            "Lmk if it's useful. Happy to walk through the specifics if any of it's unclear."
        )

        if args.dry_run:
            print(f"[DRY] would DM {pid} ({first}): {dm[:80]}…")
        else:
            send_dm(account_id, pid, dm)
            print(f"DM sent → {pid} ({first})")
        new_sent.append(pid)

    if new_sent and not args.dry_run:
        already.update(new_sent)
        sent_path.write_text(json.dumps(sorted(already), indent=2))
    print(f"processed {len(comments)} comments, {len(new_sent)} new DM(s)")


if __name__ == "__main__":
    main()
