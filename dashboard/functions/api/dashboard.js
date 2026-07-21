export async function onRequest(context) {
  const R2_BASE = 'https://hermes-main-media.devtoy.xyz/fund-system';
  
  try {
    const resp = await fetch(`${R2_BASE}/dashboard.json`, {
      cf: { cacheTtl: 60 }
    });
    if (!resp.ok) {
      return new Response(JSON.stringify({ error: 'Data not available' }), {
        status: 503,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      });
    }
    const data = await resp.json();
    return new Response(JSON.stringify(data), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  }
}
