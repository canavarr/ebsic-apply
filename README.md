# EBS Investment Club — club site

Three static pages in the ebsic.ee brand system (Zin Display Cond headings,
Montserrat body, navy/paper bands, pill buttons):

| Page | What it is |
|---|---|
| `index.html` | Club overview — hero, stat counters, teams with their heads, partners |
| `events/` | Calendar of upcoming and past events, with `.ics` download per event |
| `portfolio/` | Holdings, allocation by exposure, and return since entry, with live prices |

No build step and no dependencies. Serve the folder:

```sh
python3 -m http.server 8000
```

Open it through the server rather than double-clicking the files — the
cross-page view transitions need a same-origin http navigation.

## Portfolio prices

Prices come from one of three places, tried in order:

1. **`portfolio/prices.json`** — written by `refresh-prices.py`. Keyless.
2. **Twelve Data** — live in the browser, needs a free key in
   `portfolio/quotes-config.js` (copy `quotes-config.example.js`).
3. **The broker snapshot** baked into the page, used when neither is available.

The FX rate is always fetched from Frankfurter (ECB reference rate), which is
keyless and CORS-enabled.

```sh
cd portfolio && python3 refresh-prices.py
```

No free API serves these European ETF listings directly to a browser — Boerse
Frankfurt returns `403 Invalid CORS request` as soon as an `Origin` header is
present, and Yahoo sends no CORS header at all. That is why the keyless path is
a script writing a file the page reads same-origin, rather than a fetch from the
page itself.

Two lines are quoted in dollars (Alphabet, and the LSE listing of VUAA), so
their euro value depends on the FX rate. The euro cost basis is stored as the
broker records it — fixed at the purchase-date rate — because profit is
`value today − basis at purchase`, not `(price − cost) × qty × today's rate`.

## Still placeholders

These are invented so the layout could be built. Replace before showing anyone:

- Home: the four stat figures, the five partner slots, and the social links
  (the three team heads are real)
- Events: every date marked `TBC` — only the Jo Bhakdi evening is real
- Portfolio: **confirm `DX2X` maps to `XSX6`** (ISIN LU0328475792, Xtrackers
  STOXX Europe 600 1C) before relying on the live price

## Accessibility notes

The allocation chart's palette was validated against the chart surface: worst
adjacent CVD ΔE 9.1 (target ≥8), worst normal-vision ΔE clear of the 15 floor.
Two slots fall under 3:1 contrast, so every segment carries a visible label and
a full table view follows the chart — that relief is what makes those colours
usable, not optional decoration. Gains and losses always carry a sign in the
text, so colour is never the only channel.
