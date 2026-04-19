interface Env {
  STRIPE_SECRET_KEY: string;
  STRIPE_PRODUCT_ID: string;
  SITE_URL: string;
}

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { STRIPE_SECRET_KEY, STRIPE_PRODUCT_ID, SITE_URL } = context.env;

  if (!STRIPE_SECRET_KEY || !STRIPE_PRODUCT_ID) {
    return new Response(JSON.stringify({ error: 'Stripe configuration missing' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  try {
    // We use the Stripe REST API directly to avoid large node_modules in the worker
    const params = new URLSearchParams();
    params.append('success_url', `${SITE_URL || 'https://fuelecon.pages.dev'}/?premium=success`);
    params.append('cancel_url', `${SITE_URL || 'https://fuelecon.pages.dev'}/`);
    params.append('mode', 'payment');
    params.append('line_items[0][price]', STRIPE_PRODUCT_ID); // In Stripe, Product ID for checkout is usually the Price ID
    params.append('line_items[0][quantity]', '1');

    const response = await fetch('https://api.stripe.com/v1/checkout/sessions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${STRIPE_SECRET_KEY}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    });

    const session: any = await response.json();

    if (session.error) {
      throw new Error(session.error.message);
    }

    return new Response(JSON.stringify({ url: session.url }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: (err as Error).message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
