#!/usr/bin/env python
"""Build the Goff Lab website.

Content lives in data/*.yaml, layout in templates/, styles in assets/css/site.css.
Rendered pages are written to the repository root (served by GitHub Pages).

    python scripts/main.py                 # fetch PubMed/bioRxiv, then render
    python scripts/main.py --offline       # render from data/cache only
    python scripts/main.py --no-analytics  # omit the GA4 tag (local previews)
"""
import argparse
import datetime
import difflib
import json
import re
import sys
import urllib.request
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
CACHE = DATA / 'cache'
IMAGES = ROOT / 'images'
WEB_IMG = ROOT / 'assets' / 'img'

ENTREZ_EMAIL = 'loyalgoff@gmail.com'

# (template, output path, page title). Output paths are relative to the repo root.
PAGES = [
    ('index.html', 'index.html', None),
    ('research.html', 'research.html', 'Research'),
    ('cephalopods.html', 'cephalopods.html', 'Cephalopods'),
    ('octopus_genome.html', 'octopus_genome.html', 'Octopus chierchiae genome assembly'),
    ('publications.html', 'publications.html', 'Publications'),
    ('tools.html', 'tools.html', 'Tools & Data'),
    ('people.html', 'people.html', 'People'),
    ('join.html', 'join.html', 'Join'),
    ('contact.html', 'contact.html', 'Contact'),
    ('teaching.html', 'teaching.html', 'Teaching'),
    ('posters.html', 'posters/index.html', 'Posters'),
]

# Old URLs kept alive as redirects so external links and bookmarks still work.
REDIRECTS = {
    'preprints.html': 'publications.html#preprints',
    'software.html': 'tools.html#software',
    'datasets.html': 'tools.html#datasets',
    'lab_resources.html': 'tools.html#snippets',
    'octopus.html': 'octopus_genome.html',  # cephalopods.html while the genome is unlisted
}


def load_yaml(name):
    with open(DATA / f'{name}.yaml') as fh:
        return yaml.safe_load(fh)


def log(msg):
    print(msg, file=sys.stderr)


##########################
# Publications
##########################

def read_cache(name):
    path = CACHE / f'{name}.json'
    return json.loads(path.read_text()) if path.exists() else {}


def write_cache(name, records):
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / f'{name}.json').write_text(json.dumps(records, indent=1, ensure_ascii=False) + '\n')


def fetch_pubmed(pmids, cache):
    """Refresh cached PubMed records. Keeps the cached copy for anything that fails."""
    from Bio import Entrez, Medline
    Entrez.email = ENTREZ_EMAIL
    log(f'Fetching {len(pmids)} records from PubMed...')
    try:
        handle = Entrez.efetch(db='pubmed', id=pmids, rettype='medline', retmode='text')
        records = list(Medline.parse(handle))
    except Exception as err:  # network or API failure: fall back to cache
        log(f'\tPubMed fetch failed ({err}); using cached records')
        return cache
    for rec in records:
        if 'PMID' not in rec:
            continue
        doi = next((a.split(' ')[0] for a in rec.get('AID', []) if a.endswith('[doi]')), None)
        if not doi and '[doi]' in rec.get('LID', ''):
            doi = rec['LID'].split(' [doi]')[0].split(' [pii] ')[-1]
        cache[rec['PMID']] = dict(
            pmid=rec['PMID'], title=rec.get('TI', '').strip(), year=int(rec.get('DP', '0')[:4]),
            authors=rec.get('AU', []), journal=rec.get('SO', '').strip(), doi=doi,
            abstract=rec.get('AB', ''))
    log(f'\t{len(records)} records')
    return cache


def fetch_biorxiv(ids, cache):
    log(f'Fetching {len(ids)} preprints from bioRxiv...')
    ok = 0
    for pid in ids:
        doi = f'10.1101/{pid}'
        try:
            with urllib.request.urlopen(f'https://api.biorxiv.org/details/biorxiv/{doi}', timeout=30) as resp:
                versions = json.loads(resp.read())['collection']
        except Exception as err:
            log(f'\t{doi}: fetch failed ({err}); using cache')
            continue
        if not versions:
            continue
        first, latest = versions[0], versions[-1]
        published = latest.get('published')
        cache[doi] = dict(
            doi=doi, title=latest['title'].strip(), year=int(first['date'][:4]), date=first['date'],
            authors=[a.strip() for a in latest['authors'].split(';') if a.strip()],
            server=latest.get('server', 'biorxiv'), abstract=latest.get('abstract', ''),
            published_doi=None if published in (None, '', 'NA') else published)
        ok += 1
    log(f'\t{ok} refreshed')
    return cache


def _norm_title(t):
    return re.sub(r'[^a-z0-9 ]', '', t.lower())


def publications(offline):
    cfg = load_yaml('publications')
    pmids = [str(p['pmid']) for p in cfg['papers']]
    pre_ids = [str(p['id']) for p in cfg['preprints']]

    pub_cache, pre_cache = read_cache('pubmed'), read_cache('biorxiv')
    if not offline:
        pub_cache = fetch_pubmed(pmids, pub_cache)
        pre_cache = fetch_biorxiv(pre_ids, pre_cache)
        write_cache('pubmed', pub_cache)
        write_cache('biorxiv', pre_cache)

    themes = {str(p['pmid']): p.get('themes', []) for p in cfg['papers']}
    papers = []
    for pmid in pmids:
        if pmid not in pub_cache:
            log(f'WARNING: no record for PMID {pmid} (run without --offline)')
            continue
        papers.append(dict(pub_cache[pmid], themes=themes[pmid]))
    papers.sort(key=lambda p: (p['year'], int(p['pmid'])), reverse=True)

    # Flag preprints that now have a published version on the papers list.
    by_doi = {p['doi'].lower(): p for p in papers if p['doi']}
    titles = {_norm_title(p['title']): p for p in papers}
    preprints = []
    for pid in pre_ids:
        doi = f'10.1101/{pid}'
        if doi not in pre_cache:
            log(f'WARNING: no record for preprint {doi} (run without --offline)')
            continue
        pre = dict(pre_cache[doi])
        match = by_doi.get((pre.get('published_doi') or '').lower()) if pre.get('published_doi') else None
        if not match:
            close = difflib.get_close_matches(_norm_title(pre['title']), titles, n=1, cutoff=0.85)
            match = titles[close[0]] if close else None
        pre['published'] = match
        preprints.append(pre)
    preprints.sort(key=lambda p: (p['year'], p.get('date') or ''), reverse=True)
    return papers, preprints


##########################
# Images
##########################

USED_IMAGES = set()


def web_image(src, width):
    """Return a resized WebP copy of images/<src> (generated once, then committed)."""
    source = IMAGES / src
    stem = src.rsplit('.', 1)[0].replace('/', '__')
    out = WEB_IMG / f'{stem}-{width}.webp'
    USED_IMAGES.add(out.name)
    if not out.exists():
        WEB_IMG.mkdir(parents=True, exist_ok=True)
        with Image.open(source) as im:
            im = ImageOps.exif_transpose(im)
            im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
            if im.width > width:
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            im.save(out, 'WEBP', quality=82, method=6)
    with Image.open(out) as im:
        w, h = im.size
    return dict(path=f'assets/img/{out.name}', w=w, h=h)


def site_icons(logo_src):
    """Favicons and a link-preview image from the lab logo (regenerated only if missing)."""
    icons = ROOT / 'assets' / 'icons'
    icons.mkdir(parents=True, exist_ok=True)
    bg = (5, 7, 10, 255)  # --bg in site.css
    with Image.open(IMAGES / logo_src) as logo:
        logo = logo.convert('RGBA')
        for name, size, pad, opaque in [('favicon-32.png', 32, 0, False), ('favicon-192.png', 192, 8, False),
                                        ('apple-touch-icon.png', 180, 18, True)]:
            out = icons / name
            if out.exists():
                continue
            canvas = Image.new('RGBA', (size, size), bg if opaque else (0, 0, 0, 0))
            mark = logo.resize((size - 2 * pad, size - 2 * pad), Image.LANCZOS)
            canvas.alpha_composite(mark, (pad, pad))
            canvas.save(out, optimize=True)
        out = icons / 'social-card.png'
        if not out.exists():
            canvas = Image.new('RGBA', (1200, 630), bg)
            mark = logo.resize((540, 540), Image.LANCZOS)
            canvas.alpha_composite(mark, (330, 45))
            canvas.convert('RGB').save(out, optimize=True)


##########################
# Posters
##########################

def posters():
    items = []
    for pdf in sorted((ROOT / 'posters').glob('*.pdf')):
        name = pdf.stem
        year = None
        m = re.match(r'^(20\d{2})\d{4}_', name) or re.match(r'^(\d{2})\d{4}_', name)
        if m:
            year = int(m.group(1)) if len(m.group(1)) == 4 else 2000 + int(m.group(1))
            name = name.split('_', 1)[1]
        else:
            m = re.search(r'(20\d{2})', name)
            year = int(m.group(1)) if m else None
        label = re.sub(r'[_]+', ' ', name).strip()
        items.append(dict(file=pdf.name, label=label, year=year,
                          size=f'{pdf.stat().st_size / 1e6:.1f} MB'))
    items.sort(key=lambda p: (p['year'] or 0, p['label']), reverse=True)
    return items


##########################
# Filters
##########################

GOFF = re.compile(r'^(Goff,? ?L\.? ?A?\.?|Loyal A?\.? ?Goff)$')


def author_list(authors):
    out = []
    for a in authors:
        a = a.strip()
        out.append(f'<strong class="self">{a}</strong>' if GOFF.match(a) else a)
    return ', '.join(out)


BIORXIV = re.compile(r'\bbiorxiv\b', re.I)
BIORXIV_MARK = ('<span class="biorxiv"><span aria-hidden="true">bio<span class="bx-r">R</span>'
                '<i class="bx-chi">&chi;</i>iv</span><span class="visually-hidden">bioRxiv</span></span>')


def biorxiv_mark(text):
    """Render 'bioRxiv' as its wordmark (red R, italic chi), as on the previous site."""
    return BIORXIV.sub(BIORXIV_MARK, text or '')


def render(env, template, out, **ctx):
    target = ROOT / out
    target.parent.mkdir(parents=True, exist_ok=True)
    html = env.get_template(template).render(**ctx)
    html = re.sub(r'\n\s*\n+', '\n', html)
    target.write_text(html)
    return html.count('class="draft"')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--offline', action='store_true', help='skip PubMed/bioRxiv fetch; use data/cache')
    ap.add_argument('--no-analytics', action='store_true', help='omit the Google Analytics tag')
    args = ap.parse_args()

    site = load_yaml('site')
    if args.no_analytics:
        site['ga4_id'] = None
    papers, preprints = publications(args.offline)
    site_icons(site['logo']['src'])

    env = Environment(loader=FileSystemLoader(ROOT / 'templates'), trim_blocks=True, lstrip_blocks=True)
    env.filters['authors'] = author_list
    env.filters['biorxiv'] = biorxiv_mark
    env.globals['webimg'] = web_image
    env.tests['contains'] = lambda seq, item: item in (seq or [])

    common = dict(
        site=site, year=datetime.date.today().year,
        home=load_yaml('home'), research=load_yaml('research'), cephalopods=load_yaml('cephalopods'),
        people=load_yaml('people'), tools=load_yaml('tools'), contact=load_yaml('contact'),
        genome=load_yaml('genome_ochier'), papers=papers, preprints=preprints, posters=posters())

    drafts = 0
    for template, out, title in PAGES:
        depth = out.count('/')
        drafts += render(env, template, out, page=out, title=title, root='../' * depth, **common)
    for old, new in REDIRECTS.items():
        if new == 'octopus_genome.html' and common['genome'].get('unlisted'):
            new = 'cephalopods.html'
        render(env, '_redirect.html', old, target=new, root='', **common)

    for stale in WEB_IMG.glob('*.webp'):
        if stale.name not in USED_IMAGES:
            stale.unlink()

    log(f'Rendered {len(PAGES)} pages, {len(REDIRECTS)} redirects; '
        f'{len(papers)} papers, {len(preprints)} preprints, {len(common["posters"])} posters.')
    if drafts:
        log(f'NOTE: {drafts} DRAFT placeholders remain (data/*.yaml "draft" keys).')


if __name__ == '__main__':
    main()
