export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const days = url.searchParams.get('days') || '30';
  
  if (!env.DB) {
    return new Response(JSON.stringify([]), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  }
  
  try {
    const { results } = await env.DB.prepare(
      `SELECT date, fund_code, fund_name, estimated_value, profit_pct
       FROM portfolio_snapshots
       WHERE date >= date('now', '-' || ? || ' days')
       ORDER BY date`
    ).bind(days).all();
    return new Response(JSON.stringify(results), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  } catch (e) {
    return new Response(JSON.stringify([]), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  }
}
