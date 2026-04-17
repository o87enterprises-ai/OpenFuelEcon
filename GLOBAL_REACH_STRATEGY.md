# FuelEcon · Global Reach Strategy

> Multilingual rollout · SEO · AEO · GEO
> Owner: o87Dev / TruegleAi · Phase 2 deliverable
> Companion to `BUILD_STRATEGY.md`

---

## 0. Definitions (so we're using the same words)

- **SEO** — Search Engine Optimization. Getting FuelEcon ranked in Google/Bing for text queries people type. Traditional.
- **AEO** — Answer Engine Optimization. Getting FuelEcon's content *selected* by AI answer engines (Google's AI Overviews, Bing Copilot, ChatGPT Search, Perplexity) as the source of the answer they show directly.
- **GEO** — Generative Engine Optimization. Getting FuelEcon cited *inside* generative AI responses (ChatGPT, Claude, Gemini) even when there's no search box. The ChatGPT user asks about fuel costs → the model pulls from FuelEcon.
- **i18n** — Internationalization: making the site work in multiple languages and for multiple regional contexts (currency, units, gas-price sources, vehicle makes).

The three optimizations overlap but have different signals. We need all three, in sequence.

---

## 1. The big picture in one paragraph

Search is bifurcating into **classic search** (Google keyword results) and **answer surfaces** (AI summaries, chatbots, voice assistants). Utility sites like FuelEcon win in both if they emit the right signals: clean schema.org markup, plain-English Q&A content, citable facts with sources, and localized versions that match the regional context of the query. Our advantage is being first — most fuel-economy sites are English-only, cluttered with legacy content, and optimized for 2015-era SEO. A clean multilingual site with proper AEO/GEO structure can leapfrog them in markets that established players ignore.

---

## 2. Market prioritization — locale tiers

Not all locales are equal revenue-wise. AdSense RPM by market varies from $12 (US) to $0.30 (low-income Asia). Translation + content maintenance has real cost. Tier the rollout:

### Tier 1 — English variants (launch first)

| Locale | URL | Why | Est. RPM |
|---|---|---|---|
| `en-US` | `/` (default) | Largest market, highest RPM | $6–12 |
| `en-GB` | `/en-gb/` | Second-largest English market, different units (L/100km context) | $4–8 |
| `en-CA` | `/en-ca/` | Bilingual market, gas-cost anxiety cultural topic | $5–9 |
| `en-AU` | `/en-au/` | High RPM, relevant (big distances, expensive fuel) | $5–9 |

**Cost to implement:** almost zero. Same language, different unit defaults and gas-price data sources. Copy stays identical except spelling (e.g., "tires" → "tyres"). 95% of the revenue upside with 5% of the work.

### Tier 2 — High-value non-English (Q2 rollout)

| Locale | URL | Market size | Why |
|---|---|---|---|
| `es` | `/es/` | ~500M speakers | US Hispanic + LatAm + Spain; strong fuel-cost cultural relevance |
| `de` | `/de/` | ~100M speakers | High AdSense RPM, data-driven driving culture |
| `fr` | `/fr/` | ~280M speakers | France + Canada + West Africa |
| `pt-BR` | `/pt-br/` | ~210M speakers | Brazil has distinct fuel market (ethanol/gasoline mix) |

**Cost:** LLM-translate + native-speaker QA pass. Needs locale-specific data (European gas prices, Brazilian ANP data).

### Tier 3 — Growth markets (Q3+)

| Locale | URL | Notes |
|---|---|---|
| `it` | `/it/` | Italian — expensive fuel, engaged audience |
| `nl` | `/nl/` | Dutch — high RPM despite small population |
| `pl` | `/pl/` | Polish — fast-growing traffic, improving RPM |
| `ja` | `/ja/` | Japanese — different layout conventions, kanji density |
| `ko` | `/ko/` | Korean — strong early-adopter market |
| `tr` | `/tr/` | Turkish — very high fuel-cost anxiety, high engagement |

### Tier 4 — Revisit later

Arabic (RTL complexity, needs dedicated UX pass), Hindi (complex script rendering, lower RPM), Chinese (behind the Great Firewall — Baidu is a separate optimization project entirely).

---

## 3. URL architecture decision

Three patterns for multilingual sites; each has tradeoffs:

| Pattern | Example | Pros | Cons |
|---|---|---|---|
| **Subdirectory** | `fuelecon.com/es/` | One domain authority pool, simple hosting, best for SEO | Need server-side routing |
| **Subdomain** | `es.fuelecon.com` | Feels localized, easy separation | Splits domain authority |
| **ccTLD** | `fuelecon.es` | Strongest geo-signal | Expensive, squatting risk, fragmented authority |

**Decision: Subdirectory (`/es/`, `/de/`, etc.)**

Reasoning: FuelEcon is a small utility site, not a global enterprise. We need all our SEO authority concentrated on one hostname to rank competitively. Cloudflare Pages handles subdirectory routing trivially via `_redirects` or middleware. ccTLDs would cost us 14 × $10/yr in registration and 14× the domain-authority-split pain.

**Default locale (`/` with no prefix) = `en-US`.** No redirect to `/en-us/` — just serve English at root. This keeps our highest-revenue locale on the cleanest, shortest URL.

---

## 4. Technical implementation — two layers

### 4a. Static layer (Phase 2)

**Route pattern:** `/[locale]/[page]/`

Each locale is a directory: `public/en-gb/index.html`, `public/es/about/index.html`, etc. Build script generates these from a single source template + a translation JSON per locale.

**Translation source format** (one JSON per locale, kept in `i18n/[locale].json`):

```json
{
  "_meta": {
    "locale": "es",
    "language": "Spanish",
    "direction": "ltr",
    "currency": "EUR",
    "currency_symbol": "€",
    "distance_unit": "km",
    "volume_unit": "L",
    "decimal_separator": ",",
    "thousands_separator": "."
  },
  "nav": {
    "calculator": "Calculadora",
    "about": "Acerca",
    "privacy": "Privacidad",
    "terms": "Términos",
    "contact": "Contacto"
  },
  "home": {
    "title": "FuelEcon — Economía de Combustible Para Principiantes",
    "tagline": "Economía de combustible sin jerga",
    "h1_what_car": "¿Qué estás conduciendo?",
    "h1_how_far": "¿Qué tan lejos vas?"
  }
}
```

Build script iterates over every locale JSON × every page template → emits the static HTML. Rebuild time for all 16 locales × 6 pages ≈ 2 seconds on Cloudflare's edge.

### 4b. Dynamic layer (Phase 3)

Pages Functions at `/api/gas-price/:locale/:region` return locale-correct gas prices. Cloudflare KV caches the results.

| Locale | Data source | Update cadence |
|---|---|---|
| `en-US` | EIA weekly retail (by state) | Weekly (Mondays) |
| `en-GB` | UK Gov weekly fuel prices (by region) | Weekly (Mondays) |
| `en-CA` | Natural Resources Canada (by province) | Weekly (Tuesdays) |
| `en-AU` | ACCC report (by city) | Weekly (Fridays) |
| `es`, `de`, `fr`, `it`, `nl`, `pl` | EU Commission Weekly Oil Bulletin | Weekly (Mondays) |
| `pt-BR` | ANP (Agência Nacional do Petróleo) | Weekly (Wednesdays) |

Daily agent (Phase 4) polls all sources on their native schedules, normalizes to a common schema, writes to D1 + KV.

---

## 5. hreflang strategy

Every page declares its alternates. In `<head>` of every localized page:

```html
<link rel="alternate" hreflang="en-us" href="https://fuelecon.com/" />
<link rel="alternate" hreflang="en-gb" href="https://fuelecon.com/en-gb/" />
<link rel="alternate" hreflang="es"    href="https://fuelecon.com/es/" />
<link rel="alternate" hreflang="de"    href="https://fuelecon.com/de/" />
<!-- ... every locale ... -->
<link rel="alternate" hreflang="x-default" href="https://fuelecon.com/" />
```

**Critical rules:**
- Every page lists **all** alternates, including itself.
- `x-default` always points to the root (en-US). Used when no user locale matches.
- Tags live in both `<head>` and `sitemap.xml`. Google uses both; redundancy helps.
- No automatic redirect based on IP/language — Google warns against this. User picks via a visible language switcher.

---

## 6. SEO — classic search layer

### 6a. Keyword targeting by locale

Apply the "target queries where Google is surfacing new sites" strategy (from the YouTube video reference) per locale. Tools:

- **en-US, en-GB, en-AU, en-CA** → Clearer or Ahrefs, KD < 15
- **es, de, fr, pt-BR** → Google Keyword Planner with locale set, cross-reference Mangools KWFinder

First 20 target keywords per locale, prioritized by (monthly volume / keyword difficulty). Store the list in `docs/keyword-plans/[locale].md` so future maintenance has a paper trail.

### 6b. Programmatic page strategy (per locale)

Each locale gets its own set of programmatic pages built from local data:

- **`/gas-prices/[region]`** — 50 US states / 4 UK nations / 13 CA provinces / 8 AU states / 27 EU member states
- **`/mpg/[make]/[model]/[year]`** — locale-specific make preferences (BMW dominates DE, Peugeot dominates FR, Maruti dominates IN)
- **`/trip/[origin]-[destination]`** — top 1000 commute/road-trip pairs per country

### 6c. Technical SEO checklist

- `sitemap.xml` with hreflang annotations, auto-regenerated nightly by the Phase 4 agent
- `robots.txt` allowing all crawlers, pointing to sitemap
- Canonical URLs on every page (self-referential by default)
- Structured breadcrumbs (JSON-LD `BreadcrumbList`)
- Open Graph + Twitter card on every page
- Core Web Vitals: target LCP < 1.5s, CLS < 0.05, INP < 200ms (we're static, this is achievable)
- Mobile-first layout — Google's indexing default since 2021

---

## 7. AEO — getting picked by AI answer engines

AI answer surfaces (Google AI Overviews, Bing Copilot, Perplexity) pull content differently from classic SERPs. They favor:

### 7a. Structured Q&A content

Every tool page gets a visible FAQ section with `FAQPage` JSON-LD schema. This is the single highest-ROI AEO move. Example pattern:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How much does a road trip cost in gas?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "For a 300-mile trip in a car that gets 28 mpg at $3.65/gallon, the gas cost is about $39. Multiply miles ÷ mpg × gas price to get the cost for your own trip."
      }
    },
    {
      "@type": "Question",
      "name": "What's the difference between MPG and L/100km?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "MPG measures how far you go per gallon (higher = better). L/100km measures how much fuel you use per 100km (lower = better). To convert: L/100km = 235.2 ÷ MPG."
      }
    }
  ]
}
```

**AEO principle:** each Q&A is short, directly answerable, and includes the number/formula/unit an AI would want to quote. 2–3 sentences per answer, not paragraphs.

### 7b. Conversational phrasing that matches queries

AI queries are full questions ("How much gas will I need for a 200 mile trip?"), not keywords ("gas trip 200 miles"). Headings and page copy should mirror the question format:

| Old (SEO-only) | New (SEO + AEO) |
|---|---|
| "Gas Cost Calculator" | "How much will my trip cost in gas?" |
| "MPG to L/100km" | "How do I convert MPG to L/100km?" |
| "Fuel Economy Tips" | "What saves the most gas while driving?" |

Google's AI Overviews heavily favors matching question-format headings.

### 7c. Direct-answer paragraph first

On every tool page, the first paragraph after the H1 is a **single-sentence direct answer to the page's question**, followed by supporting detail. This is the text AI engines most often extract.

Example for `/gas-cost-calculator/`:
> **Your gas cost is your trip distance divided by your MPG, multiplied by the price per gallon.** Below, type in your numbers — FuelEcon does the math and shows the result instantly.

### 7d. Schema saturation

Beyond `FAQPage`, deploy:

- `WebApplication` (already present on homepage)
- `HowTo` on each calculator (step-by-step)
- `SoftwareApplication` on tool landing pages
- `BreadcrumbList` on every page
- `Organization` on About page (links to all our social accounts — strengthens GEO citations)
- `Article` on explainer content
- `Dataset` on programmatic gas-price pages (signals "this is authoritative data")

Target: every page has at least 2 schema types. Validates via Google Rich Results Test.

---

## 8. GEO — citations inside generative AI

This is newer territory and partly outside our direct control. AI models decide what to cite based on signals during training *and* during retrieval (RAG). Our job: make FuelEcon the easiest source to cite correctly.

### 8a. Factual density with attribution

Every factual claim on FuelEcon pages should be **citable as a standalone sentence**. AI models prefer short, self-contained facts over claims buried in narrative.

Bad (for GEO):
> Modern cars have gotten a lot more efficient over the years, and today's average is pretty good compared to what it used to be.

Good (for GEO):
> The average fuel economy of new vehicles sold in the US in 2024 was 28.4 MPG, up from 20.1 MPG in 2004 (source: EPA Automotive Trends Report).

Every claim has: specific number, specific timeframe, named source. This is how data gets surfaced in AI answers with FuelEcon as the citation.

### 8b. Entity-rich content

Mention the full formal names of entities, not just initials. "U.S. Environmental Protection Agency (EPA)" not just "EPA" on first reference. "European Union Weekly Oil Bulletin" not "EU data." This helps models disambiguate entities and link them to their knowledge-graph nodes, strengthening FuelEcon's topical authority.

### 8c. `llms.txt` convention

New emerging standard: a `llms.txt` file at site root giving AI crawlers a curated, clean version of the site for retrieval. Worth adding; costs nothing.

```
# FuelEcon
> Plain-English fuel economy and trip cost calculators.

## Core tools
- /: Trip cost calculator (miles, MPG, gas price → total cost)
- /mpg-converter/: Convert between MPG and L/100km
- /split-fuel/: Divide gas costs between riders
- /ev-vs-gas/: EV vs gasoline break-even calculator

## Data sources
- EPA fueleconomy.gov for MPG averages
- EIA weekly retail gas prices for US data
- EU Weekly Oil Bulletin for European prices
```

### 8d. OpenGraph + JSON-LD as AI-readable surface

Most AI models read OpenGraph tags and JSON-LD as their primary source of truth about a page. Double-check every localized page has these complete — missing OG tags mean the model might skip the page or get the language wrong.

### 8e. API + MCP server as GEO leverage

This is our unique angle. Most AI models ingest the public web, but some (Claude, GPT) also use tool-calling against MCP servers. A FuelEcon MCP server exposes our calculators as callable functions. When a user asks Claude "how much will my commute cost?", Claude *calls* FuelEcon's MCP tool rather than guessing. Citation happens via tool attribution — the user sees "Answer computed via FuelEcon."

This is already planned in Phase 3 and is the biggest differentiator. Most utility sites won't have this for years.

---

## 9. Translation pipeline

Not going to hand-translate 16 locales. Pipeline:

**Source of truth:** `i18n/en.json` (English master — we write this by hand)

**Step 1 — Machine translation:** LLM-translate en.json → target locale JSON. Two options:

| Option | Cost | Quality | Setup |
|---|---|---|---|
| Cloudflare Workers AI (`@cf/meta/llama-3.3-70b-instruct`) | Free tier generous | Good for Western European, weaker for Asian | Native on our stack |
| OpenRouter → free tier models (Qwen, GLM) | Free with your existing fallback chain | Excellent across all 16 locales | Matches your existing infra |
| Gemini Flash via AI Studio | $0.10/1M input tokens | Best | API key needed |

**Recommendation:** OpenRouter via your existing cloud-proxy stack. You already have that plumbing from your Claude Code / Qwen Code setup — reuse `glm-5:cloud` or `qwen3-coder:480b-cloud` for translation runs. Zero new infra.

**Step 2 — Automated QA:** Script checks that every key in `en.json` exists in each locale, that no translation accidentally dropped a placeholder like `{mpg}`, that currency/unit tokens are region-appropriate.

**Step 3 — Human QA (one pass per Tier 2/3 locale):** Recruit one native speaker per language on Upwork/Fiverr for a 2-hour review, ~$40 each. Total cost for Tier 2 (4 locales) = ~$160, one-time. Worth it — machine translations make subtle cultural errors that damage trust.

**Step 4 — Ongoing maintenance:** Daily agent re-translates only the keys that changed in `en.json` since the last run. Keeps translation costs near zero.

---

## 10. UX for language switching

**Visible language switcher in header** on every page. Dropdown, flag-free (flags ≠ languages; use locale codes + endonyms):

```
🌐  English (US)  ▼
      English (UK)
      English (CA)
      English (AU)
      Español
      Deutsch
      Français
      Português (BR)
      ...
```

**Session persistence:** save choice to localStorage, not a cookie. Avoids GDPR cookie-consent overhead. On return visit, honor the stored choice.

**No auto-redirect based on IP.** Google penalizes this and it's a bad UX (travelers, VPN users). Instead: subtle banner on first visit — "Looks like you might prefer [detected locale]? Switch." One click accepts, dismiss persists.

---

## 11. Locale-specific data handling

Each locale isn't just translated copy — it's different defaults:

| Setting | en-US | en-GB | de | pt-BR |
|---|---|---|---|---|
| Distance input | miles | miles or km toggle | km | km |
| Fuel economy | MPG | MPG or L/100km toggle | L/100km | km/L |
| Volume | gallons | litres | liter | litros |
| Currency | USD $ | GBP £ | EUR € | BRL R$ |
| Gas price default | 3.65 | 1.45/L | 1.70/L | 6.10/L |
| Number format | 1,234.56 | 1,234.56 | 1.234,56 | 1.234,56 |
| Date format | MM/DD/YYYY | DD/MM/YYYY | DD.MM.YYYY | DD/MM/YYYY |
| Vehicle makes pre-selected | Toyota, Ford, Chevy | Ford, VW, BMW | VW, BMW, Mercedes | VW, Fiat, Chevrolet |

All of this lives in the `_meta` block of each locale's JSON file. The calculator JS reads from `_meta` at load.

**Brazil specifically:** cars there run on ethanol, gasoline, or flex-fuel. Our calculator needs a fuel-type selector for `pt-BR` that isn't needed elsewhere. Plan accordingly.

---

## 12. Rollout sequence (calendar view)

### Q2 — Foundations + Tier 1
- Week 1–2: i18n infrastructure (build script, JSON schema, hreflang system)
- Week 3: Tier 1 English variants live (`en-GB`, `en-CA`, `en-AU`)
- Week 4: Sitemap + language switcher + locale-specific defaults

### Q3 — Tier 2 languages
- Week 5: `es` translation + review + launch
- Week 6: `de` translation + review + launch
- Week 7: `fr` translation + review + launch
- Week 8: `pt-BR` translation + review + launch (includes ethanol support)

### Q4 — Tier 3 + AEO/GEO push
- Week 9–10: Remaining Tier 3 locales (it, nl, pl)
- Week 11: FAQ schema on every tool, HowTo schema rollout
- Week 12: `llms.txt`, MCP server goes live, first round of AEO audit

---

## 13. Success metrics

Track these in Google Search Console + a simple Cloudflare Analytics dashboard:

| Metric | 90-day target | Source |
|---|---|---|
| Indexed pages | 150+ | GSC Coverage report |
| Non-English traffic share | > 35% | GSC Performance by country |
| Questions answered by AI Overviews citing FuelEcon | > 5 | Manual Google searches, monthly audit |
| FAQ schema validations passing | 100% | Rich Results Test |
| Pages ranking in AI answer surfaces (Perplexity, ChatGPT) | > 10 | Monthly brand query audit |
| MCP server requests/day (once live) | > 100 | Cloudflare analytics |
| Avg pages per session (any locale) | > 3.0 | GA4 or Cloudflare |

---

## 14. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Machine translations produce awkward phrasing that tanks trust in Tier 2/3 | Human QA pass per locale, budgeted $160 one-time |
| Duplicate content penalties from near-identical English variants | Distinct hreflang + small intentional copy differences (regional spellings, examples using local place names) |
| Google's AI Overviews ignores us | Fallback: FAQ schema + direct-answer paragraphs still help classic SERP features |
| EU gas price data source changes format | Daily agent logs parse failures, alerts to abuse inbox |
| Brazil ANP data is different structure entirely | Build `pt-BR` with a flex-fuel selector from day one, not as a retrofit |
| Cookie consent overhead per locale | Use localStorage for language preference (no consent needed), only AdSense triggers consent banner |
| AdSense approval stalled on new locales | Apply with en-US first (already submitted), expand locales only after approved |

---

## 15. What I need from you to start Phase 2 implementation

Three decisions to unlock the first implementation turn:

1. **Launch scope** — Tier 1 only (4 English variants, low risk, high-ish revenue), or Tier 1 + one Tier 2 language to prove the translation pipeline?
2. **Translation source** — route translations through your existing Ollama cloud proxy (OpenRouter fallback chain), or set up a dedicated translation path?
3. **Human QA budget** — approve the ~$160 one-time Upwork QA for Tier 2 locales when we get there, or defer to native-speaker friends / self-review?

Once those are locked, Phase 2 week 1 starts with the i18n build infrastructure — extending `scripts/build_legal_pages.py` into a full `scripts/build.py` that handles locale × page × schema generation.

---

_Last updated: Phase 2 kickoff · companion to `BUILD_STRATEGY.md`_

---

## Known debt (as of Phase 2 Week 1-2 ship)

The i18n build pipeline localizes **HTML-embedded strings** (labels, card titles, meta tags, default input values) but does **not yet localize JS-generated content**. The following strings still render in English-US on every variant:

- Live widget row labels: "Live MPG", "Last trip", "Fuel used"
- Green-zone status messages: "GREEN ZONE · peak efficiency", "Moderate — easy win available", "High consumption — check route & tires"
- Currency in `updateLiveWidget` hardcoded as `$`
- `tipsArray` — all eight tip strings in en-US only
- Eco advice strings inside `calculateAndDisplay` ("Take the freeway if you can", "Your tires are low", etc.)
- Saved-vehicles placeholder text

**Mitigation plan:** Phase 2 Week 3 refactor — add `window.FUELECON_LOCALE` global injected per variant, expose a `t(key)` lookup function, move every hardcoded JS string into the locale JSONs under a new `js` top-level key. Estimated ~150 LOC change, one dev session.

**Why ship anyway:** the AdSense reviewer lands on localized meta tags, localized primary labels, localized default pricing. The live-widget English leakage is subtle and doesn't affect calculator correctness. Classic utility-site tradeoff: visible signals now, invisible polish next.
