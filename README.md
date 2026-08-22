# EBS Investment Club — apply page

Landing page for the Estonian Business School Investment Club. Applicants read the three teams, then **Apply now** opens the Microsoft Form in a new flow (the form is not embedded).

Live hosting is GitHub Pages from this repository (root of `main`).

## Apply link

All **Apply now** buttons use the form URL in [`config.js`](config.js):

`https://forms.cloud.microsoft/e/5nPxMLS6NB`

The form must stay set to **Anyone can respond**.

## Page

- Navy header with the white Investment Club EBS lockup
- Hero: grayscale hall photo, blue wash, “Want to grow your future?”
- Three team cards: Events, Marketing, Portfolio
- Footer: logo and `investeerimisklubi@ebs.ee`

## GitHub Pages

1. Repo **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main`, folder: `/ (root)`
4. Site URL: `https://canavarr.github.io/ebsic-apply/`

Preview locally:

```bash
python3 -m http.server 4173
```

## Files

- `index.html` — landing page
- `styles.css` — layout
- `config.js` — Microsoft Form URL
- `app.js` — applies that URL to every Apply now link
- `assets/` — logo, mark, hero photo

Hero photo is a grayscale lecture-hall crop. Replace `assets/hero.jpg` with the club photo from the design if you have the original file.

The original print file `EBS_LOGO_INVESTMENT_CLUB_PLAIN_WHITE_CMYK.eps` stays in the repo for design work. It is not used on the page.
