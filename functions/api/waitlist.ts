interface Env {
  DB: D1Database;
}

export const onRequestPost: PagesFunction<Env> = async (context) => {
  try {
    const { email, locale, source } = await context.request.json() as { 
      email: string; 
      locale?: string; 
      source?: string; 
    };

    if (!email || !email.includes('@')) {
      return new Response(JSON.stringify({ error: 'Invalid email' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const { DB } = context.env;
    
    // Check if D1 is bound
    if (!DB) {
      console.error('D1 Database "DB" is not bound.');
      return new Response(JSON.stringify({ error: 'Database connection failed' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    await DB.prepare(
      'INSERT OR IGNORE INTO waitlist (email, locale, source) VALUES (?, ?, ?)'
    )
      .bind(email, locale || 'unknown', source || 'direct')
      .run();

    return new Response(JSON.stringify({ success: true }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: (err as Error).message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
