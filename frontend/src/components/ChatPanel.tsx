import { useState, useRef, useEffect } from "react";
import { VoiceInput } from "./VoiceInput";
import { Send } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  imageUrls?: string[];
}

interface ChatPanelProps {
  url: string;
  onSummaryChange: (summary: string) => void;
  onKeywordsExtracted?: (keywords: string[]) => void;
}

export function ChatPanel({ url, onSummaryChange, onKeywordsExtracted }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [attachedImages, setAttachedImages] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    requestAnimationFrame(() => {
      const el = scrollContainerRef.current;
      if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const sendMessage = async (text: string, images?: File[]) => {
    const t = text.trim();
    if (!t && (!images || images.length === 0)) return;

    const imageUrls: string[] = [];
    if (images?.length) {
      for (const f of images) {
        imageUrls.push(URL.createObjectURL(f));
      }
    }
    setMessages((m) => [...m, { role: "user", content: t || "(이미지)", imageUrls }]);
    setInputText("");
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("messages", JSON.stringify([...messages, { role: "user", content: t || "(이미지)" }]));
      if (url) formData.append("url", url);
      if (images?.length) {
        images.forEach((img) => formData.append("images", img));
      }

      const apiBase = (import.meta as { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL ?? "";
      const res = await fetch(`${apiBase}/api/chat`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const d = data as { detail?: string | { msg?: string }[] };
        let errMsg = res.statusText;
        if (d.detail) {
          errMsg = Array.isArray(d.detail) ? d.detail[0]?.msg ?? String(d.detail) : String(d.detail);
        }
        if (res.status === 404) {
          errMsg =
            "API를 찾을 수 없습니다. 백엔드를 실행했는지 확인하세요: cd backend && uvicorn app.main:app --port 8000";
        }
        throw new Error(errMsg || "API 오류");
      }
      const reply = (data as { reply?: string }).reply ?? "";
      if (!reply) throw new Error("응답이 비어 있습니다. API 키를 확인하세요.");

      const keywords = (data as { keywords?: string[] }).keywords ?? [];
      onSummaryChange(reply);
      if (keywords.length > 0 && onKeywordsExtracted) {
        onKeywordsExtracted(keywords);
      }
      setMessages((m) => [...m, { role: "assistant", content: reply }]);
    } catch (e) {
      const errMsg = e instanceof Error ? e.message : "응답을 받지 못했습니다.";
      setMessages((m) => [...m, { role: "assistant", content: `오류: ${errMsg}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[520px] bg-white/80 backdrop-blur rounded-2xl border border-slate-200/80 shadow-xl overflow-hidden">
      <div ref={scrollContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <p className="text-center text-slate-500 text-sm py-8">
            지원과제에 대해 무엇이든 물어보세요.
            <br />
            AI 전문 비서가 전략기획실 전문가처럼 답변합니다.
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2 ${
                m.role === "user"
                  ? "bg-sky-600 text-white"
                  : "bg-slate-100 text-slate-800"
              }`}
            >
              {m.imageUrls?.length ? (
                <div className="flex flex-wrap gap-2 mb-2">
                  {m.imageUrls.map((src, j) => (
                    <img key={j} src={src} alt="" className="max-w-24 max-h-24 object-cover rounded" />
                  ))}
                </div>
              ) : null}
              <p className="text-sm whitespace-pre-wrap">{m.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 rounded-2xl px-4 py-2">
              <span className="animate-pulse">...</span>
            </div>
          </div>
        )}
      </div>
      <div className="p-4 border-t border-slate-200/80">
        <VoiceInput
          value={inputText}
          onChange={setInputText}
          onSend={sendMessage}
          attachedImages={attachedImages}
          onAttachedImagesChange={setAttachedImages}
          disabled={loading}
        />
        <div className="mt-2 flex justify-end">
          <button
            onClick={() => sendMessage(inputText, attachedImages)}
            disabled={(!inputText.trim() && attachedImages.length === 0) || loading}
            className="flex items-center gap-2 px-4 py-2 bg-sky-600 text-white rounded-xl text-sm font-medium hover:bg-sky-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
            전송
          </button>
        </div>
      </div>
    </div>
  );
}
