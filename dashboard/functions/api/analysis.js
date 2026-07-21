export async function onRequest(context) {
  const R2_BASE = 'https://hermes-main-media.devtoy.xyz/fund-system';
  try {
    const resp = await fetch(`${R2_BASE}/analysis-latest.json`, {
      cf: { cacheTtl: 60 }
    });
    const data = resp.ok ? await resp.json() : [];
    return new Response(JSON.stringify(data), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  } catch (e) {
    return new Response(JSON.stringify([]), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  }
}
