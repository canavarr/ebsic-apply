# EBS Investment Club — apply page

Landing page for the Estonian Business School Investment Club. Applicants read the three teams, then **Apply now** opens the Microsoft Form in a new flow (the form is not embedded).

Live hosting is GitHub Pages at **https://ebsic.ee**.

## Apply link

All **Apply now** buttons use the form URL in [`config.js`](config.js):

`https://forms.cloud.microsoft/e/5nPxMLS6NB`

The form must stay set to **Anyone can respond**.

## Newsletter

Footer **Join** opens the Substack subscribe page for [ebsic.substack.com](https://ebsic.substack.com). The URL is set in [`config.js`](config.js) as `substackUrl`.

Anyone can subscribe on that publication. Subscribers confirm via the email Substack sends them. The club inbox is not notified of each Join.

To point Join at a different publication, change `substackUrl` only.

## Page

- Navy header with the white Investment Club EBS lockup
- Hero: lecture-hall photo, Zin Display headline, “Want to grow your future?”
- Three team cards: Events, Marketing, Portfolio
- Footer: logo, newsletter Join (Substack), and `investeerimisklubi@ebs.ee`
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
- `config.js` — Microsoft Form URL and Substack publication URL
- `app.js` — Apply links and newsletter Join
- `assets/` — logo, mark, hero photo
- `assets/fonts/` — Zin Display Condensed Medium and Montserrat (Medium, SemiBold, Bold)

Hero photo is the club lecture-hall image in `assets/hero.png`.

The original print file `EBS_LOGO_INVESTMENT_CLUB_PLAIN_WHITE_CMYK.eps` stays in the repo for design work. It is not used on the page.
