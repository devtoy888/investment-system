export async function onRequest(context) {
  const url = new URL(context.request.url);
  const days = parseInt(url.searchParams.get('days') || '7', 10);
  const R2_BASE = 'https://hermes-main-media.devtoy.xyz/fund-system';
  
  try {
    const resp = await fetch(`${R2_BASE}/signals-resolved.jsonl`, {
      cf: { cacheTtl: 120 }
    });
    if (!resp.ok) return new Response(JSON.stringify([]), {
      headers: { 'Content-Type': 'application/json' }
    });
    
    const text = await resp.text();
    const cutoff = new Date(Date.now() - days * 86400000);
    const signals = text.trim().split('\n').filter(Boolean)
      .map(line => { try { return JSON.parse(line); } catch { return null; } })
      .filter(Boolean)
      .filter(s => new Date(s.publish_time || s.time || 0) >= cutoff)
      .slice(-50);
    
    return new Response(JSON.stringify(signals), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  } catch (e) {
    return new Response(JSON.stringify([]), {
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
