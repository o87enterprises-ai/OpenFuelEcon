# FuelEcon — Build Strategy

> Plain-English fuel economy tools · utility-site business model · Cloudflare-native
> Owner: o87Dev / TruegleAi · Repo: `github.com/o87enterprises-ai/fuelecon`

---

## 1. The thesis in one paragraph

FuelEcon is a utility-site portfolio, not a single calculator. The site gets one visitor because they searched "gas cost for road trip" — and that visitor sees four more tools they didn't know they needed (MPG converter, fuel split calculator, EV break-even, state gas price lookup). Google display ads monetize every page view. A daily cron agent keeps programmatic pages (gas prices by state, MPG data by make/model) fresh without us lifting a finger. The moat is plain-English explainers ("for Dummies" voice) that Google rewards for long-tail queries where big calculator sites feel robotic.

---

## 2. What the YouTube video proved, applied to FuelEcon

| Video insight | FuelEcon application |
|---|---|
| Utility sites earn via RPM on page views — no click required | Target 3–4 pages per session via internal links between our fuel tools |
| $3–12 RPM realistic for tier-1 traffic | 100k monthly sessions × 3 pages × $6 RPM ≈ $1,800/mo baseline target |
| AdSense demands legal pages + substantial content before approval | Footer already has `/privacy` `/terms` `/about` `/disclosure` stubs — Batch 3 fills them |
| Portfolio beats single-tool (5 tools × $200 > 1 tool × $500) | 6 sub-tools planned — list below |
| Target queries where Google shows NEW sites (signals established sites aren't answering) | Use Clearer or Ahrefs for low-KD fuel queries; Phase 2 deliverable |
| Evergreen, zero maintenance | Daily agent keeps content fresh; tool logic never expires |
| Remix/template referrals (Horizons) | Our equivalent: open-source the repo, MCP server as a lead magnet for `o87enterprises-ai` brand |

---

## 3. Updated phased roadmap

### Phase 1 — Foundation (in progress)
- **Batch 1 ✅** rebranded `index.html`, palette applied, footer legal stubs, SEO meta foundation
- **Batch 2** repo scaffold (`/public`, `/functions`, `/mcp`, `/agent`), `wrangler.toml`, PWA manifest, service worker, favicon
- **Batch 3** legal pages (`/about` `/privacy` `/terms` `/disclosure`), FAQ section with `FAQPage` schema, `HowTo` schema on calculator

### Phase 2 — SEO / AEO / GEO layer
- Sitemap + robots.txt + canonical links
- Schema.org: `WebApplication`, `FAQPage`, `HowTo`, `Article` (on explainer pages)
- AEO: conversational Q&A blocks ("How much does a road trip cost?"), clear one-sentence answers
- GEO: citation-ready facts with source attribution (EIA for gas prices, EPA for MPG data)
- Programmatic pages:
  - `/gas-prices/{state}` — 50 US states, daily-refreshed
  - `/mpg/{make}/{model}/{year}` — EPA fuelecon.gov dataset
  - `/trip/{from}-{to}` — dynamically generated for top 1000 common routes
- Keyword research output → first 20 programmatic pages prioritized by KD < 10

### Phase 3 — Backend, API, MCP
- Cloudflare Worker routes:
  - `GET /api/gas-price/:state` — cached EIA data
  - `POST /api/trip/calculate` — server-side version of client calc
  - `GET /api/mpg/:make/:model` — EPA lookup
  - `POST /api/vehicles` / `GET /api/vehicles/:userId` — D1 synced garage
- D1 schema: `vehicles`, `trips`, `gas_prices_cache`, `mpg_lookup_cache`
- MCP server (remote, at `mcp.fuelecon.com`):
  - `tool: calculate_trip_cost(distance, mpg, gas_price, route_type)`
  - `tool: get_gas_price(state)`
  - `tool: lookup_vehicle_mpg(make, model, year)`
  - Positions FuelEcon as a developer-friendly data source — lead magnet for o87Dev

### Phase 4 — Agentic daily maintenance
- Cloudflare Worker with `scheduled` handler, triggered at `0 6 * * *` UTC
- Tasks per run:
  1. Fetch EIA weekly retail gas prices, upsert to D1
  2. Regenerate `/gas-prices/{state}` pages with fresh data + "updated today" badge
  3. Rotate homepage featured tip from `tipsArray` (or LLM-generated via Ollama cloud proxy)
  4. Crawl top 10 SERPs for our target keywords, flag rank changes
  5. Ping Google Indexing API on updated pages
  6. Send digest to ops inbox (format: `o87-marketing-ops` worker pattern)
  7. Weekly: LLM generates one new explainer article via cloud Ollama
- Uses same `ANTHROPIC_BASE_URL=http://localhost:8000` pattern via tunneled proxy for local runs; `workers.ai` for production

### Phase 5 — Monetization + launch
- AdSense application (only after Phases 2–4 complete → gives us content depth for approval)
- Google Search Console + Bing Webmaster
- Submit sitemap, request indexing on 20 priority URLs
- PWA install prompt (day-2 return visitors)
- Social: one-off launch post on r/cars, r/fuelsaving, r/roadtrip
- iframe README embed live

---

## 4. Tool portfolio — the 6 planned micro-tools

| Tool | URL | Target query | KD target |
|---|---|---|---|
| Trip cost calculator (hub) | `/` | "fuel cost calculator road trip" | < 15 |
| MPG ⇄ L/100km converter | `/mpg-converter` | "mpg to l/100km calculator" | < 10 |
| Fuel cost split calculator | `/split-fuel` | "split gas money calculator roommates" | < 8 |
| EV vs gas break-even | `/ev-vs-gas` | "is an ev worth it calculator" | < 15 |
| Lease vs buy fuel factor | `/lease-vs-buy-fuel` | "lease vs buy fuel cost comparison" | < 5 |
| Commute cost weekly/monthly | `/commute-cost` | "how much does my commute cost" | < 12 |

Each tool is a separate page but shares header/footer/nav with the hub. Internal linking: every tool footer shows "You might also like" with 2 sibling tools. This is how we get 3+ pages per session.

---

## 5. AdSense approval checklist (hard requirements from the video)

Before submitting, site must have:
- [x] Real domain (not `*.pages.dev` subdomain) — register `fuelecon.com` or `.app`
- [ ] Privacy policy (GDPR/CCPA-aware)
- [ ] Terms of service
- [ ] Cookie/ads disclosure page
- [ ] Contact page (email at minimum)
- [ ] "About" page with real human ownership signals
- [ ] ≥ 2 working tools (more is better)
- [ ] Each tool has 300+ words of unique explainer content
- [ ] Mobile responsive ✅ (already done)
- [ ] SSL (automatic on Cloudflare Pages)
- [ ] Site navigable — header nav + footer nav
- [ ] 30 days of organic traffic is preferred but not required

---

## 6. Revenue model — FuelEcon-specific math

Following the video's framework:

```
Visitors × pages_per_session × (RPM / 1000) = monthly revenue
```

| Scenario | Monthly visitors | PPS | RPM | Revenue |
|---|---|---|---|---|
| Conservative (month 3) | 10,000  | 2.2 | $4  | $88      |
| Realistic (month 6)    | 50,000  | 3.0 | $6  | $900     |
| Target (month 12)      | 200,000 | 3.5 | $7  | $4,900   |
| Stretch (month 24)     | 800,000 | 4.0 | $9  | $28,800  |

Fuel topics attract high-RPM advertisers (auto insurance, auto loans, gas cards, EV brands) — the $6–9 RPM range is defensible for US traffic.

---

## 7. Repo layout (Batch 2 will scaffold)

```
fuelecon/
├── public/                    # static site (served by Cloudflare Pages)
│   ├── index.html             # ✅ hub / trip calculator
│   ├── mpg-converter/
│   ├── split-fuel/
│   ├── ev-vs-gas/
│   ├── about/
│   ├── privacy/
│   ├── terms/
│   ├── manifest.json
│   ├── sw.js                  # service worker (PWA)
│   ├── robots.txt
│   └── sitemap.xml
├── functions/                 # Cloudflare Pages Functions (Workers)
│   ├── api/
│   │   ├── gas-price/[state].ts
│   │   ├── trip/calculate.ts
│   │   └── vehicles/[[path]].ts
│   └── _middleware.ts         # auth, rate limit, CORS
├── agent/                     # daily maintenance cron Worker
│   ├── wrangler.toml
│   └── src/index.ts
├── mcp/                       # MCP server (remote)
│   ├── wrangler.toml
│   └── src/index.ts
├── schema/                    # D1 migrations
│   └── 0001_init.sql
├── scripts/
│   └── generate-programmatic-pages.ts
├── wrangler.toml              # root Pages config
├── README.md                  # iframe embed of live site
└── BUILD_STRATEGY.md          # this file
```

---

## 8. Batch 2 preview (next turn)

- `wrangler.toml` + Cloudflare Pages config
- `manifest.json` + `sw.js` for home-screen installability
- SVG favicon + apple-touch-icon
- Repo README with iframe embed placeholder
- `.gitignore`, basic GitHub Actions CI stub

Then Batch 3 finishes Phase 1 with legal pages + FAQ schema.

---

_Last updated: Batch 1 · Phase 1_
