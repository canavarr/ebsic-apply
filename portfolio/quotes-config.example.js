/**
 * Live quotes configuration — copy to quotes-config.js and add your key.
 *
 * Without this file the page still works: it shows the broker snapshot values
 * and says so. With it, prices refresh live and value/profit are recomputed.
 *
 * Provider: Twelve Data (https://twelvedata.com) — chosen because it is one of
 * the few free APIs that (a) sends `access-control-allow-origin: *`, so a static
 * page can call it from the browser at all, and (b) carries the European ETF
 * listings this portfolio actually holds.
 *
 * Free tier: 8 requests/minute, 800/day. This page spends 6 requests per
 * refresh (5 instruments + 1 FX rate), so the default 5-minute interval costs
 * ~72/hour. Don't drop refreshMs much below 60000 or you'll hit the per-minute
 * limit and get throttled.
 *
 * The key is visible to anyone who opens the page — that is unavoidable for a
 * browser-side call. Use a free key, not a paid one, and rotate it if abused.
 */
window.IC_QUOTES = {
  provider: "twelvedata",
  apiKey: "YOUR_TWELVE_DATA_KEY",
  refreshMs: 300000,   // 5 minutes
};
