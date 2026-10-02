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

Photos go in `images/`; the build makes resized WebP copies in `assets/img/`.
Posters dropped into `posters/` are listed automatically.

## Building

```bash
pip install -r scripts/requirements.txt
python scripts/main.py                 # fetch PubMed/bioRxiv, render all pages
python scripts/main.py --offline       # render from data/cache only
python scripts/main.py --no-analytics  # local preview without the GA4 tag
python -m http.server                  # then open http://localhost:8000
```

Layout is in `templates/` (Jinja2), styles in `assets/css/site.css`.

The `Rebuild site` GitHub Action re-runs the build weekly, on demand, and whenever
site sources change on `master`, committing the refreshed pages.
