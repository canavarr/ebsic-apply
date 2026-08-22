# EBS Investment Club — apply page

Public English application page for the Estonian Business School Investment Club. It is a static site: branded landing, three team cards, then a [Microsoft Forms](https://forms.office.com) embed. Responses land in Excel in the club’s Microsoft 365 account.

Live hosting is GitHub Pages from this repository (root of `main`).

## What applicants see

1. Short pitch for the club
2. Events, Marketing, and Portfolio Management team descriptions
3. The membership form (iframe once you paste the embed URL)

## Connect Microsoft Forms

We cannot create the form from this repo. An officer with an EBS Microsoft 365 account does it once per intake.

1. Open [forms.office.com](https://forms.office.com) signed in with your EBS account.
2. **New Form** titled `EBS Investment Club membership application`.
3. Add the questions **in this order** (all required unless marked optional).
4. Theme: dark or black background if available, so it sits better on this page.
5. **Collect responses**
   - Who can fill out this form: **Anyone can respond**  
     If you leave this as “Only people in my organization”, non-EBS emails and some browsers will hit a Microsoft login wall.
   - Turn off “Record name” unless you specifically want Microsoft accounts attached.
6. **Embed** (`<>`). Copy the `src` URL from the iframe snippet. It looks like:

   `https://forms.office.com/Pages/ResponsePage.aspx?id=...&embed=true`

7. Paste that URL into [`config.js`](config.js) as `formEmbedUrl`.
8. Commit and push. GitHub Pages will pick it up after the next deploy.
9. Optional: **Open in Excel** / **Responses** in Forms, or a Power Automate flow that emails the board on each submit.

If `formEmbedUrl` is empty, the page shows a placeholder and the question list instead of the iframe.

### Questions to recreate

**Details**

| # | Question | Type | Required |
|---|----------|------|----------|
| 1 | Full name | Text | Yes |
| 2 | Study group | Text | Yes |
| 3 | Email | Text, email validation if available | Yes |
| 4 | Phone | Text | Yes |
| 5 | Programme and year | Choice: `BA` / `MA` / `Other`, plus a text field **Year of study** (or one text field such as `BA, year 2`) | Yes |
| 6 | LinkedIn | Text (URL) | No |
| 7 | How did you hear about the club? | Text | Yes |
| 8 | Investing experience | Choice: `None` / `Beginner` / `Some` / `Active` | Yes |

**Team preferences** — same three options on both questions. A second preference may match the first if they only want one team (Forms cannot easily block duplicates).

| # | Question | Type | Options |
|---|----------|------|---------|
| 9 | My preferred team no. 1 | Choice | Events team · Marketing Team · Portfolio Management Team |
| 10 | My preferred team no. 2 | Choice | Events team · Marketing Team · Portfolio Management Team |

**Written answers** — long text

| # | Question |
|---|----------|
| 11 | Please briefly introduce yourself and explain why you think you would be a good fit for the team(s) you selected. |
| 12 | Why do I want to be part of the EBS Investment Club? |
| 13 | What skillset will I bring to the team? |

**Consent**

| # | Question | Type |
|---|----------|------|
| 14 | I consent to the EBS Investment Club contacting me about membership. | Choice: `Yes` / `No` — required, and only **Yes** should be accepted (use branching: if No, show a message and do not continue) |

Do not add a separate “Motivation” field. Question 12 is the motivation question.

### Iframe height

Long forms need a tall embed. Adjust `formHeight` in `config.js` (pixels) if applicants have to scroll inside a clipped frame. Default is `2800`.

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

- `index.html` — page structure
- `styles.css` — dark club layout
- `config.js` — form URL only; safe to edit each semester
- `app.js` — injects the iframe when a URL is set
- `assets/` — white lockup and EBS mark (from the original EPS)

The original print file `EBS_LOGO_INVESTMENT_CLUB_PLAIN_WHITE_CMYK.eps` stays in the repo for design work. It is not used on the page.

## Later options

If the Microsoft widget looks too generic, keep this page chrome and replace the iframe with a custom HTML form (Formspree, FormSubmit, or a Power Automate webhook into Excel). Team copy and questions stay the same.
