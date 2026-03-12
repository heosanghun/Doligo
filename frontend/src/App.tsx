import { useState } from "react";
import { FileUpload } from "./components/FileUpload";
import { KeywordInput } from "./components/KeywordInput";
import { UrlInput } from "./components/UrlInput";
import { ChatPanel } from "./components/ChatPanel";
import { ProgressDisplay } from "./components/ProgressDisplay";
import { DownloadResult } from "./components/DownloadResult";

function App() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [keywords, setKeywords] = useState("");
  const [url, setUrl] = useState("");
  const [chatSummary, setChatSummary] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const handleStart = (id: string) => {
    setJobId(id);
  };

  const handleReset = () => {
    setJobId(null);
    setKeywords("");
    setUrl("");
    setChatSummary("");
    setFile(null);
  };

  const handleKeywordsExtracted = (newKeywords: string[]) => {
    if (newKeywords.length === 0) return;
    const existing = keywords
      .split(/[,，、\n]+/)
      .map((k) => k.trim())
      .filter(Boolean);
    const seen = new Set(existing.map((k) => k.toLowerCase()));
    const toAdd: string[] = [];
    for (const kw of newKeywords) {
      const k = kw.trim();
      if (k && !seen.has(k.toLowerCase())) {
        seen.add(k.toLowerCase());
        toAdd.push(k);
      }
    }
    if (toAdd.length > 0) {
      const combined = existing.length ? [...existing, ...toAdd] : toAdd;
      setKeywords(combined.join(", "));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-sky-50/30 to-indigo-50/40">
      <header className="relative overflow-hidden border-b border-slate-200/60 bg-white/80 backdrop-blur-xl shadow-sm">
        <div className="absolute inset-0 bg-gradient-to-r from-sky-500/5 to-indigo-500/5" />
        <div className="relative max-w-4xl mx-auto py-6 px-6 flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <img src="/doligo-logo.svg" alt="DOLIGO" className="h-10" />
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-sky-600 to-indigo-600 bg-clip-text text-transparent">
                지원과제 AI 작성 서비스
              </h1>
              <p className="text-sm text-slate-500 mt-0.5">
                전문 비서 · 전략기획실 최고 전문가가 정확한 니즈를 반영합니다
              </p>
            </div>
          </div>
          <img src="/ceo-image.png" alt="김명환 대표" className="h-16 object-contain" />
        </div>
      </header>

      <main className="max-w-4xl mx-auto py-8 px-4">
        {!jobId ? (
          <div className="space-y-8">
            <section>
              <h2 className="text-sm font-semibold text-slate-600 mb-3">지원과제 맥락</h2>
              <UrlInput value={url} onChange={setUrl} />
            </section>

            <section>
              <h2 className="text-sm font-semibold text-slate-600 mb-3">AI와 대화하기</h2>
              <ChatPanel
                url={url}
                onSummaryChange={setChatSummary}
                onKeywordsExtracted={handleKeywordsExtracted}
              />
            </section>

            <section className="bg-white/80 backdrop-blur rounded-2xl border border-slate-200/80 p-6 shadow-xl">
              <h2 className="text-sm font-semibold text-slate-600 mb-4">문서 생성</h2>
              <KeywordInput value={keywords} onChange={setKeywords} />
              <div className="mt-4">
                <FileUpload
                  file={file}
                  onFileChange={setFile}
                  onStart={handleStart}
                  keywords={keywords}
                  url={url}
                  chatSummary={chatSummary}
                />
              </div>
            </section>
          </div>
        ) : (
          <div className="space-y-6">
            <ProgressDisplay jobId={jobId} onReset={handleReset} />
            <DownloadResult jobId={jobId} onReset={handleReset} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
