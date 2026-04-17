# ⛽ FuelEcon · Fuel Economy for Dummies

> Plain-English gas cost calculator. Type your car, your trip, get your real cost and the easy tweaks that save fuel. No mpg maths degree required.

[![Live Demo](https://img.shields.io/badge/Live_Demo-fuelecon.pages.dev-1A5F3F?style=for-the-badge&logo=cloudflare&logoColor=white)](https://fuelecon.pages.dev)
[![PWA Ready](https://img.shields.io/badge/PWA-Installable-B8E23A?style=for-the-badge)](https://fuelecon.pages.dev/manifest.json)
[![MIT License](https://img.shields.io/badge/License-MIT-F4A52D?style=for-the-badge)](./LICENSE)
[![Made by o87Dev](https://img.shields.io/badge/Made_by-o87Dev-1B2430?style=for-the-badge)](https://github.com/o87enterprises-ai)

<p align="center">
  <a href="https://fuelecon.pages.dev">
    <img src="./public/icon-512.png" alt="FuelEcon" width="140"/>
  </a>
</p>

<p align="center">
  <strong><a href="https://fuelecon.pages.dev">→ Open the live app</a></strong>
</p>

---

## 🪟 Live embed

> The `<iframe>` below renders on embed-friendly platforms (dev.to, Notion, most docs sites). GitHub's README sanitizer strips iframes for security — click the preview above to open the full site instead.

<iframe
  src="https://fuelecon.pages.dev"
  width="100%"
  height="720"
  frameborder="0"
  loading="lazy"
  allowfullscreen
  style="border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.1); border: 1px solid #ece3cf;"
  title="FuelEcon · live demo"
  sandbox="allow-scripts allow-same-origin allow-popups allow-forms">
</iframe>

<details>
<summary>📋 Embed code (copy for your own site)</summary>

```html
<iframe
  src="https://fuelecon.pages.dev"
  width="100%"
  height="720"
  frameborder="0"
  loading="lazy"
  style="border-radius: 16px;"
  title="FuelEcon">
</iframe>
```

</details>

---

## What FuelEcon does

FuelEcon is a utility-site portfolio of fuel-economy tools, each a dedicated page, all cross-linked. One visit answers the query the user came for — and surfaces three more tools they didn't know they needed.

| Tool | Status | Path |
|---|---|---|
| 🚗 Trip cost calculator (hub) | ✅ Live | `/` |
| 🔄 MPG ⇄ L/100km converter | 🛠 Phase 2 | `/mpg-converter` |
| 💵 Split fuel cost | 🛠 Phase 2 | `/split-fuel` |
| ⚡ EV vs gas break-even | 🛠 Phase 2 | `/ev-vs-gas` |
| 🏦 Lease vs buy fuel factor | 🛠 Phase 2 | `/lease-vs-buy-fuel` |
| 🕐 Commute cost weekly/monthly | 🛠 Phase 2 | `/commute-cost` |

---

## ✨ Features in v0.1

- **Quick vehicle picker** — 15 makes × 100 engine/drivetrain combinations, EPA-grounded MPG averages. No mpg sheet required.
- **Live trip calculator** — distance slider, route type (highway/backroads), tire pressure modifier, effective-MPG math
- **Live "green zone" widget** — real-time efficiency scoring
- **Offline-first PWA** — installable on iOS, Android, desktop. Works without signal.
- **Saved garage** — IndexedDB persistence for your cars (D1 sync coming in Phase 3)
- **Plain-English voice** — every blurb is written for humans, not spec sheets

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  fuelecon.pages.dev                          │
│   ┌─────────────┐    ┌────────────────┐    ┌─────────────┐  │
│   │  Static UI  │←──→│ Pages Functions│←──→│ Cloudflare  │  │
│   │  (public/)  │    │   (functions/) │    │  D1 + KV    │  │
│   └─────────────┘    └────────────────┘    └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
              │                 │
              │                 │
         ┌────▼────┐       ┌────▼─────────┐
         │   PWA   │       │  MCP Server  │
         │ offline │       │  (for AI     │
         │ install │       │  assistants) │
         └─────────┘       └──────────────┘

         ┌─────────────────────────────────┐
         │  Daily Maintenance Agent        │
         │  (separate Cron Worker)         │
         │  - EIA gas price refresh        │
         │  - Programmatic page regen      │
         │  - SEO audit + indexing ping    │
         └─────────────────────────────────┘
```

---

## 🚀 Quickstart

### Prerequisites
- Node 18+
- A Cloudflare account (free tier works)
- `wrangler` CLI authenticated (`npx wrangler login`)

### Local development
```bash
git clone https://github.com/o87enterprises-ai/fuelecon.git
cd fuelecon
npm install
npm run dev
# → http://localhost:8788
```

### Deploy to Cloudflare Pages

**Option A — Native GitHub integration (recommended, zero-config):**
1. Go to Cloudflare dashboard → Pages → Create project → Connect to Git
2. Select `o87enterprises-ai/fuelecon`, branch `main`
3. Build command: *(leave empty)*
4. Build output directory: `public`
5. Save → every push to `main` auto-deploys

**Option B — CLI manual deploy:**
```bash
npm run deploy
```

---

## 📦 Repo layout

```
fuelecon/
├── public/                 # static site (served by Cloudflare Pages)
│   ├── index.html          # hub / trip calculator
│   ├── manifest.json       # PWA manifest
│   ├── sw.js               # service worker (offline-first)
│   ├── favicon.svg         # brand mark (vector)
│   ├── icon-192.png        # PWA icons (any + maskable variants)
│   ├── icon-512.png
│   ├── apple-touch-icon.png
│   └── ...
├── functions/              # Cloudflare Pages Functions (Phase 3)
│   └── api/
│       └── (coming)
├── mcp/                    # MCP server for AI assistants (Phase 3)
├── agent/                  # daily cron Worker (Phase 4)
├── schema/                 # D1 migrations (Phase 3)
├── wrangler.toml           # Cloudflare config
├── package.json
├── README.md               # this file
└── BUILD_STRATEGY.md       # phased roadmap + revenue model
```

---

## 🗺 Roadmap

- **✅ Phase 1** — static site, rebrand, PWA, vehicle picker *(current)*
- **Phase 2** — SEO/AEO/GEO layer, 5 additional tools, programmatic pages
- **Phase 3** — Pages Functions API, Cloudflare D1, MCP server
- **Phase 4** — daily maintenance agent (cron Worker + LLM)
- **Phase 5** — AdSense monetization, custom domain, launch

Full plan in [`BUILD_STRATEGY.md`](./BUILD_STRATEGY.md).

---

## 🔌 API (Phase 3)

The REST API will be available at `/api/*` on the same domain (co-located Pages Functions — no CORS).

Planned endpoints:
```
GET  /api/gas-price/:state           # cached EIA weekly data
POST /api/trip/calculate             # server-side trip cost
GET  /api/mpg/:make/:model/:year     # EPA fueleconomy.gov lookup
GET  /api/vehicles/:userId           # synced garage (D1)
POST /api/vehicles                   # save a vehicle
```

API keys issued via a dev portal (coming). Free tier generous, paid tier for high-volume embedding.

---

## 🧠 MCP server (Phase 3)

Add FuelEcon to any MCP-compatible AI assistant (Claude Desktop, Claude Code, Cursor, etc.):

```json
{
  "mcpServers": {
    "fuelecon": {
      "url": "https://fuelecon-mcp.workers.dev/sse"
    }
  }
}
```

Tools exposed: `calculate_trip_cost`, `get_gas_price`, `lookup_vehicle_mpg`. The same logic as the REST API, but callable by AI agents as part of their workflows.

---

## 📜 License

MIT © o87Dev / o87enterprises-ai

---

<p align="center">
  <sub>Built with Cloudflare Pages · Powered by EPA fueleconomy.gov data · Made by <a href="https://github.com/o87enterprises-ai">@o87enterprises-ai</a></sub>
</p>
