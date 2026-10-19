#!/usr/bin/env python3
"""
Refresh portfolio prices without any API key.

Why a script instead of fetching from the page: the sources that cover these
European ETF listings refuse browser requests. Boerse Frankfurt returns
"403 Invalid CORS request" the moment an Origin header is present, and Yahoo
sends no Access-Control-Allow-Origin at all. A script has no such limit, so it
fetches the prices and writes prices.json next to index.html, which the page
then reads same-origin.

Sources (both free, neither needs a key):
  - Boerse Frankfurt  — last traded price by ISIN, in EUR
  - Frankfurter       — ECB reference rate for USD/EUR

Usage:
    python3 refresh-prices.py            # fetch once and write prices.json
    python3 refresh-prices.py --watch    # keep refreshing every 60s
    python3 refresh-prices.py --watch 30 # ...every 30s
    python3 refresh-prices.py --dry-run  # print what it would write

Run it before opening the page, or on a schedule:
    */15 9-18 * * 1-5  cd /path/to/portfolio && /usr/bin/python3 refresh-prices.py
"""

import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

BF = "https://api.boerse-frankfurt.de/v1/data/quote_box/single?isin={isin}&mic=XETR"
FX = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR"
OUT = Path(__file__).resolve().parent / "prices.json"

# One entry per instrument. `key` must match symbol:exchange in index.html.
INSTRUMENTS = [
    {"key": "GOOGL:NASDAQ", "isin": "US02079K3059", "name": "Alphabet Inc."},
    {"key": "EXXT:XETR",    "isin": "DE000A0F5UF5", "name": "iShares NASDAQ-100 UCITS ETF"},
    {"key": "VUAA:XETR",    "isin": "IE00BFMXXD54", "name": "Vanguard S&P 500 UCITS ETF"},
    {"key": "VUAA:LSE",     "isin": "IE00BFMXXD54", "name": "Vanguard S&P 500 UCITS ETF"},
    {"key": "XSX6:XETR",    "isin": "LU0328475792", "name": "Xtrackers STOXX Europe 600 1C"},
]

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36")


def get_json(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def once(dry=False):
    """Fetch every instrument plus the FX rate and write prices.json."""
    quotes, errors = {}, []

    for inst in INSTRUMENTS:
        if inst["key"] in quotes:          # same ISIN used by two lines
            continue
        try:
            d = get_json(BF.format(isin=inst["isin"]))
            price = d.get("lastPrice")
            if price is None:
                raise ValueError("no lastPrice in response")
            quotes[inst["key"]] = {
                "price": float(price),
                "currency": "EUR",         # Frankfurt quotes in EUR regardless of home listing
                "changePct": d.get("changeToPrevDayInPercent"),
                "asOf": d.get("timestamp"),
                "isin": inst["isin"],
            }
            print(f"  {inst['key']:14s} {price:>10.2f} EUR   {inst['name']}", flush=True)
        except Exception as e:                      # one bad symbol must not lose the rest
            errors.append(f"{inst['key']}: {e}")
            print(f"  {inst['key']:14s} {'FAILED':>10}   {e}")

    # Both VUAA lines share an ISIN, so copy the quote across.
    for inst in INSTRUMENTS:
        src = next((i for i in INSTRUMENTS if i["isin"] == inst["isin"] and i["key"] in quotes), None)
        if src and inst["key"] not in quotes:
            quotes[inst["key"]] = dict(quotes[src["key"]])

    fx = None
    try:
        fx = float(get_json(FX)["rates"]["EUR"])
        print(f"  {'USD/EUR':14s} {fx:>10.5f}")
    except Exception as e:
        errors.append(f"fx: {e}")
        print(f"  {'USD/EUR':14s} {'FAILED':>10}   {e}")

    payload = {
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "Boerse Frankfurt (prices) + Frankfurter/ECB (FX)",
        "fxUsdEur": fx,
        "quotes": quotes,
        "errors": errors,
    }

    if dry:
        print(json.dumps(payload, indent=2))
        return 0

    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nwrote {OUT}  ({len(quotes)} quotes"
          + (f", {len(errors)} error(s)" if errors else "") + ")", flush=True)
    return 1 if len(quotes) == 0 else 0


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args

    # --watch [seconds]: keep refreshing so the page tracks the feed as it
    # updates. The sources are free and unmetered, so a short interval costs
    # nothing; the underlying quotes are still ~15 minutes delayed.
    if "--watch" in args:
        i = args.index("--watch")
        try:
            every = int(args[i + 1])
        except (IndexError, ValueError):
            every = 60
        print(f"  watching: refreshing every {every}s, ctrl-c to stop\n", flush=True)
        try:
            while True:
                once(dry)
                print(f"  ...sleeping {every}s\n", flush=True)
                time.sleep(every)
        except KeyboardInterrupt:
            print("\n  stopped")
            return 0
    return once(dry)


if __name__ == "__main__":
    sys.exit(main())
