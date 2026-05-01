"""reddit-scrape.py — fetch top posts from GovCon subreddits for weekly topic inspiration.

Uses Reddit's public JSON endpoint (no API key required).
Filters posts by ICP-relevant keywords and saves top results to research/.

Usage:
  python scripts/reddit-scrape.py [--days 7] [--limit 25]
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import requests

SUBREDDITS_FILE = Path("research/subreddits.md")
OUTPUT_DIR = Path("research")

ICP_KEYWORDS = [
    "gsa", "gsa schedule", "sam", "sam.gov", "federal contract", "federal contracting",
    "small business", "set-aside", "naics", "8(a)", "8a ", "wosb", "sdvosb", "hubzone",
    "oasis", "sewp", "gwac", "mas ", "multiple award schedule", "past performance",
    "teaming", "subcontract", "capability statement", "contracting officer",
    "cage code", "far ", "dfars", "rfq", "rfp", "sources sought", "industry day",
    "recompete", "prime contractor", "govcon", "government contracting",
]

HEADERS = {"User-Agent": "GSAFocusResearchBot/1.0 (content research only)"}


def parse_subreddits(md_path: Path) -> list[str]:
    """Extract subreddit names from the subreddits.md file."""
    text = md_path.read_text()
    names = re.findall(r"reddit\.com/r/([A-Za-z0-9_]+)", text)
    return names


def is_icp_relevant(title: str, text: str) -> bool:
    combined = (title + " " + text).lower()
    return any(kw in combined for kw in ICP_KEYWORDS)


def fetch_top_posts(subreddit: str, limit: int, days: int) -> list[dict]:
    timeframe = "week" if days <= 7 else "month"
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t={timeframe}&limit={limit}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"  warning: failed to fetch r/{subreddit} — {e}", file=sys.stderr)
        return []

    posts = []
    now = datetime.now(timezone.utc).timestamp()
    cutoff = now - (days * 86400)

    for child in r.json().get("data", {}).get("children", []):
        d = child["data"]
        if d.get("created_utc", 0) < cutoff:
            continue
        title = d.get("title", "")
        selftext = d.get("selftext", "")
        if not is_icp_relevant(title, selftext):
            continue
        posts.append({
            "subreddit": subreddit,
            "title": title,
            "score": d.get("score", 0),
            "comments": d.get("num_comments", 0),
            "url": f"https://www.reddit.com{d.get('permalink', '')}",
            "preview": selftext[:200].strip().replace("\n", " ") if selftext else "",
        })

    return posts


def write_markdown(all_posts: list[dict], output_dir: Path, date_str: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"reddit-trends-{date_str}.md"

    lines = [
        f"# Reddit GovCon Trends — {date_str}",
        "",
        "Top posts from r/GovernmentContracting, r/govcon, r/fednews filtered by ICP keywords.",
        "Use these as topic inspiration — stay within the GSA/federal contracting space.",
        "",
    ]

    if not all_posts:
        lines.append("No relevant posts found this week.")
    else:
        for i, p in enumerate(all_posts[:15], 1):
            lines += [
                f"## {i}. {p['title']}",
                f"- **Subreddit:** r/{p['subreddit']}",
                f"- **Score:** {p['score']} | **Comments:** {p['comments']}",
                f"- **URL:** {p['url']}",
            ]
            if p["preview"]:
                lines += [f"- **Preview:** {p['preview']}…"]
            lines.append("")

    out_path.write_text("\n".join(lines))
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7, help="Look back N days (default 7)")
    ap.add_argument("--limit", type=int, default=25, help="Posts to fetch per subreddit (default 25)")
    args = ap.parse_args()

    if not SUBREDDITS_FILE.exists():
        print(f"error: {SUBREDDITS_FILE} not found", file=sys.stderr)
        sys.exit(1)

    subreddits = parse_subreddits(SUBREDDITS_FILE)
    if not subreddits:
        print("error: no subreddits found in subreddits.md", file=sys.stderr)
        sys.exit(1)

    print(f"Scraping {len(subreddits)} subreddits in parallel (top/{args.days}d, limit={args.limit})...")
    all_posts: list[dict] = []

    def _fetch(sub: str) -> tuple[str, list[dict]]:
        return sub, fetch_top_posts(sub, args.limit, args.days)

    with ThreadPoolExecutor(max_workers=len(subreddits)) as ex:
        for sub, posts in ex.map(_fetch, subreddits):
            print(f"  r/{sub}: {len(posts)} relevant posts")
            all_posts.extend(posts)

    all_posts.sort(key=lambda p: p["score"], reverse=True)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = write_markdown(all_posts, OUTPUT_DIR, date_str)
    print(f"\nSaved {min(len(all_posts), 15)} posts to {out_path}")


if __name__ == "__main__":
    main()
