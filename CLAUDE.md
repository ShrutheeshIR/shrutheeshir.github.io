# shrutheeshir.github.io

Personal site for Shrutheesh Raman Iyer, built with [Zola](https://www.getzola.org/) (single Rust
binary static site generator, Tera templates). This replaced a much heavier Hugo/Wowchemy setup
(still on the `hugo` branch, kept for reference/history only — don't edit it). All work happens on
the `revamped` branch. `zola` binary lives at `~/.local/bin/zola` if not on PATH.

## Directory map

- `content/` — Markdown + TOML front matter, one folder per section:
  - `_index.md` — homepage (hero, intro, featured pubs, news, build-note), template `index.html`
  - `bio.md` — single page, template `bio.html`, structured data (education/experience/skills) lives
    in its own `[extra]` TOML front matter, not in the CSS or templates
  - `publications/_index.md` — **no per-publication files**. Publications live in
    `publications.bib` at repo root, see below
  - `projects/<slug>/index.md` — one page bundle per project (images sit alongside `index.md`),
    template `project_single.html`; list template `project_list.html`
  - `news/<slug>.md` — **short** updates (a sentence or two), shown on homepage + `/news/`.
    Template `news_list.html` / `news_single.html`
  - `blog/<slug>.md` — **long-form** posts. Template `blog_list.html` / `blog_single.html`.
    Empty as of this writing — add files here when there's actual long-form content
- `templates/` — Tera templates, one per page type (see mapping above), `macros.html` for shared
  bits (social icons, author-list bolding), `base.html` is the shell (nav/footer/favicon)
- `static/css/style.css` — the *only* stylesheet, plain CSS (no Sass/build step), CSS custom
  properties for theming, mobile breakpoint at `max-width: 640px`
- `static/images`, `static/papers`, `static/publications_preview`, `static/uploads/CV.pdf` — assets
- `scripts/bib_to_json.py` — stdlib-only Python, parses `publications.bib` → `data/publications.json`
- `.github/workflows/deploy.yml` — CI: runs `bib_to_json.py`, `zola build`, deploys to GitHub Pages
  (requires repo Settings → Pages → source = "GitHub Actions", not yet flipped as of this writing)

## How to add things (no need to re-explore the repo for these)

- **New publication**: edit `publications.bib` only (BibTeX + custom fields `pdf`, `code`, `video`,
  `website`, `note`, `preview`, `abbr`, `projects`; `@string{}` macros used for venue names). Run
  `make pubs` (or `make serve`/`make build`, which do it automatically) to regenerate
  `data/publications.json`. The homepage shows the 3 most recent automatically (already sorted by
  year desc in the JSON) — no template change needed for a new entry.
- **New news item** (short): new file in `content/news/`, front matter `title` + `date`, body is
  1-2 sentences. Shows up on homepage (top 5) and `/news/` automatically.
- **New blog post** (long-form): new file in `content/blog/`, front matter `title` + `date` +
  optional `description` (used as excerpt on `/blog/`).
- **New project**: new folder `content/projects/<slug>/` with `index.md`. Copy the front-matter
  shape from an existing one (e.g. `content/projects/home-robot/index.md`) — needs `title`,
  `description`, `weight` (controls order, lower = earlier), `template = "project_single.html"`,
  `[taxonomies] tags = [...]`, `[extra] location`, optionally `image` (filename colocated in the
  same folder) and `external_link`.
- **New top-level page/nav item**: add the `<li>` in `templates/base.html` nav, create the content
  file + a template if it needs bespoke layout (or reuse `page.html` for a plain prose page).

## Design system

- CSS custom properties in `static/css/style.css` `:root` (+ a `prefers-color-scheme: dark`
  override block): `--bg`, `--bg-alt`, `--text`, `--text-muted`, `--accent` (gold, primary —
  publications/links/branding), `--accent-2` (green, secondary — project tags), `--border`.
- Colors were deliberately chosen: gold = "between bright yellow and Purdue's Old Gold" (user's
  request), green = secondary accent (user likes green). Don't drift these without asking — they're
  personal, not arbitrary.
- No JS framework, no webfonts (system font stack), no build step for CSS. Mobile nav uses a
  checkbox-hack hamburger (`.nav-toggle`), not JS.
- Theme follows OS `prefers-color-scheme` by default, but there's a manual toggle button
  (`#theme-toggle` in `base.html` nav) that sets `data-theme="light"/"dark"` on `<html>` and
  persists the choice in `localStorage`; CSS has `:root[data-theme="light"|"dark"]` override
  blocks in `static/css/style.css` that win over the media query. The head has a small blocking
  inline script that applies the stored/preferred theme before first paint (avoids a flash).
- Favicon is `static/favicon.svg` — gold rounded square + 🤖 emoji, linked from `base.html`.

## Known non-obvious decisions

- Publications are intentionally **not** individual Markdown pages — the whole point (per explicit
  user request) is that editing `publications.bib` is the only thing needed to update the site,
  matching how academics already maintain a BibTeX file. Don't reintroduce per-pub content files.
- News vs. Blog is a deliberate split (user request): News = short updates surfaced on the
  homepage, Blog = long-form, not shown on homepage, currently empty.
- `docs/` at repo root is leftover root-owned build output from the old Hugo Docker pipeline;
  it's untracked and can't be deleted without sudo. Harmless, ignore it.

## Local dev

```
make serve   # regenerates publications.json, starts zola serve with live reload
make build   # regenerates publications.json, zola build into public/
```
