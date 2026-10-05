# gofflab.github.io

Source for [www.gofflab.org](https://www.gofflab.org), served by GitHub Pages from the repository root.

## Editing content

Content lives in `data/*.yaml`. Edit the YAML, then rebuild.

| File | Controls |
|---|---|
| `data/site.yaml` | Lab name, tagline, menu, footer links, funders, GA4 ID |
| `data/home.yaml` | Homepage sections |
| `data/research.yaml` | Research page (approach, future directions, past themes) |
| `data/cephalopods.yaml` | Cephalopods hub page |
| `data/genome_ochier.yaml` | *O. chierchiae* genome downloads and stats |
| `data/publications.yaml` | PMIDs and bioRxiv IDs (metadata is fetched automatically) |
| `data/people.yaml` | Current members, alumni, rotation students |
| `data/news.yaml` | News items (format notes at the top of the file) |
| `data/tools.yaml` | Software, datasets, code snippets |
| `data/contact.yaml` | Addresses and phone numbers |

To keep an entry off the site without deleting it (a pre-release tool, a person who prefers not
to be listed), add `hidden: true` to it in `data/tools.yaml` (software, datasets, snippets) or
`data/people.yaml`. The build log lists what it hid. The YAML itself is public on GitHub.

Photos go in `images/`; the build makes resized WebP copies in `assets/img/`.
Page-header background images are set under `accents` in `data/site.yaml`. 3D renders on a grey
backdrop, and render movies, need a one-time prep first:
`python scripts/prep_renders.py image|movie SRC NAME` keys the backdrop to black and writes
`images/renders/` (and `assets/video/` for movies); see the script header for options.
Posters dropped into `posters/` are listed automatically.

## Previewing your edits

```bash
pip install -r scripts/requirements.txt   # once
scripts/preview.sh                        # build, serve at http://localhost:8000, open the browser
```

Press Ctrl-C to stop. The preview leaves out Google Analytics; stopping it rebuilds the pages
with analytics, so they are safe to commit.

## Building

```bash
python scripts/main.py                 # fetch PubMed/bioRxiv, render all pages
python scripts/main.py --offline       # render from data/cache only
python scripts/main.py --no-analytics  # local preview without the GA4 tag
python -m http.server                  # then open http://localhost:8000
```

Layout is in `templates/` (Jinja2), styles in `assets/css/site.css`.

The `Rebuild site` GitHub Action re-runs the build weekly, on demand, and whenever
site sources change on `master`, committing the refreshed pages.
