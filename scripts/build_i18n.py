#!/usr/bin/env python3
"""
FuelEcon · i18n build script
=============================

What it does:
  1. Reads every locale JSON from i18n/
  2. Merges each locale onto the en-us master (deep merge)
  3. For each non-default locale, generates public/<locale>/index.html by
     transforming the root public/index.html:
       - Rewrites meta title/description
       - Swaps unit/currency labels per _meta
       - Injects hreflang tags (x-default + every locale)
       - Sets canonical to en-US root (aggressive consolidation)
       - Injects language switcher into header
  4. Also injects the language switcher + hreflang into root public/index.html

Run: python3 scripts/build_i18n.py
Output: public/en-gb/, public/en-ca/, public/en-au/  (each with index.html)
        public/index.html is updated in-place with switcher + hreflang.

Config:
  CANONICAL_MODE = 'us-consolidated'   # points all variants to en-US root
  CANONICAL_MODE = 'self-referential'  # each variant self-canonicals
"""

import json
import re
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent.parent
I18N_DIR = ROOT / "i18n"
PUBLIC = ROOT / "public"
SITE_URL = "https://fuelecon.pages.dev"

# ------------------- configuration -------------------
DEFAULT_LOCALE = "en-us"
CANONICAL_MODE = "us-consolidated"   # or "self-referential"

# ------------------- helpers -------------------

def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base. Override wins on conflicts."""
    out = deepcopy(base)
    for key, val in override.items():
        if key in out and isinstance(out[key], dict) and isinstance(val, dict):
            out[key] = deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def load_locales() -> dict:
    """Load all locale JSONs; merge deltas onto en-us master."""
    en_us_path = I18N_DIR / f"{DEFAULT_LOCALE}.json"
    master = json.loads(en_us_path.read_text(encoding="utf-8"))

    locales = {DEFAULT_LOCALE: master}
    for p in sorted(I18N_DIR.glob("*.json")):
        slug = p.stem
        if slug == DEFAULT_LOCALE:
            continue
        delta = json.loads(p.read_text(encoding="utf-8"))
        locales[slug] = deep_merge(master, delta)
    return locales


def build_hreflang_block(all_locales: list[str]) -> str:
    """Generate <link rel='alternate' hreflang='...'> tags for every locale + x-default."""
    lines = []
    for slug in all_locales:
        href = SITE_URL + "/" if slug == DEFAULT_LOCALE else f"{SITE_URL}/{slug}/"
        lines.append(f'  <link rel="alternate" hreflang="{slug}" href="{href}" />')
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{SITE_URL}/" />')
    return "\n".join(lines)


def canonical_for(slug: str) -> str:
    if CANONICAL_MODE == "us-consolidated":
        return f"{SITE_URL}/"
    # self-referential
    return SITE_URL + "/" if slug == DEFAULT_LOCALE else f"{SITE_URL}/{slug}/"


def build_lang_switcher_html(current_slug: str, all_locales: list[dict]) -> str:
    """Inline <select>-based language switcher. Plays nice without JS frameworks."""
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


# ------------------- transformations -------------------

def transform_root_index(html: str, master: dict, all_slugs: list[str], all_locales_data: list[dict]) -> str:
    """Apply hreflang block + language switcher to the en-US (root) index.html."""
    hreflang_block = build_hreflang_block(all_slugs)
    canonical = canonical_for(DEFAULT_LOCALE)
    switcher = build_lang_switcher_html(DEFAULT_LOCALE, all_locales_data)

    # Set <html lang="en-us">
    html = re.sub(r'<html lang="[^"]*">', f'<html lang="{DEFAULT_LOCALE}">', html)

    # Replace canonical link
    html = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{canonical}">',
        html,
    )

    # Strip any existing hreflang block before reinserting (idempotent re-runs)
    html = re.sub(
        r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*" />',
        '',
        html,
    )
    html = re.sub(r'\s*<!-- HREFLANG_BLOCK -->', '', html)

    # Insert fresh hreflang block before </head>
    html = html.replace(
        "</head>",
        f"  <!-- HREFLANG_BLOCK -->\n{hreflang_block}\n</head>",
        1,
    )

    # Inject language switcher into header (replace or add)
    if 'class="lang-switcher"' not in html:
        html = re.sub(
            r'(<div class="premium-badge")',
            f'{switcher}\n    \\1',
            html,
            count=1,
        )

    return html


def transform_variant_index(
    root_html: str,
    locale: dict,
    all_slugs: list[str],
    all_locales_data: list[dict],
) -> str:
    """Transform the root en-US HTML into a variant's HTML by applying locale substitutions."""
    slug = locale["_meta"]["locale"]
    meta = locale["_meta"]
    home = locale.get("home", {})
    footer = locale.get("footer", {})

    html = root_html

    # --- meta tags ---
    meta_title = home.get("meta_title", "")
    meta_desc = home.get("meta_description", "")
    if meta_title:
        html = re.sub(r"<title>[^<]*</title>", f"<title>{meta_title}</title>", html, count=1)
        html = re.sub(
            r'<meta property="og:title" content="[^"]*">',
            f'<meta property="og:title" content="{meta_title}">',
            html,
        )
        html = re.sub(
            r'<meta name="twitter:title" content="[^"]*">',
            f'<meta name="twitter:title" content="{meta_title}">',
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
        html = re.sub(
            r'<meta name="twitter:description" content="[^"]*">',
            f'<meta name="twitter:description" content="{meta_desc}">',
            html,
        )

    # --- canonical + hreflang ---
    canonical = canonical_for(slug)
    html = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{canonical}">',
        html,
    )

    # Strip ALL existing hreflang tags (whether inside marker block or not)
    # then reinject a single clean block.
    html = re.sub(
        r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*" />',
        '',
        html,
    )
    # Also strip the now-orphaned marker comment if it exists
    html = re.sub(r'\s*<!-- HREFLANG_BLOCK -->', '', html)

    # Inject a fresh hreflang block + marker just before </head>
    hreflang_block = build_hreflang_block(all_slugs)
    html = html.replace(
        "</head>",
        f"  <!-- HREFLANG_BLOCK -->\n{hreflang_block}\n</head>",
        1,
    )

    # --- html lang attr ---
    html = re.sub(r'<html lang="[^"]*">', f'<html lang="{slug}">', html)

    # --- language switcher (reflect current locale as selected) ---
    switcher_new = build_lang_switcher_html(slug, all_locales_data)
    html = re.sub(
        r'<div class="lang-switcher".*?</div>\s*(?=<div class="premium-badge")',
        switcher_new + "\n    ",
        html,
        flags=re.DOTALL,
    )

    # --- text substitutions in home content ---
    # tagline in header
    if home.get("vehicle_card_blurb"):
        html = re.sub(
            r"(Tell us your car's MPG[^<]*?save it for next time\.|Don't know your MPG\?[^<]*)",
            home["vehicle_card_blurb"],
            html,
            count=1,
        )

    # Card titles + labels
    swaps = [
        (r">What are you driving\?<",          f">{home.get('vehicle_card_title', 'What are you driving?')}<"),
        (r">How far are you going\?<",         f">{home.get('trip_card_title',    'How far are you going?')}<"),
        (r">Quick pick your car<",             f">{home.get('preset_title',       'Quick pick your car')}<"),
        (r">Live widget<",                     f">{home.get('widget_title',       'Live widget')}<"),
        (r">Gas-saving tips<",                 f">{home.get('tips_card_title',    'Gas-saving tips')}<"),
        (r">Work out this trip<",              f">{home.get('btn_calculate',      'Work out this trip')}<"),
        (r">Save this car<",                   f">{home.get('btn_save_car',       'Save this car')}<"),
        (r">Show me another tip<",             f">{home.get('btn_new_tip',        'Show me another tip')}<"),
        (r">Use this MPG<",                    f">{home.get('preset_apply_btn',   'Use this MPG')}<"),
        (r">or enter your own<",               f">{home.get('or_enter_own',       'or enter your own')}<"),
    ]
    for pattern, replacement in swaps:
        html = re.sub(pattern, replacement, html)

    # Labels (these carry the unit / currency in parentheses)
    # NOTE: labels contain inner <i class="fas..."> icons, so we use .*? with DOTALL
    html = re.sub(
        r'<label for="mpgInput">.*?</label>',
        f'<label for="mpgInput"><i class="fas fa-tachometer-alt"></i> {home.get("label_fuel_economy", "Fuel economy (MPG)")}</label>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'<label for="gasPriceInput">.*?</label>',
        f'<label for="gasPriceInput"><i class="fas fa-gas-pump"></i> {home.get("label_gas_price", "Gas price ($ / gal)")}</label>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'<label for="distanceSlider">.*?</label>',
        f'<label for="distanceSlider">{home.get("label_distance", "📏 Distance (miles)")}</label>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'<label for="tireBooster">.*?</label>',
        f'<label for="tireBooster"><i class="fas fa-wind"></i> {home.get("label_tires", "Tire pressure")}</label>',
        html,
        flags=re.DOTALL,
    )

    # Route type options
    route_hw = home.get("route_highway", "🛣️ Freeway / Highway (best MPG)")
    route_br = home.get("route_backroads", "🌲 Back roads / City (lower MPG)")
    html = re.sub(
        r'<option value="highway">[^<]*</option>',
        f'<option value="highway">{route_hw}</option>',
        html,
    )
    html = re.sub(
        r'<option value="backroads">[^<]*</option>',
        f'<option value="backroads">{route_br}</option>',
        html,
    )

    # EV notice
    ev_html = home.get("ev_notice_html")
    if ev_html:
        html = re.sub(
            r'(<div class="ev-notice">\s*)(⚡[^<]*<a[^>]*>[^<]*</a>[^<]*)(\s*</div>)',
            lambda m: m.group(1) + ev_html + m.group(3),
            html,
            count=1,
        )

    # Footer blurb + legal line
    if footer.get("blurb"):
        html = re.sub(
            r'(Plain-English tools[^<]*?Built by drivers, for drivers\.)',
            footer["blurb"],
            html,
            count=1,
        )

    # Set default gas-price input value to the locale default
    gas_default = meta.get("gas_price_default")
    if gas_default is not None:
        html = re.sub(
            r'(<input[^>]*id="gasPriceInput"[^>]*value=")[^"]*(")',
            lambda m: f'{m.group(1)}{gas_default}{m.group(2)}',
            html,
            count=1,
        )
        # Also patch the JS loadDefaultVehicle() call, which overrides the HTML on init.
        # Pattern: syncInputsFromVehicle({ name: '...', mpg: 28.5, gasPrice: 3.65 });
        html = re.sub(
            r"(syncInputsFromVehicle\(\{\s*name:\s*'[^']*',\s*mpg:\s*)[\d.]+(\s*,\s*gasPrice:\s*)[\d.]+(\s*\}\);)",
            lambda m: f'{m.group(1)}28.5{m.group(2)}{gas_default}{m.group(3)}',
            html,
            count=1,
        )

    # Adjust footer tool links to be locale-prefixed where applicable
    # (/ev-vs-gas -> /en-gb/ev-vs-gas etc.)
    for tool in ["mpg-converter", "split-fuel", "ev-vs-gas"]:
        html = html.replace(f'href="/{tool}/"', f'href="/{slug}/{tool}/"')
    # about / contact / privacy / terms / disclosure stay en-US only for now
    # (variant versions come in Phase 2 Week 3+)

    return html


# ------------------- CSS injection (language switcher styling) -------------------

LANG_SWITCHER_CSS = """
/* ---------- Language switcher (injected by build_i18n.py) ---------- */
.lang-switcher {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.lang-switcher select {
  padding: 8px 30px 8px 14px;
  border-radius: 100px;
  border: 1.5px solid var(--c-border);
  background: white url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%231A5F3F' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><polyline points='6 9 12 15 18 9'></polyline></svg>") no-repeat right 12px center;
  appearance: none;
  -webkit-appearance: none;
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--c-ink);
  cursor: pointer;
  transition: 0.15s;
}
.lang-switcher select:hover { border-color: var(--c-primary); }
.lang-switcher select:focus {
  outline: none;
  border-color: var(--c-primary);
  box-shadow: 0 0 0 3px rgba(26,95,63,0.15);
}
"""

def ensure_css_block_present(html: str) -> str:
    """Append language-switcher CSS to the <style> block if not there."""
    if ".lang-switcher {" in html:
        return html
    return html.replace("</style>", f"{LANG_SWITCHER_CSS}\n</style>", 1)


# ------------------- build -------------------

def build():
    locales = load_locales()
    all_slugs = list(locales.keys())
    all_locales_data = list(locales.values())

    root_index_path = PUBLIC / "index.html"
    root_html = root_index_path.read_text(encoding="utf-8")

    # Always inject CSS + switcher + hreflang into the root
    root_html = ensure_css_block_present(root_html)
    root_html = transform_root_index(root_html, locales[DEFAULT_LOCALE], all_slugs, all_locales_data)
    root_index_path.write_text(root_html, encoding="utf-8")
    print(f"✓ updated root public/index.html ({DEFAULT_LOCALE}, canonical={canonical_for(DEFAULT_LOCALE)})")

    # Generate each variant
    for slug, locale in locales.items():
        if slug == DEFAULT_LOCALE:
            continue
        out_dir = PUBLIC / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        variant_html = transform_variant_index(root_html, locale, all_slugs, all_locales_data)
        (out_dir / "index.html").write_text(variant_html, encoding="utf-8")
        print(f"✓ built public/{slug}/index.html (canonical={canonical_for(slug)})")

    # Summary
    print("\n" + "─" * 50)
    print(f"Locales built:      {len(locales)}")
    print(f"Canonical mode:     {CANONICAL_MODE}")
    print(f"Default locale URL: {SITE_URL}/")
    print("Variant URLs:")
    for slug in all_slugs:
        if slug != DEFAULT_LOCALE:
            print(f"  {SITE_URL}/{slug}/")
    print("─" * 50)


if __name__ == "__main__":
    build()
