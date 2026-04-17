#!/usr/bin/env python3
"""
FuelEcon · sitemap.xml generator
Produces public/sitemap.xml with proper xhtml:link hreflang alternates.

Run: python3 scripts/build_sitemap.py
"""

from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
SITE_URL = "https://fuelecon.pages.dev"
TODAY = date.today().isoformat()

LOCALES = ["en-us", "en-gb", "en-ca", "en-au"]
DEFAULT = "en-us"

# Pages that exist in every locale (homepage), and legal pages which live at root only (for now)
LOCALIZED_PAGES = [""]  # root path = home calculator
ROOT_ONLY_PAGES = ["about/", "privacy/", "terms/", "disclosure/", "contact/"]


def url_for(locale: str, page: str) -> str:
    prefix = "" if locale == DEFAULT else f"/{locale}"
    return f"{SITE_URL}{prefix}/{page}".rstrip("/") + ("/" if page else "/")


def hreflang_block_for(page: str) -> str:
    """Emit xhtml:link alternates for every locale for the given page."""
    lines = []
    for loc in LOCALES:
        href = url_for(loc, page)
        lines.append(f'    <xhtml:link rel="alternate" hreflang="{loc}" href="{href}"/>')
    lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{url_for(DEFAULT, page)}"/>')
    return "\n".join(lines)


def url_entry(loc: str, page: str, priority: str, changefreq: str, with_alternates: bool) -> str:
    alternates = hreflang_block_for(page) + "\n" if with_alternates else ""
    return f"""  <url>
    <loc>{url_for(loc, page)}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
{alternates}  </url>"""


def build():
    entries = []

    # Localized pages (homepage in every locale)
    for page in LOCALIZED_PAGES:
        for loc in LOCALES:
            priority = "1.0" if loc == DEFAULT else "0.9"
            entries.append(url_entry(loc, page, priority, "weekly", with_alternates=True))

    # Root-only pages (legal — English-US only for now)
    for page in ROOT_ONLY_PAGES:
        entries.append(url_entry(DEFAULT, page, "0.5", "monthly", with_alternates=False))

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
{chr(10).join(entries)}
</urlset>
"""
    (PUBLIC / "sitemap.xml").write_text(xml, encoding="utf-8")
    print(f"✓ built public/sitemap.xml ({len(entries)} URLs)")


if __name__ == "__main__":
    build()
