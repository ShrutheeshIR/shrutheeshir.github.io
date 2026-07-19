# shrutheeshir.github.io

Personal site, built with [Zola](https://www.getzola.org/).

## Local development

Install Zola (pick one, no root needed for the second):

```
brew install zola   # macOS
snap install zola   # Linux, if snap is available
```

Or grab a prebuilt binary for your platform from
https://github.com/getzola/zola/releases and put it on your `PATH`.

Then:

```
make serve           # regenerates publications.json and starts a live-reload dev server
```

## Adding content

- **Publications**: edit `publications.bib` (standard BibTeX, plus custom fields `pdf`, `code`,
  `video`, `website`, `note`, `preview`, `abbr`, `projects`). `make serve`/`make build` regenerate
  `data/publications.json` automatically via `scripts/bib_to_json.py`.
- **News** (short updates, shown on the homepage): add a new `.md` file under `content/news/`
  with `title` and `date` in the front matter.
- **Blog** (long-form posts): add a new `.md` file under `content/blog/` with `title`, `date`,
  and optionally `description` (used as the excerpt on the blog index) in the front matter.
- **Projects**: add a new folder under `content/projects/<slug>/` with an `index.md` (see existing
  ones for the front-matter shape) and any images alongside it.
- **Bio/experience**: edit `content/bio.md`.

## Deploy

Pushing to `revamped` (or the branch this repo treats as its Pages source) triggers
`.github/workflows/deploy.yml`, which regenerates `publications.json`, runs `zola build`, and
publishes `public/` via GitHub Pages. Make sure the repo's Pages source is set to "GitHub Actions"
under Settings → Pages.
