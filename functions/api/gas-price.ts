interface Env {
  DB: D1Database;
}

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const { searchParams } = new URL(context.request.url);
  const region = searchParams.get('region'); // e.g. 'US-CA', 'US-AVG'

  if (!region) {
    return new Response(JSON.stringify({ error: 'Missing region parameter' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  try {
    const { DB } = context.env;
    
    if (!DB) {
      return new Response(JSON.stringify({ error: 'Database not bound' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const priceRecord = await DB.prepare(
      "SELECT price, currency, updated_at FROM gas_prices_cache WHERE region_code = ?"
    )
      .bind(region)
      .first<{ price: number; currency: string; updated_at: string }>();

    if (!priceRecord) {
      return new Response(JSON.stringify({ error: 'Region not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response(JSON.stringify(priceRecord), {
      headers: { 
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=3600' // Cache for 1 hour at edge
      },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: (err as Error).message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
