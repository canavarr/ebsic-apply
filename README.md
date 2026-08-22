# EBS Investment Club — apply page

Public English application page for the Estonian Business School Investment Club. Static site: branded landing, three team cards, then a custom membership form that matches the page (not Microsoft Forms).

Applications are emailed to the club through [FormSubmit](https://formsubmit.co). Live hosting is GitHub Pages from this repository (root of `main`).

## What applicants see

1. Short pitch for the club
2. Events, Marketing, and Portfolio Management team descriptions
3. The membership form, styled like the rest of the page

## Where submissions go

Edit [`config.js`](config.js) and set `submitEmail` to the inbox that should receive applications. It currently uses `investeerimisklubi@ebs.ee`.

The **first** submission to a new address sends a confirmation mail from FormSubmit. Open that mail once. After that, applications arrive as emails.

Microsoft Forms cannot be restyled (it is an iframe). That is why this page uses a custom form instead of the embed.

## Application questions

**Details** — full name, study group, email, phone, programme (BA / MA / Other), year of study, LinkedIn (optional), how they heard about the club, investing experience (none / beginner / some / active).

**Team preferences** — preferred team 1 and 2: Events team, Marketing Team, Portfolio Management Team. The second choice may match the first.

**Written answers**

- Please briefly introduce yourself and explain why you think you would be a good fit for the team(s) you selected.
- Why do I want to be part of the EBS Investment Club?
- What skillset will I bring to the team?

**Consent** — must choose Yes to submit.

## GitHub Pages

1. Repo **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main`, folder: `/ (root)`
4. Save. The site URL will be `https://canavarr.github.io/ebsic-apply/`

Preview locally:

```bash
python3 -m http.server 4173
```

Then open `http://localhost:4173`.

## Files

- `index.html` — page and form fields
- `styles.css` — dark club layout
- `config.js` — destination email
- `app.js` — sends the application
- `assets/` — white lockup and EBS mark (from the original EPS)

The original print file `EBS_LOGO_INVESTMENT_CLUB_PLAIN_WHITE_CMYK.eps` stays in the repo for design work. It is not used on the page.
