/**
 * DOLIGO 채팅 API - Cloudflare Worker
 * POST /api/chat → Gemini API 프록시
 */

const SYSTEM_PROMPT = `당신은 DOLIGO의 AI 전문 비서이자 전략기획실 최고 전문가입니다.
사용자의 지원과제(정부사업, R&D, 과제 신청 등) 작성 요청에 대해:
1. 사용자의 의도와 맥락을 정확히 이해합니다.
2. 전문 비서처럼 핵심 요구사항을 명확히 정리합니다.
3. 전략기획실 전문가 관점으로 보완점과 제안을 제시합니다.
4. 사용자가 원하는 정확한 니즈를 파악해 문서 작성에 반영할 수 있도록 구체화합니다.
한국어로 응답하며, 친절하고 전문적인 톤을 유지합니다.

[중요] 응답 마지막에 반드시 새 줄 두 개 후 다음 형식으로 이 대화에서 문서 작성에 유용한 핵심 키워드 1~3개를 추출해 적어주세요:
___KEYWORDS___: 키워드1, 키워드2, 키워드3
(키워드가 없거나 추출할 수 없으면 ___KEYWORDS___: 만 적어주세요)`;

function parseKeywords(text) {
  const match = text.match(/___KEYWORDS___:\s*(.+)/s);
  if (!match) return [];
  const raw = match[1].trim();
  if (!raw) return [];
  return raw.split(/[,，、\n]+/).map((k) => k.trim()).filter(Boolean).slice(0, 5);
}

function stripKeywords(text) {
  return text.replace(/\n*\s*___KEYWORDS___:.*$/s, "").trim();
}

async function fetchUrlContent(url) {
  if (!url || !url.trim().startsWith("http")) return "";
  try {
    const res = await fetch(url.trim(), {
      headers: { "User-Agent": "Mozilla/5.0 (compatible; DOLIGO/1.0)" },
    });
    if (!res.ok) return "";
    const html = await res.text();
    const text = html
      .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, "")
      .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, "")
      .replace(/<[^>]+>/g, " ")
      .replace(/\s+/g, " ")
      .trim();
    return text.slice(0, 15000);
  } catch {
    return "";
  }
}

async function callGemini(apiKey, prompt, imageParts = []) {
  const model = "gemini-2.5-pro";
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;

  const parts = [...imageParts, { text: prompt }];

  const body = {
    contents: [{ role: "user", parts }],
    generationConfig: { temperature: 0.7, maxOutputTokens: 8192 },
  };

  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Gemini API error: ${res.status}`);
  }

  const data = await res.json();
  const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || "";
  return text;
}

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Access-Control-Max-Age": "86400",
};

export default {
  async fetch(request, env, ctx) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS });
    }

    const url = new URL(request.url);
    if (url.pathname === "/health" || url.pathname === "/api/health") {
      return new Response(JSON.stringify({ status: "ok" }), {
        status: 200,
        headers: { "Content-Type": "application/json", ...CORS },
      });
    }
    if (url.pathname !== "/api/chat" || request.method !== "POST") {
      return new Response(JSON.stringify({ detail: "Not Found" }), {
        status: 404,
        headers: { "Content-Type": "application/json", ...CORS },
      });
    }

    const apiKey = env.GEMINI_API_KEY || env.BEMINI_API_KEV;
    if (!apiKey || !apiKey.trim()) {
      return new Response(
        JSON.stringify({ detail: "GEMINI_API_KEY가 설정되지 않았습니다. Worker Secrets에서 설정하세요." }),
        { status: 503, headers: { "Content-Type": "application/json", ...CORS } }
      );
    }

    try {
      const formData = await request.formData();
      const messagesStr = formData.get("messages");
      const urlContextInput = formData.get("url") || "";

      if (!messagesStr) {
        return new Response(JSON.stringify({ detail: "messages 필드가 필요합니다." }), {
          status: 400,
          headers: { "Content-Type": "application/json", ...CORS },
        });
      }

      let messages;
      try {
        messages = JSON.parse(messagesStr);
      } catch {
        return new Response(JSON.stringify({ detail: "messages 형식 오류" }), {
          status: 400,
          headers: { "Content-Type": "application/json", ...CORS },
        });
      }

      let urlContext = "";
      if (urlContextInput && urlContextInput.trim().startsWith("http")) {
        urlContext = await fetchUrlContent(urlContextInput.trim());
      }

      let convText = "";
      if (urlContext) {
        convText += `[참고: 지원과제 관련 URL 맥락]\n${urlContext.slice(0, 8000)}\n\n`;
      }
      for (const m of messages) {
        const role = m.role === "user" ? "사용자" : "AI";
        convText += `${role}: ${m.content || ""}\n\n`;
      }
      const prompt = `${SYSTEM_PROMPT}\n\n---\n\n대화 내용:\n${convText}\nAI:`;

      const raw = await callGemini(apiKey, prompt, []);
      const keywords = parseKeywords(raw);
      const reply = stripKeywords(raw) || "응답을 생성하지 못했습니다.";

      return new Response(JSON.stringify({ reply, keywords }), {
        status: 200,
        headers: { "Content-Type": "application/json", ...CORS },
      });
    } catch (e) {
      const msg = String(e?.message || e);
      const status = msg.includes("API_KEY") || msg.includes("invalid") ? 503 : 500;
      return new Response(JSON.stringify({ detail: msg }), {
        status,
        headers: { "Content-Type": "application/json", ...CORS },
      });
    }
  },
};
