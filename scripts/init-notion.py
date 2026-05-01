"""init-notion.py — one-shot: creates the 3 Notion databases this repo needs.

Run this locally once. It prints three `NOTION_*_DB_ID=...` lines you paste into
GitHub repo secrets.

Prereqs:
  1. Created a Notion integration at https://www.notion.so/profile/integrations
     and copied its internal integration token.
  2. Created a parent page in Notion (any workspace page works).
  3. On that parent page: ... menu -> Connections -> Connect to -> your integration.

Usage:
  export NOTION_TOKEN=secret_...           # or ntn_...
  python scripts/init-notion.py "<parent_page_url_or_id>"

Run it once. If you re-run, it creates duplicate DBs — don't.
"""

from __future__ import annotations
import os
import re
import sys

import requests

NOTION_VERSION = "2022-06-28"
API = "https://api.notion.com/v1"


def token() -> str:
    t = os.environ.get("NOTION_TOKEN")
    if not t:
        print("set NOTION_TOKEN env var", file=sys.stderr)
        sys.exit(2)
    return t


def headers() -> dict:
    return {
        "Authorization": f"Bearer {token()}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def extract_page_id(page_url_or_id: str) -> str:
    """Accepts a Notion URL (with or without a slug prefix) or a raw 32-char ID.
    Returns the UUID in canonical dashed form."""
    s = page_url_or_id.strip()
    # Match the last 32 hex chars in the string — that's the page ID in any URL form.
    m = re.search(r"([0-9a-fA-F]{32})", s.replace("-", ""))
    if not m:
        print(f"couldn't parse a page id from: {page_url_or_id}", file=sys.stderr)
        sys.exit(2)
    raw = m.group(1)
    return f"{raw[0:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:32]}"


def create_db(parent_id: str, title: str, properties: dict) -> dict:
    payload = {
        "parent": {"type": "page_id", "page_id": parent_id},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": properties,
    }
    r = requests.post(f"{API}/databases", headers=headers(), json=payload, timeout=30)
    if r.status_code >= 400:
        print(f"Notion error creating '{title}': {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(1)
    return r.json()


# --- Schemas ----------------------------------------------------------------

def magnets_schema() -> dict:
    return {
        "Title": {"title": {}},
        "Format": {
            "select": {
                "options": [
                    {"name": n} for n in
                    ["checklist", "template", "swipe", "cheat-sheet", "teardown", "story", "calculator"]
                ]
            }
        },
        "Topic": {
            "multi_select": {
                "options": [
                    {"name": n} for n in
                    ["gsa_basics", "pricing", "compliance", "marketing", "case_study", "founder_story", "bid_strategy"]
                ]
            }
        },
        "Notion Public URL": {"url": {}},
        "Downloads / Opt-ins": {"number": {"format": "number"}},
        "Created At": {"created_time": {}},
    }


def posts_schema(magnets_db_id: str, experiments_db_id: str) -> dict:
    return {
        "Name": {"title": {}},
        "Date": {"date": {}},
        "Hook": {"rich_text": {}},
        "Body": {"rich_text": {}},
        "CTA": {"rich_text": {}},
        "Lead Magnet": {"relation": {"database_id": magnets_db_id, "type": "single_property", "single_property": {}}},
        "Format": {
            "select": {"options": [{"name": n} for n in ["checklist", "template", "swipe", "cheat-sheet", "teardown", "story", "calculator"]]}
        },
        "Topic": {
            "multi_select": {"options": [{"name": n} for n in ["gsa_basics", "pricing", "compliance", "marketing", "case_study", "founder_story", "bid_strategy"]]}
        },
        "Hook Pattern": {
            "select": {"options": [{"name": n} for n in ["contrarian", "list", "question", "number", "story", "myth-bust"]]}
        },
        "Experiment": {"relation": {"database_id": experiments_db_id, "type": "single_property", "single_property": {}}},
        "Status": {"select": {"options": [{"name": n, "color": c} for n, c in [
            ("draft", "gray"), ("approved", "yellow"), ("published", "green"), ("archived", "default")
        ]]}},
        "Impressions": {"number": {"format": "number"}},
        "Reactions": {"number": {"format": "number"}},
        "Comments": {"number": {"format": "number"}},
        "Shares": {"number": {"format": "number"}},
        "Opt-ins": {"number": {"format": "number"}},
        "Engagement Score": {
            "formula": {
                "expression": (
                    "prop(\"Impressions\") + 10 * prop(\"Reactions\") + "
                    "30 * prop(\"Comments\") + 50 * prop(\"Opt-ins\")"
                )
            }
        },
        "LinkedIn URL": {"url": {}},
    }


def experiments_schema() -> dict:
    return {
        "ID": {"title": {}},
        "Hypothesis": {"rich_text": {}},
        "Variable Changed": {"select": {"options": [{"name": n} for n in [
            "hook_pattern_weights", "format_weights", "topic_focus", "cta_style",
            "overlay_text_pattern", "magnet_length", "tone"
        ]]}},
        "Baseline Start": {"date": {}},
        "Baseline End": {"date": {}},
        "Test Start": {"date": {}},
        "Test End": {"date": {}},
        "Baseline Median Score": {"number": {"format": "number"}},
        "Test Median Score": {"number": {"format": "number"}},
        "Decision": {"select": {"options": [
            {"name": "active", "color": "yellow"},
            {"name": "keep", "color": "green"},
            {"name": "revert", "color": "red"}
        ]}},
        "Commit SHA": {"rich_text": {}},
    }


# --- Main --------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    parent_id = extract_page_id(sys.argv[1])

    # Order matters: Magnets + Experiments must exist before Posts (which relates to both).
    magnets = create_db(parent_id, "Linked Content — Magnets", magnets_schema())
    experiments = create_db(parent_id, "Linked Content — Experiments", experiments_schema())
    posts = create_db(parent_id, "Linked Content — Posts", posts_schema(magnets["id"], experiments["id"]))

    print()
    print("=" * 60)
    print("Paste these into your GitHub repo secrets:")
    print("=" * 60)
    print(f"NOTION_MAGNETS_DB_ID={magnets['id']}")
    print(f"NOTION_EXPERIMENTS_DB_ID={experiments['id']}")
    print(f"NOTION_POSTS_DB_ID={posts['id']}")
    print()
    print("Notion URLs (for your reference):")
    print(f"  Magnets:     {magnets['url']}")
    print(f"  Experiments: {experiments['url']}")
    print(f"  Posts:       {posts['url']}")


if __name__ == "__main__":
    main()
