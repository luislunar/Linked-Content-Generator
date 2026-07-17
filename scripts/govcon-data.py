"""govcon-data.py — pull fresh small-business federal spending data from USAspending.gov.

Writes research/govcon-data-YYYY-MM-DD.md: a short digest the daily generators read
as OPTIONAL inspiration (data-led posts are a supplement, not the default).

Usage:
  python scripts/govcon-data.py

No API key required. If the API is down the script exits 0 without writing,
so the daily posts continue from the normal topic bank.
"""

from __future__ import annotations
import datetime as dt
import sys
from pathlib import Path

import requests

API = "https://api.usaspending.gov/api/v2/search/spending_by_category"
OUT_DIR = Path("research")


def last_quarter() -> tuple[str, str, str]:
    """Return (start, end, label) for the most recent full calendar quarter."""
    today = dt.date.today()
    q_start_month = 3 * ((today.month - 1) // 3) + 1
    this_q_start = dt.date(today.year, q_start_month, 1)
    prev_q_end = this_q_start - dt.timedelta(days=1)
    prev_q_start = dt.date(prev_q_end.year, 3 * ((prev_q_end.month - 1) // 3) + 1, 1)
    label = f"Q{(prev_q_start.month - 1) // 3 + 1} {prev_q_start.year}"
    return prev_q_start.isoformat(), prev_q_end.isoformat(), label


def top_categories(category: str, start: str, end: str, limit: int = 8) -> list[dict]:
    r = requests.post(
        f"{API}/{category}/",
        json={
            "filters": {
                "time_period": [{"start_date": start, "end_date": end}],
                "recipient_type_names": ["small_business"],
            },
            "limit": limit,
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json().get("results", [])


def fmt_amount(amount: float) -> str:
    if amount >= 1e9:
        return f"${amount / 1e9:.1f}B"
    if amount >= 1e6:
        return f"${amount / 1e6:.0f}M"
    return f"${amount:,.0f}"


def main() -> None:
    start, end, label = last_quarter()
    try:
        by_industry = top_categories("naics", start, end)
        by_agency = top_categories("awarding_agency", start, end)
    except Exception as e:
        print(f"warning: USAspending unavailable ({e}) — no digest written, posts continue as usual")
        return

    if not by_industry:
        print("warning: empty response — no digest written")
        return

    total = sum(r.get("amount", 0) for r in by_industry)
    today = dt.date.today().isoformat()
    lines = [
        f"# GovCon data digest — week of {today}",
        "",
        f"Federal awards to **small businesses**, {label} (source: USAspending.gov —",
        "cite it on any card that uses these numbers).",
        "",
        f"## Top industries ({label}, small business recipients)",
        "",
    ]
    for r in by_industry:
        lines.append(f"- {r.get('name', '?')}: **{fmt_amount(r.get('amount', 0))}**")
    lines += [
        "",
        f"Top-{len(by_industry)} industries combined: **{fmt_amount(total)}** in one quarter.",
        "",
        f"## Top awarding agencies ({label}, small business recipients)",
        "",
    ]
    for r in by_agency[:6]:
        lines.append(f"- {r.get('name', '?')}: **{fmt_amount(r.get('amount', 0))}**")
    lines += [
        "",
        "## How to use (all profiles)",
        "",
        "- OPTIONAL inspiration: at most 1-2 data-led posts per profile per week. The",
        "  normal topic bank remains the default — do not force a stat post daily.",
        "- Angle it to the ICP (owners *considering* federal): the money is real,",
        "  it goes to companies their size, the barrier is the paperwork not the odds.",
        "- Never two profiles using the same figure on the same day (uniqueness rules).",
        "- Round numbers as shown; always credit USAspending.gov on the card.",
    ]
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"govcon-data-{today}.md"
    out.write_text("\n".join(lines) + "\n")

    # Keep only the 3 most recent digests.
    digests = sorted(OUT_DIR.glob("govcon-data-*.md"))
    for old in digests[:-3]:
        old.unlink()

    print(f"digest written: {out}")


if __name__ == "__main__":
    main()
