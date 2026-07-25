export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) return res.status(500).json({ error: 'Chua cau hinh API key' });

  try {
    const { parts } = req.body;

    // Dung dung endpoint cua google-genai SDK (v1alpha = moi nhat, ho tro gemini-3.x)
    const model = 'gemini-2.0-flash-lite';
    const url = `https://generativelanguage.googleapis.com/v1alpha/models/${model}:generateContent?key=${apiKey}`;

    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ role: 'user', parts }],
        generationConfig: { maxOutputTokens: 1500, temperature: 0.3 }
      })
    });

    const data = await r.json();
    if (data.error) return res.status(500).json({ error: data.error.message });

    let text = '';
    try { text = data.candidates[0].content.parts[0].text || ''; } catch(e) {}
    if (!text) return res.status(500).json({ error: 'Khong co phan hoi tu AI' });
    return res.status(200).json({ text });

  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
