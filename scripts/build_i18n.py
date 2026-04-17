#!/usr/bin/env python3
"""
FuelEcon · i18n build script with FULL GEO/AEO/SEO implementation
"""

import json
import re
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent.parent
I18N_DIR = ROOT / "i18n"
PUBLIC = ROOT / "public"
SITE_URL = "https://fuelecon.pages.dev"

DEFAULT_LOCALE = "en-us"
CANONICAL_MODE = "us-consolidated"

# GEO configuration
GEO_REGIONS = {
    "en-us": {"code": "US", "name": "United States", "lat": "37.0902", "lon": "-95.7129"},
    "en-ca": {"code": "CA", "name": "Canada", "lat": "56.1304", "lon": "-106.3468"},
    "en-gb": {"code": "GB", "name": "United Kingdom", "lat": "55.3781", "lon": "-3.4360"},
    "en-au": {"code": "AU", "name": "Australia", "lat": "-25.2744", "lon": "133.7751"}
}

# Currency configuration
CURRENCY_CONFIG = {
    "en-us": {"symbol": "$", "code": "USD", "position": "before"},
    "en-ca": {"symbol": "CA$", "code": "CAD", "position": "before"},
    "en-gb": {"symbol": "£", "code": "GBP", "position": "before"},
    "en-au": {"symbol": "A$", "code": "AUD", "position": "before"}
}

# Unit configurations per region
UNITS_CONFIG = {
    "en-us": {"fuel": "MPG (US)", "distance": "miles", "volume": "gallons (US)"},
    "en-ca": {"fuel": "MPG (US)", "distance": "kilometers", "volume": "liters"},
    "en-gb": {"fuel": "MPG (Imp)", "distance": "miles", "volume": "gallons (Imp)"},
    "en-au": {"fuel": "L/100km", "distance": "kilometers", "volume": "liters"}
}

# Open Graph locales
OG_LOCALES = {
    "en-us": "en_US",
    "en-ca": "en_CA", 
    "en-gb": "en_GB",
    "en-au": "en_AU"
}

def deep_merge(base: dict, override: dict) -> dict:
    out = deepcopy(base)
    for key, val in override.items():
        if key in out and isinstance(out[key], dict) and isinstance(val, dict):
            out[key] = deep_merge(out[key], val)
        else:
            out[key] = val
    return out

def load_locales() -> dict:
    en_us_path = I18N_DIR / f"{DEFAULT_LOCALE}.json"
    master = json.loads(en_us_path.read_text(encoding="utf-8"))
    
    locales = {DEFAULT_LOCALE: master}
    for p in sorted(I18N_DIR.glob("*.json")):
        if p.name.startswith("._") or p.name.startswith(".DS_Store"):
            continue
        slug = p.stem
        if slug == DEFAULT_LOCALE:
            continue
        try:
            delta = json.loads(p.read_text(encoding="utf-8"))
            locales[slug] = deep_merge(master, delta)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"⚠️ Skipping {p.name}: {e}")
            continue
    return locales

def build_hreflang_block(all_locales: list[str]) -> str:
    lines = []
    for slug in all_locales:
        href = SITE_URL + "/" if slug == DEFAULT_LOCALE else f"{SITE_URL}/{slug}/"
        lines.append(f'  <link rel="alternate" hreflang="{slug}" href="{href}" />')
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{SITE_URL}/" />')
    return "\n".join(lines)

def canonical_for(slug: str) -> str:
    if CANONICAL_MODE == "us-consolidated":
        return f"{SITE_URL}/"
    return SITE_URL + "/" if slug == DEFAULT_LOCALE else f"{SITE_URL}/{slug}/"

def build_schema_org(slug: str, locale_data: dict) -> str:
    """Generate Schema.org JSON-LD for AEO"""
    geo = GEO_REGIONS.get(slug, GEO_REGIONS["en-us"])
    currency = CURRENCY_CONFIG.get(slug, CURRENCY_CONFIG["en-us"])
    units = UNITS_CONFIG.get(slug, UNITS_CONFIG["en-us"])
    
    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "FuelEcon",
        "alternateName": "Fuel Economy Calculator",
        "url": SITE_URL if slug == DEFAULT_LOCALE else f"{SITE_URL}/{slug}/",
        "inLanguage": slug,
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{SITE_URL}/?q={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    }
    
    # Add geo-specific organization data
    org_schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": f"FuelEcon {geo['name']}",
        "url": SITE_URL if slug == DEFAULT_LOCALE else f"{SITE_URL}/{slug}/",
        "address": {
            "@type": "PostalAddress",
            "addressCountry": geo['code']
        },
        "currenciesAccepted": currency['code'],
        "paymentAccepted": "Credit Card, Debit Card, PayPal"
    }
    
    return f"""<script type="application/ld+json">
{json.dumps(schema, indent=2)}
</script>
<script type="application/ld+json">
{json.dumps(org_schema, indent=2)}
</script>"""

def build_lang_switcher_html(current_slug: str, all_locales: list[dict]) -> str:
    options = []
    for loc in all_locales:
        slug = loc["_meta"]["locale"]
        display = loc["_meta"]["locale_display"]
        selected = ' selected' if slug == current_slug else ''
        path = "/" if slug == DEFAULT_LOCALE else f"/{slug}/"
        options.append(f'      <option value="{path}"{selected}>{display}</option>')
    options_html = "\n".join(options)
    return f"""<div class="lang-switcher" aria-label="Language and region">
    <label for="langSelect" style="display:none;">Language</label>
    <select id="langSelect" onchange="window.location.href=this.value" aria-label="Switch language">
{options_html}
    </select>
  </div>"""

def transform_root_index(html: str, master: dict, all_slugs: list[str], all_locales_data: list[dict]) -> str:
    hreflang_block = build_hreflang_block(all_slugs)
    canonical = canonical_for(DEFAULT_LOCALE)
    switcher = build_lang_switcher_html(DEFAULT_LOCALE, all_locales_data)
    
    html = re.sub(r'<html lang="[^"]*">', f'<html lang="{DEFAULT_LOCALE}">', html)
    html = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{canonical}">', html)
    html = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*" />', '', html)
    html = re.sub(r'\s*<!-- HREFLANG_BLOCK -->', '', html)
    
    # Add GEO meta tags for root
    geo = GEO_REGIONS[DEFAULT_LOCALE]
    geo_tags = f'    <meta name="geo.region" content="{geo["code"]}" />\n    <meta name="geo.placename" content="{geo["name"]}" />\n    <meta name="geo.position" content="{geo["lat"]};{geo["lon"]}" />\n    <meta name="ICBM" content="{geo["lat"]}, {geo["lon"]}" />'
    
    html = html.replace("</head>", f"  <!-- HREFLANG_BLOCK -->\n{hreflang_block}\n    {geo_tags}\n</head>", 1)
    
    # Add Schema.org
    schema = build_schema_org(DEFAULT_LOCALE, master)
    html = html.replace("</head>", f"{schema}\n</head>", 1)
    
    if 'class="lang-switcher"' not in html:
        html = re.sub(r'(<div class="premium-badge")', f'{switcher}\n    \\1', html, count=1)
    
    return html

def transform_variant_index(root_html: str, locale: dict, all_slugs: list[str], all_locales_data: list[dict]) -> str:
    slug = locale["_meta"]["locale"]
    meta = locale["_meta"]
    home = locale.get("home", {})
    footer = locale.get("footer", {})
    
    html = root_html
    
    # Meta tags
    meta_title = home.get("meta_title", "")
    meta_desc = home.get("meta_description", "")
    if meta_title:
        html = re.sub(r"<title>[^<]*</title>", f"<title>{meta_title}</title>", html, count=1)
        html = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{meta_title}">', html)
    
    if meta_desc:
        html = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{meta_desc}">', html)
        html = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{meta_desc}">', html)
    
    # Canonical + hreflang
    canonical = canonical_for(slug)
    html = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{canonical}">', html)
    html = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*" />', '', html)
    html = re.sub(r'\s*<!-- HREFLANG_BLOCK -->', '', html)
    
    hreflang_block = build_hreflang_block(all_slugs)
    
    # GEO meta tags
    geo = GEO_REGIONS.get(slug, GEO_REGIONS["en-us"])
    geo_tags = f'    <meta name="geo.region" content="{geo["code"]}" />\n    <meta name="geo.placename" content="{geo["name"]}" />\n    <meta name="geo.position" content="{geo["lat"]};{geo["lon"]}" />\n    <meta name="ICBM" content="{geo["lat"]}, {geo["lon"]}" />'
    
    # Open Graph locale
    og_locale = OG_LOCALES.get(slug, "en_US")
    html = re.sub(r'<meta property="og:locale" content="[^"]*">', f'<meta property="og:locale" content="{og_locale}">', html)
    
    # Currency meta tags
    currency = CURRENCY_CONFIG.get(slug, CURRENCY_CONFIG["en-us"])
    html = re.sub(r'<meta property="product:price:currency" content="[^"]*">', f'<meta property="product:price:currency" content="{currency["code"]}">', html)
    
    # Insert all meta tags
    html = html.replace("</head>", f"  <!-- HREFLANG_BLOCK -->\n{hreflang_block}\n    {geo_tags}\n</head>", 1)
    
    # Add Schema.org for variant
    schema = build_schema_org(slug, locale)
    html = html.replace("</head>", f"{schema}\n</head>", 1)
    
    # Language switcher
    switcher_new = build_lang_switcher_html(slug, all_locales_data)
    html = re.sub(r'<div class="lang-switcher".*?</div>\s*(?=<div class="premium-badge")', switcher_new + "\n    ", html, flags=re.DOTALL)
    
    # Unit conversion labels
    units = UNITS_CONFIG.get(slug, UNITS_CONFIG["en-us"])
    html = html.replace("MPG", units["fuel"])
    html = html.replace("miles", units["distance"])
    html = html.replace("gallons", units["volume"])
    
    # Currency symbol replacement
    if currency["symbol"] != "$":
        html = html.replace("$", currency["symbol"])
    
    return html

LANG_SWITCHER_CSS = """
.lang-switcher {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.lang-switcher select {
  padding: 8px 30px 8px 14px;
  border-radius: 100px;
  border: 1.5px solid #ddd;
  background: white url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%231A5F3F' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><polyline points='6 9 12 15 18 9'></polyline></svg>") no-repeat right 12px center;
  appearance: none;
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}
"""

def ensure_css_block_present(html: str) -> str:
    if ".lang-switcher {" in html:
        return html
    return html.replace("</style>", f"{LANG_SWITCHER_CSS}\n</style>", 1)

def build():
    locales = load_locales()
    all_slugs = list(locales.keys())
    all_locales_data = list(locales.values())
    
    root_index_path = PUBLIC / "index.html"
    root_html = root_index_path.read_text(encoding="utf-8")
    
    root_html = ensure_css_block_present(root_html)
    root_html = transform_root_index(root_html, locales[DEFAULT_LOCALE], all_slugs, all_locales_data)
    root_index_path.write_text(root_html, encoding="utf-8")
    print(f"✓ updated root public/index.html ({DEFAULT_LOCALE}, canonical={canonical_for(DEFAULT_LOCALE)})")
    
    for slug, locale in locales.items():
        if slug == DEFAULT_LOCALE:
            continue
        out_dir = PUBLIC / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        variant_html = transform_variant_index(root_html, locale, all_slugs, all_locales_data)
        (out_dir / "index.html").write_text(variant_html, encoding="utf-8")
        print(f"✓ built public/{slug}/index.html (canonical={canonical_for(slug)})")
    
    print(f"\n✓ GEO/AEO/SEO Enhanced Build Complete")
    print(f"  - {len(locales)} locales built")
    print(f"  - Schema.org markup added for AEO")
    print(f"  - GEO meta tags for regional targeting")
    print(f"  - Currency localization active")
    print(f"  - Unit conversion per region")

if __name__ == "__main__":
    build()