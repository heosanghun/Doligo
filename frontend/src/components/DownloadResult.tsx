import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Download, Home, FileText, Copy, X } from "lucide-react";

interface DownloadResultProps {
  jobId: string;
  onReset?: () => void;
}

const getApiBase = () =>
  (import.meta as { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL ?? "";

export function DownloadResult({ jobId, onReset }: DownloadResultProps) {
  const [showMd, setShowMd] = useState(false);
  const [mdContent, setMdContent] = useState("");
  const [copyDone, setCopyDone] = useState(false);
  const apiBase = getApiBase();

  const { data, isLoading } = useQuery({
    queryKey: ["job", jobId],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/generate/${jobId}`);
      if (!res.ok) throw new Error("조회 실패");
      return res.json();
    },
    refetchInterval: (q) => (q.state.data?.status === "completed" ? false : 2000),
    enabled: !!jobId,
  });

  const handleDownload = () => {
    window.open(`${apiBase}/api/generate/${jobId}/download`, "_blank");
  };

  const handleShowMd = async () => {
    const res = await fetch(`${apiBase}/api/generate/${jobId}/content`);
    if (!res.ok) return;
    const json = await res.json();
    setMdContent(json.markdown || "");
    setShowMd(true);
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(mdContent);
    setCopyDone(true);
    setTimeout(() => setCopyDone(false), 2000);
  };

  if (isLoading || !data) return null;
  if (data.status !== "completed") return null;

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        <span className="text-sm text-slate-600">문서 생성 완료</span>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-xl text-sm font-medium hover:bg-green-700"
          >
            <Download className="w-4 h-4" />
            다운로드
          </button>
          <button
            onClick={handleShowMd}
            className="flex items-center gap-2 px-4 py-2 bg-slate-600 text-white rounded-xl text-sm font-medium hover:bg-slate-700"
          >
            <FileText className="w-4 h-4" />
            Markdown 보기
          </button>
          {onReset && (
            <button
              onClick={onReset}
              className="flex items-center gap-2 px-4 py-2 bg-sky-600 text-white rounded-xl text-sm font-medium hover:bg-sky-700"
            >
              <Home className="w-4 h-4" />
              홈으로 돌아가기
            </button>
          )}
        </div>
      </div>

      {showMd && (
        <div className="mt-4 fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setShowMd(false)}>
          <div className="bg-white rounded-xl shadow-xl max-w-3xl w-full max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between p-4 border-b">
              <span className="font-medium">Markdown 내용 (복붙용)</span>
              <div className="flex gap-2">
                <button onClick={handleCopy} className="flex items-center gap-2 px-3 py-1.5 bg-sky-600 text-white rounded-lg text-sm hover:bg-sky-700">
                  <Copy className="w-4 h-4" />
                  {copyDone ? "복사됨!" : "전체 복사"}
                </button>
                <button onClick={() => setShowMd(false)} className="p-1.5 hover:bg-slate-100 rounded-lg">
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            <pre className="flex-1 overflow-auto p-4 text-sm text-slate-800 whitespace-pre-wrap font-sans">{mdContent}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
