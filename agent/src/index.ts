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

  console.log("Fetching latest gas prices from EIA...");

  try {
    // EIA API v2 endpoint for Weekly Retail Gasoline Prices
    // This is a stub for the real API call structure
    const url = `https://api.eia.gov/v2/total-energy/data/?api_key=${env.EIA_API_KEY}&frequency=weekly&data[]=value&facets[series][]=RU_E_GAS_P_GAL_US`;
    
    const response = await fetch(url);
    const data: any = await response.json();

    if (data.response && data.response.data) {
      const latest = data.response.data[0];
      const price = parseFloat(latest.value);

      // Update D1 Cache
      await env.DB.prepare(
        "INSERT INTO gas_prices_cache (region_code, price, currency) VALUES (?, ?, ?) ON CONFLICT(region_code) DO UPDATE SET price = excluded.price, updated_at = CURRENT_TIMESTAMP"
      )
        .bind("US-AVG", price, "USD")
        .run();
        
      console.log(`Successfully updated US-AVG gas price to $${price}`);
    }
  } catch (err) {
    console.error("Failed to update gas prices:", err);
  }
}
