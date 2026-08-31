# EBS Investment Club — apply page

Landing page for the Estonian Business School Investment Club. Applicants read the three teams, then **Apply now** opens the Microsoft Form in a new flow (the form is not embedded).

Live hosting is GitHub Pages at **https://ebsic.ee**.

## Apply link

All **Apply now** buttons use the form URL in [`config.js`](config.js):

`https://forms.cloud.microsoft/e/5nPxMLS6NB`

The form must stay set to **Anyone can respond**.

## Newsletter

**Subscribe** saves the address in a Supabase table. The person stays on the page. The club inbox is not emailed.

### Dashboard (once)

1. Create a free project at [supabase.com](https://supabase.com).
2. Open **SQL Editor** and run:

```sql
create table newsletter_signups (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  created_at timestamptz not null default now()
);

create unique index newsletter_signups_email_lower
  on newsletter_signups (lower(email));

alter table newsletter_signups enable row level security;

create policy "anon can insert"
  on newsletter_signups
  for insert
  to anon
  with check (true);
```

Row Level Security is on. The public `anon` role can **insert** only. There is no `select` policy for `anon`, so visitors cannot read the list.

3. **Project Settings → API**: copy **Project URL** and the **anon public** key into [`config.js`](config.js) as `supabaseUrl` and `supabaseAnonKey`. Do not put the **service role** key on the site.

Until those two values are set, Subscribe shows “Newsletter signup is not configured yet.”

### Export the list

In Supabase: **Table Editor → newsletter_signups → Export → CSV**.

## Event page

[ebsic.ee/jobhakdi](https://ebsic.ee/jobhakdi) is the Jo Bhakdi event landing page (`jobhakdi/index.html`).

**Register now** opens [Fienta tickets](https://fienta.com/ebs-investment-club-jobhakdi) (`eventRegisterUrl` in [`config.js`](config.js)).

**Submit your application** (dinner with Jo Bhakdi) opens the [Pioneerlands RSVP](https://pioneerlands.org/pioneer-academy/dinner) (`eventDinnerUrl`).

## Page

- Navy header with the white Investment Club EBS lockup
- Hero: lecture-hall photo, Zin Display headline, “Want to grow your future?”
- Three team cards: Events, Marketing, Portfolio
- Newsletter band: “Stay ahead, stay informed” and Subscribe (Supabase)
- Footer: logo and `investeerimisklubi@ebs.ee`
- Type: Zin Display Condensed Medium for headlines, Montserrat (Medium / SemiBold / Bold) for body copy

## GitHub Pages

Custom domain: **ebsic.ee** (see `CNAME`).

1. Repo **Settings → Pages**
2. Source: **Deploy from a branch**, folder `/ (root)`
3. Custom domain: `ebsic.ee`
4. After DNS is verified, enable **Enforce HTTPS**

### DNS at Elkdata

`ebsic.ee` is on Elkdata. Keep the existing **MX** records so mail is unchanged. Replace only the website **A** record:

| Type | Name | Value |
| --- | --- | --- |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| AAAA | `@` | `2606:50c0:8000::153` |
| AAAA | `@` | `2606:50c0:8001::153` |
| AAAA | `@` | `2606:50c0:8002::153` |
| AAAA | `@` | `2606:50c0:8003::153` |

Delete the old A record `85.194.202.140`. Leave `www` as a CNAME to `ebsic.ee`.

Preview locally:

```bash
python3 -m http.server 4173
```

## Files

- `index.html` — landing page
- `styles.css` — layout
- `config.js` — Microsoft Form URL and Supabase project URL / anon key
- `app.js` — Apply links, header menu, and newsletter Subscribe
- `jobhakdi/` — Jo Bhakdi event page (`ebsic.ee/jobhakdi`)
- `assets/ebsic-logo.svg` — header and footer lockup
- `assets/icons/` — menu and Join us icons
- `assets/images/hero-image.png` / `hero-mobile.png` — home hero
- `assets/fonts/` — Zin Display Condensed Medium and Montserrat (Medium, SemiBold, Bold)
