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
    "en-us": {
        "code": "US",
        "name": "United States",
        "lat": "37.0902",
        "lon": "-95.7129",
    },
    "en-ca": {"code": "CA", "name": "Canada", "lat": "56.1304", "lon": "-106.3468"},
    "en-gb": {
        "code": "GB",
        "name": "United Kingdom",
        "lat": "55.3781",
        "lon": "-3.4360",
    },
    "en-au": {"code": "AU", "name": "Australia", "lat": "-25.2744", "lon": "133.7751"},
}

# Currency configuration
CURRENCY_CONFIG = {
    "en-us": {"symbol": "$", "code": "USD", "position": "before"},
    "en-ca": {"symbol": "CA$", "code": "CAD", "position": "before"},
    "en-gb": {"symbol": "£", "code": "GBP", "position": "before"},
    "en-au": {"symbol": "A$", "code": "AUD", "position": "before"},
}

# Unit configurations per region
UNITS_CONFIG = {
    "en-us": {"fuel": "MPG", "distance": "miles", "volume": "gallons", "fuel_word": "Gas", "distance_word": "miles"},
    "en-ca": {"fuel": "MPG", "distance": "kilometers", "volume": "liters", "fuel_word": "Gas", "distance_word": "kilometers"},
    "en-gb": {"fuel": "MPG Imp", "distance": "miles", "volume": "liters", "fuel_word": "Petrol", "distance_word": "miles"},
    "en-au": {"fuel": "L/100km", "distance": "kilometers", "volume": "liters", "fuel_word": "Petrol", "distance_word": "kilometers"},
}


# Open Graph locales
OG_LOCALES = {"en-us": "en_US", "en-ca": "en_CA", "en-gb": "en_GB", "en-au": "en_AU"}


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


def build_hreflang_block(all_locales: list[str], rel_path: str = "index.html") -> str:
    lines = []
    # If rel_path is index.html, we treat it as root
    path_suffix = "" if rel_path == "index.html" else rel_path.replace("index.html", "")

    for slug in all_locales:
        if slug == DEFAULT_LOCALE:
            href = f"{SITE_URL}/{path_suffix}"
        else:
            href = f"{SITE_URL}/{slug}/{path_suffix}"
        lines.append(f'  <link rel="alternate" hreflang="{slug}" href="{href}" />')
    
    x_default = f"{SITE_URL}/{path_suffix}"
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{x_default}" />')
    return "\n".join(lines)


def canonical_for(slug: str, rel_path: str = "index.html") -> str:
    path_suffix = "" if rel_path == "index.html" else rel_path.replace("index.html", "")
    
    if CANONICAL_MODE == "us-consolidated":
        return f"{SITE_URL}/{path_suffix}"
    
    if slug == DEFAULT_LOCALE:
        return f"{SITE_URL}/{path_suffix}"
    return f"{SITE_URL}/{slug}/{path_suffix}"


def build_schema_org(slug: str, locale_data: dict, rel_path: str = "index.html") -> str:
    """Generate Schema.org JSON-LD for AEO"""
    geo = GEO_REGIONS.get(slug, GEO_REGIONS["en-us"])
    currency = CURRENCY_CONFIG.get(slug, CURRENCY_CONFIG["en-us"])
    units = UNITS_CONFIG.get(slug, UNITS_CONFIG["en-us"])
    path_suffix = "" if rel_path == "index.html" else rel_path.replace("index.html", "")
    page_url = f"{SITE_URL}/{path_suffix}" if slug == DEFAULT_LOCALE else f"{SITE_URL}/{slug}/{path_suffix}"

    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "FuelEcon",
        "alternateName": "Fuel Economy Calculator",
        "url": page_url,
        "inLanguage": slug,
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{SITE_URL}/?q={{search_term_string}}",
            "query-input": "required name=search_term_string",
        },
    }

    # Add geo-specific organization data
    org_schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": f"FuelEcon {geo['name']}",
        "url": page_url,
        "logo": f"{SITE_URL}/favicon.svg",
        "sameAs": [
            "https://github.com/o87enterprises-ai",
            "https://github.com/TruegleAi"
        ],
        "contactPoint": {
            "@type": "ContactPoint",
            "email": "hello@trumpafi.online",
            "contactType": "customer support"
        },
        "address": {"@type": "PostalAddress", "addressCountry": geo["code"]},
        "currenciesAccepted": currency["code"],
        "paymentAccepted": "Credit Card, Debit Card, PayPal",
    }

    # Add FAQPage schema
    faq_data = locale_data.get("home", {}).get("faq", [])
    faq_schema = None
    if faq_data:
        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item["q"],
                    "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
                }
                for item in faq_data
            ],
        }

    # Add HowTo schema
    howto_schema = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": f"How to Calculate Trip {units['fuel_word']} Cost",
        "description": "Calculate the exact cost of your next trip based on your car's fuel economy and current gas prices.",
        "step": [
            {
                "@type": "HowToStep",
                "name": "Select your vehicle",
                "text": "Pick your car from our presets or enter your own MPG manually.",
                "url": f"{SITE_URL}#vehicle-card"
            },
            {
                "@type": "HowToStep",
                "name": "Enter trip distance",
                "text": f"Type in your trip distance in {units['distance_word']} or use the slider.",
                "url": f"{SITE_URL}#trip-card"
            },
            {
                "@type": "HowToStep",
                "name": "Choose your route type",
                "text": "Select whether you'll be driving on highways or back roads for a more accurate estimate.",
                "url": f"{SITE_URL}#trip-card"
            },
            {
                "@type": "HowToStep",
                "name": "See your results",
                "text": "Your total trip cost and fuel needed will update instantly in the results panel.",
                "url": f"{SITE_URL}#resultPanel"
            }
        ]
    }

    out = f"""<script type="application/ld+json">
{json.dumps(schema, indent=2)}
</script>
<script type="application/ld+json">
{json.dumps(org_schema, indent=2)}
</script>"""

    if faq_schema:
        out += f"""\n<script type="application/ld+json">
{json.dumps(faq_schema, indent=2)}
</script>"""

    out += f"""\n<script type="application/ld+json">
{json.dumps(howto_schema, indent=2)}
</script>"""

    return out


def build_faq_html(faq_data: list[dict]) -> str:
    if not faq_data:
        return ""
    items = []
    for item in faq_data:
        html = f"""<div class="faq-item">
    <button class="faq-question">
      {item['q']}
      <i class="fas fa-chevron-down"></i>
    </button>
    <div class="faq-answer">
      <p>{item['a']}</p>
    </div>
  </div>"""
        items.append(html)
    return "\n".join(items)


def build_lang_switcher_html(current_slug: str, all_locales: list[dict]) -> str:
    options = []
    for loc in all_locales:
        slug = loc["_meta"]["locale"]
        display = loc["_meta"]["locale_display"]
        selected = " selected" if slug == current_slug else ""
        path = "/" if slug == DEFAULT_LOCALE else f"/{slug}/"
        options.append(f'      <option value="{path}"{selected}>{display}</option>')
    options_html = "\n".join(options)
    return f"""<div class="lang-switcher" aria-label="Language and region">
    <label for="langSelect" style="display:none;">Language</label>
    <select id="langSelect" onchange="window.location.href=this.value" aria-label="Switch language">
{options_html}
    </select>
  </div>"""


def transform_root_index(
    html: str, master: dict, all_slugs: list[str], all_locales_data: list[dict], rel_path: str = "index.html"
) -> str:
    hreflang_block = build_hreflang_block(all_slugs, rel_path)
    canonical = canonical_for(DEFAULT_LOCALE, rel_path)
    switcher = build_lang_switcher_html(DEFAULT_LOCALE, all_locales_data)

    html = re.sub(r'<html lang="[^"]*">', f'<html lang="{DEFAULT_LOCALE}">', html)
    html = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{canonical}">',
        html,
    )
    html = re.sub(
        r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*" />', "", html
    )
    html = re.sub(r"\s*<!-- HREFLANG_BLOCK -->", "", html)

    # FAQ injection
    faq_html = build_faq_html(master.get("home", {}).get("faq", []))
    html = html.replace("<!-- FAQ_ITEMS_PLACEHOLDER -->", faq_html)

    # Add GEO meta tags for root
    geo = GEO_REGIONS[DEFAULT_LOCALE]
    geo_tags = f'    <meta name="geo.region" content="{geo["code"]}" />\n    <meta name="geo.placename" content="{geo["name"]}" />\n    <meta name="geo.position" content="{geo["lat"]};{geo["lon"]}" />\n    <meta name="ICBM" content="{geo["lat"]}, {geo["lon"]}" />'

    # Currency meta tag (for JS to read)
    currency = CURRENCY_CONFIG[DEFAULT_LOCALE]
    currency_meta = f'    <meta name="currency-symbol" content="{currency["symbol"]}" />'

    # Inject strings for JS
    js_strings = master.get("js", {})
    js_injection = f"""<script>
  window.FUELECON_LOCALE = "{DEFAULT_LOCALE}";
  window.FUELECON_STRINGS = {json.dumps(js_strings, ensure_ascii=False)};
</script>"""

    html = html.replace(
        "</head>",
        f"  <!-- HREFLANG_BLOCK -->\n{hreflang_block}\n    {geo_tags}\n    {currency_meta}\n{js_injection}\n</head>",
        1,
    )

    # Add Schema.org
    schema = build_schema_org(DEFAULT_LOCALE, master, rel_path)
    html = html.replace("</head>", f"{schema}\n</head>", 1)

    if 'class="lang-switcher"' not in html:
        html = re.sub(
            r'(<div class="premium-badge")', f"{switcher}\n    \\1", html, count=1
        )

    return html


def apply_variant_transforms(
    root_html: str, locale: dict, all_slugs: list[str], all_locales_data: list[dict], rel_path: str = "index.html"
) -> str:
    slug = locale["_meta"]["locale"]
    meta = locale["_meta"]
    home = locale.get("home", {})
    footer = locale.get("footer", {})

    # Currency config (needed early)
    currency = CURRENCY_CONFIG.get(slug, CURRENCY_CONFIG["en-us"])

    html = root_html

    # Meta tags
    meta_title = home.get("meta_title", "")
    meta_desc = home.get("meta_description", "")
    if meta_title:
        html = re.sub(
            r"<title>[^<]*</title>", f"<title>{meta_title}</title>", html, count=1
        )
        html = re.sub(
            r'<meta property="og:title" content="[^"]*">',
            f'<meta property="og:title" content="{meta_title}">',
            html,
        )

    if meta_desc:
        html = re.sub(
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{meta_desc}">',
            html,
        )
        html = re.sub(
            r'<meta property="og:description" content="[^"]*">',
            f'<meta property="og:description" content="{meta_desc}">',
            html,
        )

    # Canonical + hreflang
    canonical = canonical_for(slug, rel_path)
    html = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{canonical}">',
        html,
    )
    html = re.sub(
        r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*" />', "", html
    )
    html = re.sub(r"\s*<!-- HREFLANG_BLOCK -->", "", html)

    hreflang_block = build_hreflang_block(all_slugs, rel_path)

    # GEO meta tags
    geo = GEO_REGIONS.get(slug, GEO_REGIONS["en-us"])
    geo_tags = f'    <meta name="geo.region" content="{geo["code"]}" />\n    <meta name="geo.placename" content="{geo["name"]}" />\n    <meta name="geo.position" content="{geo["lat"]};{geo["lon"]}" />\n    <meta name="ICBM" content="{geo["lat"]}, {geo["lon"]}" />'

    # Open Graph locale
    og_locale = OG_LOCALES.get(slug, "en_US")
    html = re.sub(
        r'<meta property="og:locale" content="[^"]*">',
        f'<meta property="og:locale" content="{og_locale}">',
        html,
    )

    # Currency symbol replacement (must happen BEFORE JS injection)
    # Use unique placeholders to avoid corrupting the JS injection or template literals
    js_strings = locale.get("js", {})
    if currency["symbol"] != "$":
        import copy

        js_strings_safe = copy.deepcopy(js_strings)
        # Protect savings placeholder
        for key in ["highwaySaving"]:
            if key in js_strings_safe.get("ecoAdvice", {}):
                old_val = js_strings_safe["ecoAdvice"][key]
                js_strings_safe["ecoAdvice"][key] = old_val.replace(
                    "${savings}", "__SAVINGS_PLACEHOLDER__"
                )
        # Protect currencySymbol
        if "currencySymbol" in js_strings_safe:
            js_strings_safe["currencySymbol"] = "__CURRENCY_SYMBOL__"

        js_injection = f"""<script>
  window.FUELECON_LOCALE = "{slug}";
  window.FUELECON_STRINGS = {json.dumps(js_strings_safe, ensure_ascii=False)};
</script>"""
        html = html.replace("</head>", f"{js_injection}\n</head>", 1)

        # Protect ALL JS template literals ${...} in the HTML before global replacement
        # We'll use a regex to find ${...} and replace it with a token
        protected_literals = []
        def protect_literal(match):
            protected_literals.append(match.group(0))
            return f"__JS_LITERAL_{len(protected_literals)-1}__"
        
        html = re.sub(r'\$\{([^}]+)\}', protect_literal, html)

        # Now do currency replacement in the rest of HTML
        html = html.replace("$", currency["symbol"])

        # Restore JS template literals
        for i, literal in enumerate(protected_literals):
            html = html.replace(f"__JS_LITERAL_{i}__", literal)

        # Fix the placeholders in JS injection
        html = html.replace("__SAVINGS_PLACEHOLDER__", "${savings}")
        html = html.replace("__CURRENCY_SYMBOL__", currency["symbol"])
    else:
        # No replacement needed, inject directly
        js_injection = f"""<script>
  window.FUELECON_LOCALE = "{slug}";
  window.FUELECON_STRINGS = {json.dumps(js_strings, ensure_ascii=False)};
</script>"""
        html = html.replace("</head>", f"{js_injection}\n</head>", 1)

    # Insert all meta tags
    html = html.replace(
        "</head>",
        f"  <!-- HREFLANG_BLOCK -->\n{hreflang_block}\n    {geo_tags}\n</head>",
        1,
    )

    # Add Schema.org for variant
    schema = build_schema_org(slug, locale, rel_path)
    html = html.replace("</head>", f"{schema}\n</head>", 1)

    # Language switcher
    switcher_new = build_lang_switcher_html(slug, all_locales_data)
    html = re.sub(
        r'<div class="lang-switcher".*?</div>',
        switcher_new,
        html,
        flags=re.DOTALL,
    )

    # Unit conversion labels
    units = UNITS_CONFIG.get(slug, UNITS_CONFIG["en-us"])
    html = html.replace("MPG", units["fuel"])
    html = html.replace("miles", units["distance"])
    html = html.replace("gallons", units["volume"])

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


def apply_variant_transforms(
    root_html: str, locale: dict, all_slugs: list[str], all_locales_data: list[dict], rel_path: str = "index.html"
) -> str:
    slug = locale["_meta"]["locale"]
    meta = locale["_meta"]
    home = locale.get("home", {})
    footer = locale.get("footer", {})

    # Currency config (needed early)
    currency = CURRENCY_CONFIG.get(slug, CURRENCY_CONFIG["en-us"])

    html = root_html

    # Meta tags
    meta_title = home.get("meta_title", "")
    meta_desc = home.get("meta_description", "")
    if meta_title:
        html = re.sub(
            r"<title>[^<]*</title>", f"<title>{meta_title}</title>", html, count=1
        )
        html = re.sub(
            r'<meta property="og:title" content="[^"]*">',
            f'<meta property="og:title" content="{meta_title}">',
            html,
        )

    if meta_desc:
        html = re.sub(
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{meta_desc}">',
            html,
        )
        html = re.sub(
            r'<meta property="og:description" content="[^"]*">',
            f'<meta property="og:description" content="{meta_desc}">',
            html,
        )

    # Canonical + hreflang
    canonical = canonical_for(slug, rel_path)
    html = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{canonical}">',
        html,
    )
    html = re.sub(
        r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*" />', "", html
    )
    html = re.sub(r"\s*<!-- HREFLANG_BLOCK -->", "", html)

    hreflang_block = build_hreflang_block(all_slugs, rel_path)

    # GEO meta tags
    geo = GEO_REGIONS.get(slug, GEO_REGIONS["en-us"])
    geo_tags = f'    <meta name="geo.region" content="{geo["code"]}" />\n    <meta name="geo.placename" content="{geo["name"]}" />\n    <meta name="geo.position" content="{geo["lat"]};{geo["lon"]}" />\n    <meta name="ICBM" content="{geo["lat"]}, {geo["lon"]}" />'

    # Open Graph locale
    og_locale = OG_LOCALES.get(slug, "en_US")
    html = re.sub(
        r'<meta property="og:locale" content="[^"]*">',
        f'<meta property="og:locale" content="{og_locale}">',
        html,
    )

    # Currency symbol replacement (must happen BEFORE JS injection)
    # Use unique placeholders to avoid corrupting the JS injection or template literals
    js_strings = locale.get("js", {})
    if currency["symbol"] != "$":
        import copy

        js_strings_safe = copy.deepcopy(js_strings)
        # Protect savings placeholder
        for key in ["highwaySaving"]:
            if key in js_strings_safe.get("ecoAdvice", {}):
                old_val = js_strings_safe["ecoAdvice"][key]
                js_strings_safe["ecoAdvice"][key] = old_val.replace(
                    "${savings}", "__SAVINGS_PLACEHOLDER__"
                )
        # Protect currencySymbol
        if "currencySymbol" in js_strings_safe:
            js_strings_safe["currencySymbol"] = "__CURRENCY_SYMBOL__"

        js_injection = f"""<script>
  window.FUELECON_LOCALE = "{slug}";
  window.FUELECON_STRINGS = {json.dumps(js_strings_safe, ensure_ascii=False)};
</script>"""
        html = html.replace("</head>", f"{js_injection}\n</head>", 1)

        # Protect ALL JS template literals ${...} in the HTML before global replacement
        # We'll use a regex to find ${...} and replace it with a token
        protected_literals = []
        def protect_literal(match):
            protected_literals.append(match.group(0))
            return f"__JS_LITERAL_{len(protected_literals)-1}__"
        
        html = re.sub(r'\$\{([^}]+)\}', protect_literal, html)

        # Now do currency replacement in the rest of HTML
        html = html.replace("$", currency["symbol"])

        # Restore JS template literals
        for i, literal in enumerate(protected_literals):
            html = html.replace(f"__JS_LITERAL_{i}__", literal)

        # Fix the placeholders in JS injection
        html = html.replace("__SAVINGS_PLACEHOLDER__", "${savings}")
        html = html.replace("__CURRENCY_SYMBOL__", currency["symbol"])
    else:
        # No replacement needed, inject directly
        js_injection = f"""<script>
  window.FUELECON_LOCALE = "{slug}";
  window.FUELECON_STRINGS = {json.dumps(js_strings, ensure_ascii=False)};
</script>"""
        html = html.replace("</head>", f"{js_injection}\n</head>", 1)

    # Insert all meta tags
    html = html.replace(
        "</head>",
        f"  <!-- HREFLANG_BLOCK -->\n{hreflang_block}\n    {geo_tags}\n</head>",
        1,
    )

    # Add Schema.org for variant
    schema = build_schema_org(slug, locale, rel_path)
    html = html.replace("</head>", f"{schema}\n</head>", 1)

    # Language switcher
    switcher_new = build_lang_switcher_html(slug, all_locales_data)
    html = re.sub(
        r'<div class="lang-switcher".*?</div>',
        switcher_new,
        html,
        flags=re.DOTALL,
    )

    # Unit conversion labels
    units = UNITS_CONFIG.get(slug, UNITS_CONFIG["en-us"])
    html = html.replace("MPG", units["fuel"])
    html = html.replace("miles", units["distance"])
    html = html.replace("gallons", units["volume"])

    return html
    return html.replace("</style>", f"{LANG_SWITCHER_CSS}\n</style>", 1)


def build():
    locales = load_locales()
    all_slugs = list(locales.keys())
    all_locales_data = list(locales.values())

    # Pages to process: index.html and all tools in subdirectories
    pages_to_process = [PUBLIC / "index.html"]
    for tool_dir in ["mpg-converter", "split-fuel", "ev-vs-gas", "commute-cost"]:
        tool_path = PUBLIC / tool_dir / "index.html"
        if tool_path.exists():
            pages_to_process.append(tool_path)

    for page_path in pages_to_process:
        rel_path = page_path.relative_to(PUBLIC)
        is_root = rel_path == Path("index.html")
        
        original_html = page_path.read_text(encoding="utf-8")
        original_html = ensure_css_block_present(original_html)

        # 1. Update root version of the page
        processed_root = transform_root_index(
            original_html, locales[DEFAULT_LOCALE], all_slugs, all_locales_data
        )
        page_path.write_text(processed_root, encoding="utf-8")
        print(f"✓ updated root {rel_path} ({DEFAULT_LOCALE})")

        # 2. Build variants for this page
        for slug, locale in locales.items():
            if slug == DEFAULT_LOCALE:
                continue
            
            variant_html = apply_variant_transforms(
                original_html, locale, all_slugs, all_locales_data
            )
            
            out_path = PUBLIC / slug / rel_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(variant_html, encoding="utf-8")
            print(f"✓ built public/{slug}/{rel_path}")

    print(f"\n✓ GEO/AEO/SEO Enhanced Build Complete")
    print(f"  - {len(locales)} locales built")
    print(f"  - Schema.org markup added for AEO")
    print(f"  - GEO meta tags for regional targeting")
    print(f"  - Currency localization active")
    print(f"  - Unit conversion per region")


if __name__ == "__main__":
    build()
