"""notion-sync.py — tiny CLI around the Notion REST API.

Subcommands:
  create-post   <drafts_dir>                   create Posts DB row (status=draft) from post.md + post.meta.json
  active-experiment                            print active experiment as JSON (or {})
  last-14-days                                 print recent Posts rows as JSON
  update-published <post_id> <linkedin_url>    flip status=published and set URL

Env: NOTION_TOKEN, NOTION_POSTS_DB_ID, NOTION_EXPERIMENTS_DB_ID
Requires: requests. No other deps.
"""

from __future__ import annotations
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

NOTION_VERSION = "2022-06-28"
API = "https://api.notion.com/v1"


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        print(f"missing env var: {name}", file=sys.stderr)
        sys.exit(2)
    return v


def headers() -> dict:
    return {
        "Authorization": f"Bearer {env('NOTION_TOKEN')}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


# ---- Markdown → Notion blocks ------------------------------------------------

def md_to_blocks(markdown: str) -> list[dict]:
    blocks: list[dict] = []
    in_code = False
    code_buf: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("```"):
            if in_code:
                blocks.append(_code("\n".join(code_buf)))
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        if not line.strip():
            continue
        if line.startswith("# "):
            blocks.append(_heading(1, line[2:]))
        elif line.startswith("## "):
            blocks.append(_heading(2, line[3:]))
        elif line.startswith("### "):
            blocks.append(_heading(3, line[4:]))
        elif line.lstrip().startswith(("- [ ] ", "- [x] ")):
            checked = line.lstrip().startswith("- [x]")
            blocks.append(_todo(line.lstrip()[6:], checked))
        elif line.lstrip().startswith(("- ", "* ")):
            blocks.append(_bullet(line.lstrip()[2:]))
        elif line.lstrip()[:2].isdigit() and line.lstrip()[2:3] == "." or (line.lstrip()[:1].isdigit() and line.lstrip()[1:2] == "."):
            # numbered list — naive
            content = line.lstrip().split(".", 1)[1].strip() if "." in line else line.lstrip()
            blocks.append(_numbered(content))
        else:
            blocks.append(_paragraph(line))
    if in_code and code_buf:
        blocks.append(_code("\n".join(code_buf)))
    # Notion caps children at 100 blocks per request — slice safely
    return blocks[:100]


def _text(s: str) -> list[dict]:
    return [{"type": "text", "text": {"content": s[:2000]}}]


def _paragraph(s: str) -> dict:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": _text(s)}}


def _heading(n: int, s: str) -> dict:
    k = f"heading_{n}"
    return {"object": "block", "type": k, k: {"rich_text": _text(s)}}


def _bullet(s: str) -> dict:
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": _text(s)}}


def _numbered(s: str) -> dict:
    return {"object": "block", "type": "numbered_list_item", "numbered_list_item": {"rich_text": _text(s)}}


def _todo(s: str, checked: bool) -> dict:
    return {"object": "block", "type": "to_do", "to_do": {"rich_text": _text(s), "checked": checked}}


def _code(s: str) -> dict:
    return {"object": "block", "type": "code", "code": {"rich_text": _text(s), "language": "plain text"}}


# ---- Drafts dir helpers ------------------------------------------------------

def _read_drafts(drafts_dir: str) -> tuple[dict, str]:
    d = Path(drafts_dir)
    meta = json.loads((d / "post.meta.json").read_text())
    post_md = (d / "post.md").read_text()
    return meta, post_md


# ---- Create post -------------------------------------------------------------

def create_post(drafts_dir: str) -> None:
    meta, post_md = _read_drafts(drafts_dir)
    d = Path(drafts_dir)
    date_str = d.name  # YYYY-MM-DD

    # Split post_md into hook/body/cta heuristically: first non-empty line = hook,
    # last non-empty line = CTA, middle = body. Good enough for v1 — the generator
    # can emit these as explicit fields in post.meta.json later.
    lines = [ln for ln in post_md.splitlines() if ln.strip()]
    hook = lines[0] if lines else ""
    cta = lines[-1] if len(lines) > 1 else ""
    body = "\n".join(lines[1:-1]) if len(lines) > 2 else ""

    name = f"{date_str} — {hook[:80]}"

    db_id = env("NOTION_POSTS_DB_ID")
    props = {
        "Name": {"title": _text(name)},
        "Date": {"date": {"start": date_str}},
        "Hook": {"rich_text": _text(hook)},
        "Body": {"rich_text": _text(body)},
        "CTA": {"rich_text": _text(cta)},
        "Format": {"select": {"name": meta["format"]}},
        "Topic": {"multi_select": [{"name": meta["topic"]}]},
        "Hook Pattern": {"select": {"name": meta["hook_pattern"]}},
        "Status": {"select": {"name": "draft"}},
    }
    payload = {"parent": {"database_id": db_id}, "properties": props}
    r = requests.post(f"{API}/pages", headers=headers(), json=payload, timeout=30)
    if r.status_code >= 400:
        print(f"Notion error: {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(1)
    page = r.json()
    print(f"{page['url']}\t{page['id']}")


# ---- Misc --------------------------------------------------------------------

def last_14_days() -> None:
    db_id = env("NOTION_POSTS_DB_ID")
    since = (datetime.now(timezone.utc) - timedelta(days=14)).date().isoformat()
    payload = {
        "filter": {"property": "Date", "date": {"on_or_after": since}},
        "page_size": 100,
    }
    r = requests.post(f"{API}/databases/{db_id}/query", headers=headers(), json=payload, timeout=30)
    r.raise_for_status()
    print(json.dumps(r.json(), indent=2))


def update_published(post_id: str, linkedin_url: str) -> None:
    props = {"Status": {"select": {"name": "published"}}}
    if linkedin_url and linkedin_url.startswith("http"):
        props["LinkedIn URL"] = {"url": linkedin_url}
    payload = {"properties": props}
    r = requests.patch(f"{API}/pages/{post_id}", headers=headers(), json=payload, timeout=30)
    if r.status_code >= 400:
        print(f"Notion error: {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(1)
    print(f"updated {post_id} → status=published")


def cmd(argv: list[str]) -> None:
    if not argv:
        print(__doc__)
        sys.exit(1)
    sub = argv[0]
    if sub == "create-post":
        create_post(argv[1])
    elif sub == "active-experiment":
        print("{}")
    elif sub == "last-14-days":
        last_14_days()
    elif sub == "update-published":
        update_published(argv[1], argv[2] if len(argv) > 2 else "")
    else:
        print(f"not yet implemented: {sub}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    cmd(sys.argv[1:])
