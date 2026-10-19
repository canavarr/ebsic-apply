# EBS Investment Club — club site

Three static pages in the ebsic.ee brand system (Zin Display Cond headings,
Montserrat body, navy/paper bands, pill buttons):

| Page | What it is |
|---|---|
| `index.html` | Club overview — hero, stat counters, teams with their heads, partners |
| `events/` | Calendar of upcoming and past events, with `.ics` download per event |
| `portfolio/` | Holdings, allocation by exposure, and return since entry, with live prices |
| `api/` | Two public JSON endpoints and the page documenting them |

No build step and no dependencies. Serve the folder:

```sh
python3 -m http.server 8000
```

Open it through the server rather than double-clicking the files — the
cross-page view transitions need a same-origin http navigation.

## The API

GitHub Pages serves static files with `Access-Control-Allow-Origin: *`, so a
committed JSON file is a real endpoint any site can read. Two are published:

| Endpoint | Contents |
|---|---|
| `https://ebsic.ee/api/events.json` | The calendar, with absolute urls, ISO timestamps and `upcoming`/`past` status |
| `https://ebsic.ee/api/portfolio.json` | Every holding valued in euros, plus totals, weights and the FX rate used |

Neither is written by hand. Rebuild both after changing an event or a holding:

```sh
python3 api/build-api.py           # rebuild
python3 api/build-api.py --check   # exit 1 if the committed output is stale
```

The holdings live in `portfolio/positions.json`. `portfolio/index.html` keeps
its own inline copy so the page still renders if a fetch fails, and the builder
compares the two and **refuses to build if they disagree** — otherwise the API
could publish figures that appear nowhere on the site.

## How prices actually update

This matters because it surprises people: **Pages has no server**, so nothing
refreshes on its own when someone opens the page. `portfolio/prices.json` is a
file in the repo, and the site shows whatever that file last said. Something has
to fetch new prices and commit them.

There are three ways to make that happen, in descending order of how little you
have to remember:

1. **The scheduled workflow** — `.github/workflows/refresh-prices.yml`. Fetches
   prices every 15 minutes while European markets are open, rebuilds the API and
   commits the result. Nobody has to do anything. **It only works from the
   repository's default branch**, because GitHub runs `schedule:` triggers from
   there and nowhere else, so the file has to be on `main` even though
   everything it touches is on the Pages branch.
2. **On a schedule on your own machine** — the same script under `cron` or
   `launchd`, committing and pushing afterwards. No repository settings needed,
   but it only runs while your machine is awake.
3. **By hand**, which is where things stand until one of the above is set up:

```sh
cd portfolio && python3 refresh-prices.py
cd .. && python3 api/build-api.py
git add portfolio/prices.json api/*.json && git commit -m "Refresh prices" && git push
```

Whichever you choose, the quotes themselves are about **15 minutes delayed**, so
refreshing more often than that returns the same numbers. Genuinely real-time
European exchange data is not available for free: Twelve Data's free tier is
real-time for US listings and end-of-day for European ones, and its real-time
European feed starts at $99/month.

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
