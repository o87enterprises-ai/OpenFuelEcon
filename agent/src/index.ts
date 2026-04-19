export interface Env {
  DB: D1Database;
  EIA_API_KEY: string;
}

export default {
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    console.log(`[Maintenance Agent] Run started at ${event.scheduledTime}`);

    // Task 1: Update Gas Prices from EIA
    ctx.waitUntil(updateGasPrices(env));

    // Task 2: (Optional) Ping Search Engines
    // ctx.waitUntil(pingSearchEngines(env));
  },

  // Also allow manual trigger via fetch if needed during dev
  async fetch(request: Request, env: Env): Promise<Response> {
    await updateGasPrices(env);
    return new Response("Maintenance tasks executed manually.");
  }
};

async function updateGasPrices(env: Env) {
  if (!env.EIA_API_KEY) {
    console.error("Missing EIA_API_KEY secret");
    return;
  }

  console.log("Fetching latest Weekly Retail Gasoline prices from EIA...");

  try {
    // EIA API v2: Weekly Retail Gasoline (National Average)
    // Series: EMM_EPMR_PTE_NUS_DPG (Regular Gasoline, All Formulations)
    const url = new URL("https://api.eia.gov/v2/petroleum/pri/gnd/data/");
    url.searchParams.set("api_key", env.EIA_API_KEY);
    url.searchParams.set("frequency", "weekly");
    url.searchParams.set("data[]", "value");
    url.searchParams.set("facets[series][]", "EMM_EPMR_PTE_NUS_DPG");
    url.searchParams.set("sort[0][column]", "period");
    url.searchParams.set("sort[0][direction]", "desc");
    url.searchParams.set("length", "1");

    const response = await fetch(url.toString());
    const result: any = await response.json();

    if (result.response && result.response.data && result.response.data.length > 0) {
      const latest = result.response.data[0];
      const price = parseFloat(latest.value);
      const date = latest.period;

      // Update D1 Cache for US-AVG
      await env.DB.prepare(
        "INSERT INTO gas_prices_cache (region_code, price, currency) VALUES (?, ?, ?) " +
        "ON CONFLICT(region_code) DO UPDATE SET price = excluded.price, updated_at = CURRENT_TIMESTAMP"
      )
        .bind("US-AVG", price, "USD")
        .run();
        
      console.log(`[Success] Updated US-AVG to $${price} (Reported for: ${date})`);
    } else {
      console.warn("EIA API returned empty data for the requested series.");
    }
  } catch (err) {
    console.error("EIA Update Failed:", err);
  }
}
