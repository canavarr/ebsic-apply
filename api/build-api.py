#!/usr/bin/env python3
"""
Build the public JSON API for ebsic.ee.

GitHub Pages serves static files with "Access-Control-Allow-Origin: *", so a
committed JSON file is a real, readable-from-anywhere API endpoint. This script
writes two of them:

    api/events.json     the club calendar
    api/portfolio.json  the club's holdings, valued with the latest prices

Both are generated, never hand-edited. The sources are the same files the site
itself reads, so the API can never disagree with the pages:

    events/events.json      written by the back office  -> api/events.json
    portfolio/positions.json  the holdings              -> api/portfolio.json
    portfolio/prices.json     written by refresh-prices.py

Usage:
    python3 build-api.py            # rebuild both endpoints
    python3 build-api.py --check    # exit 1 if the committed output is stale
"""

import json
import posixpath
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TALLINN = ZoneInfo("Europe/Tallinn")
except Exception:                      # no system tzdata (bare containers)
    TALLINN = None

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "api"
BASE = "https://ebsic.ee"

# The calendar is written in local Tallinn wall-clock time with no zone on it.
# Europe/Tallinn is EET (+02) in winter and EEST (+03) from the last Sunday in
# March to the last Sunday in October. zoneinfo knows the rule; the fallback
# below reproduces it for the rare environment with no tzdata installed.
def tallinn_offset(dt):
    def last_sunday(year, month):
        d = datetime(year + (month == 12), (month % 12) + 1, 1) - timedelta(days=1)
        return d - timedelta(days=(d.weekday() + 1) % 7)
    start = last_sunday(dt.year, 3).replace(hour=3)    # 01:00 UTC
    end = last_sunday(dt.year, 10).replace(hour=4)     # 01:00 UTC
    return timedelta(hours=3) if start <= dt < end else timedelta(hours=2)


def to_iso(local_str):
    """'2026-10-29T17:00' -> '2026-10-29T17:00:00+02:00'"""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$", str(local_str or ""))
    if not m:
        return None
    dt = datetime(*(int(g) for g in m.groups()))
    tz = TALLINN or timezone(tallinn_offset(dt))
    return dt.replace(tzinfo=tz).isoformat()


def absolute(url, relative_to):
    """
    events.json urls are written relative to /events/, because that is where the
    calendar renders them. The API is read from anywhere, so they have to be
    absolute: '../portfolio/' -> 'https://ebsic.ee/portfolio/'. normpath drops a
    trailing slash, so it is put back when the original had one.
    """
    if not url:
        return None
    if url.startswith(("http://", "https://")):
        return url
    joined = posixpath.normpath(posixpath.join("/", relative_to, url))
    if url.endswith("/") and not joined.endswith("/"):
        joined += "/"
    return BASE + joined


def round2(n):
    return round(n + 0.0, 2)


# --------------------------------------------------------------------------
# events
# --------------------------------------------------------------------------
def build_events(now):
    src = json.loads((ROOT / "events" / "events.json").read_text())
    out = []

    for ev in src.get("events", []):
        start_iso = to_iso(ev.get("start"))
        if not start_iso:
            continue
        start_dt = datetime.fromisoformat(start_iso)
        end_iso = to_iso(ev.get("end"))
        # No end time means a two-hour slot, the same assumption the pages make.
        end_dt = datetime.fromisoformat(end_iso) if end_iso else start_dt + timedelta(hours=2)

        out.append({
            "id": ev.get("id"),
            "title": ev.get("title"),
            "kind": ev.get("kind") or None,
            "start": start_iso,
            "end": end_iso,
            "endEstimated": not end_iso,
            "timezone": "Europe/Tallinn",
            "location": ev.get("location") or None,
            "blurb": ev.get("blurb") or None,
            "url": absolute(ev.get("url"), "events"),
            "urlLabel": ev.get("urlLabel") or None,
            "dateConfirmed": not ev.get("tbc", False),
            "status": "upcoming" if end_dt >= now else "past",
        })

    out.sort(key=lambda e: e["start"])
    upcoming = [e for e in out if e["status"] == "upcoming"]

    return {
        "$schema": f"{BASE}/api/",
        "endpoint": f"{BASE}/api/events.json",
        "generated": now.isoformat(timespec="seconds"),
        "source": "EBS Investment Club event calendar",
        "timezone": "Europe/Tallinn",
        "counts": {"total": len(out), "upcoming": len(upcoming), "past": len(out) - len(upcoming)},
        "next": upcoming[0]["id"] if upcoming else None,
        "events": out,
    }


# --------------------------------------------------------------------------
# portfolio
# --------------------------------------------------------------------------
def check_positions_match_page(positions):
    """
    portfolio/index.html keeps its own copy of the holdings inline so the page
    renders even if a fetch fails. That copy is the one members see, so if the
    two ever disagree the API would publish figures nobody can see on the site.
    Fail loudly instead.
    """
    page = (ROOT / "portfolio" / "index.html").read_text()
    inline = re.search(r"var POSITIONS = \[(.*?)\n  \];", page, re.S)
    if not inline:
        return ["could not find POSITIONS in portfolio/index.html"]

    found = {}
    for m in re.finditer(
        r'symbol:\s*"([^"]+)",\s*exchange:\s*"([^"]+)",\s*\n?\s*'
        r'qty:\s*([\d.]+),\s*cost:\s*([\d.]+),\s*snapshot:\s*([\d.]+),\s*'
        r'currency:\s*"([^"]+)",\s*costEur:\s*([\d.]+)',
        inline.group(1),
    ):
        sym, exch, qty, cost, snap, cur, cost_eur = m.groups()
        found[f"{sym}:{exch}"] = (float(qty), float(cost), float(snap), cur, float(cost_eur))

    problems = []
    for p in positions:
        k = f"{p['symbol']}:{p['exchange']}"
        mine = (float(p["qty"]), float(p["cost"]), float(p["snapshot"]), p["currency"], float(p["costEur"]))
        if k not in found:
            problems.append(f"{k} is in positions.json but not in portfolio/index.html")
        elif found[k] != mine:
            problems.append(f"{k} differs: page {found[k]} vs positions.json {mine}")
    for k in found:
        if k not in {f"{p['symbol']}:{p['exchange']}" for p in positions}:
            problems.append(f"{k} is in portfolio/index.html but not in positions.json")
    return problems


def build_portfolio(now):
    pos_doc = json.loads((ROOT / "portfolio" / "positions.json").read_text())
    positions = pos_doc["positions"]

    problems = check_positions_match_page(positions)
    if problems:
        print("ERROR: holdings do not match the portfolio page:", file=sys.stderr)
        for pr in problems:
            print(f"  - {pr}", file=sys.stderr)
        sys.exit(1)

    prices_path = ROOT / "portfolio" / "prices.json"
    prices = json.loads(prices_path.read_text()) if prices_path.exists() else {}
    quotes = prices.get("quotes") or {}

    fx = prices.get("fxUsdEur") or pos_doc["snapshotFxUsdEur"]
    fx_live = bool(prices.get("fxUsdEur"))

    holdings, live_count = [], 0
    for p in positions:
        key = f"{p['symbol']}:{p['exchange']}"
        q = quotes.get(key)

        # Frankfurt quotes everything in euros, including the two lines whose
        # home listing is in dollars. Convert back to the position's own
        # currency so "since entry" compares like with like, exactly as the
        # page does.
        price_native, as_of, source = p["snapshot"], None, "broker snapshot"
        if q and isinstance(q.get("price"), (int, float)):
            price_native = q["price"]
            if q.get("currency") == "EUR" and p["currency"] == "USD":
                price_native = q["price"] / fx
            as_of, source = q.get("asOf"), "Boerse Frankfurt"
            live_count += 1

        rate = fx if p["currency"] == "USD" else 1.0
        value_eur = p["qty"] * price_native * rate

        holdings.append({
            "name": p["name"],
            "ticker": p["ticker"],
            "symbol": p["symbol"],
            "exchange": p["exchange"],
            "isin": p["isin"],
            "group": p["group"],
            "quantity": p["qty"],
            "currency": p["currency"],
            "entryPrice": round2(p["cost"]),
            "price": round2(price_native),
            "priceSource": source,
            "priceAsOf": as_of,
            "changeSinceEntryPct": round2((price_native - p["cost"]) / p["cost"] * 100),
            "costEur": round2(p["costEur"]),
            "valueEur": round2(value_eur),
            "profitEur": round2(value_eur - p["costEur"]),
        })

    # Totals add up the rounded line figures, not the raw ones, so the columns
    # visibly sum to the total the way a broker statement does.
    cost = round2(sum(h["costEur"] for h in holdings))
    value = round2(sum(h["valueEur"] for h in holdings))
    profit = round2(sum(h["profitEur"] for h in holdings))

    by_group = {}
    for h in holdings:
        g = by_group.setdefault(h["group"], {"group": h["group"], "valueEur": 0.0, "costEur": 0.0})
        g["valueEur"] += h["valueEur"]
        g["costEur"] += h["costEur"]
    groups = []
    for g in by_group.values():
        groups.append({
            "group": g["group"],
            "valueEur": round2(g["valueEur"]),
            "costEur": round2(g["costEur"]),
            "weightPct": round2(g["valueEur"] / value * 100) if value else 0.0,
        })
    groups.sort(key=lambda g: -g["valueEur"])

    for h in holdings:
        h["weightPct"] = round2(h["valueEur"] / value * 100) if value else 0.0

    stale = live_count < len(positions)
    return {
        "$schema": f"{BASE}/api/",
        "endpoint": f"{BASE}/api/portfolio.json",
        "generated": now.isoformat(timespec="seconds"),
        "baseCurrency": "EUR",
        "prices": {
            "source": prices.get("source") or "broker snapshot only",
            "updated": prices.get("updated"),
            "live": live_count,
            "fallback": len(positions) - live_count,
            "delayMinutes": 15,
            "note": "Exchange prices are delayed by about 15 minutes. Not for trading.",
        },
        "fx": {
            "pair": "USD/EUR",
            "rate": fx,
            "source": "Frankfurter / ECB reference rate" if fx_live else "snapshot rate",
        },
        "totals": {
            "costEur": cost,
            "valueEur": value,
            "profitEur": profit,
            "returnPct": round2(profit / cost * 100) if cost else 0.0,
            "positions": len(holdings),
        },
        "groups": groups,
        "holdings": holdings,
        "complete": not stale,
    }


# --------------------------------------------------------------------------
def main():
    check = "--check" in sys.argv[1:]
    now = datetime.now(timezone.utc).replace(microsecond=0)

    targets = {
        API / "events.json": build_events(now),
        API / "portfolio.json": build_portfolio(now),
    }

    stale = []
    for path, payload in targets.items():
        text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        if check:
            # "generated" always differs, so compare everything else.
            old = json.loads(path.read_text()) if path.exists() else {}
            new = dict(payload)
            old.pop("generated", None)
            new.pop("generated", None)
            if old != new:
                stale.append(path.name)
            continue
        API.mkdir(exist_ok=True)
        path.write_text(text)
        print(f"  wrote {path.relative_to(ROOT)}  ({len(text):,} bytes)")

    if check:
        if stale:
            print("stale: " + ", ".join(stale), file=sys.stderr)
            return 1
        print("  api output is up to date")
        return 0

    ev, pf = targets[API / "events.json"], targets[API / "portfolio.json"]
    print(f"\n  events    {ev['counts']['upcoming']} upcoming of {ev['counts']['total']}")
    print(f"  portfolio {pf['totals']['valueEur']:,.2f} EUR, "
          f"{pf['prices']['live']}/{pf['totals']['positions']} lines priced live")
    return 0


if __name__ == "__main__":
    sys.exit(main())
