import { useEffect, useState } from "react";
import { Home, FileText, Pen, Sparkles } from "lucide-react";

interface ProgressDisplayProps {
  jobId: string;
  onReset: () => void;
}

const STATUS_INFO: Record<string, { label: string; desc: string }> = {
  pending: { label: "대기", desc: "작업을 시작합니다" },
  parsing: { label: "양식 분석", desc: "문서 구조를 분석하고 있습니다" },
  drafting: { label: "초안 작성", desc: "AI가 전문가처럼 초안을 작성하고 있습니다" },
  feedback_1: { label: "피드백 1회차", desc: "품질 검토 및 보완점을 적용하고 있습니다" },
  feedback_2: { label: "피드백 2회차", desc: "자체 검증을 진행하고 있습니다" },
  feedback_3: { label: "피드백 3회차", desc: "보완점을 반영해 개선하고 있습니다" },
  feedback_4: { label: "피드백 4회차", desc: "추가 개선점을 검토하고 있습니다" },
  feedback_5: { label: "피드백 5회차", desc: "최종 검토 및 완성도를 높이고 있습니다" },
  images: { label: "이미지 생성", desc: "문서에 삽입할 이미지를 준비하고 있습니다" },
  building: { label: "문서 조립", desc: "최종 문서를 조립하고 있습니다" },
  completed: { label: "완료", desc: "문서 생성이 완료되었습니다" },
  failed: { label: "실패", desc: "오류가 발생했습니다" },
  cancelled: { label: "취소됨", desc: "작업이 취소되었습니다" },
};

export function ProgressDisplay({ jobId, onReset }: ProgressDisplayProps) {
  const [status, setStatus] = useState("");
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let closed = false;
    const apiBase = (import.meta as { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL ?? "";
    const evt = new EventSource(`${apiBase}/api/generate/${jobId}/stream`);

    evt.onmessage = (e) => {
      if (closed) return;
      try {
        const data = JSON.parse(e.data);
        setStatus(data.status || "");
        setProgress(data.progress ?? 0);
        setMessage(data.message || "");
        setError(data.error || null);
      } catch {}
    };

    evt.onerror = () => {
      if (!closed) evt.close();
    };

    return () => {
      closed = true;
      evt.close();
    };
  }, [jobId]);

  const done = ["completed", "failed", "cancelled"].includes(status);
  const info = STATUS_INFO[status] || { label: "대기 중", desc: "작업을 준비하고 있습니다" };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-xl overflow-hidden">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-slate-800">문서 생성 진행</h2>
        {done && (
          <button
            onClick={onReset}
            className="flex items-center gap-2 px-4 py-2 text-sm text-sky-600 hover:text-sky-700 font-medium hover:bg-sky-50 rounded-xl transition-colors"
          >
            <Home className="w-4 h-4" />
            홈으로 돌아가기
          </button>
        )}
      </div>

      {!done && (
        <>
          {/* 펜 + 문서 애니메이션 */}
          <div className="flex justify-center mb-8">
            <div className="relative w-48 h-36 flex items-center justify-center">
              <FileText
                className="w-24 h-24 text-sky-100 animate-pulse"
                strokeWidth={1}
              />
              <Pen
                className="absolute w-10 h-10 text-sky-500 pen-animate"
                strokeWidth={2}
                style={{ top: "50%", left: "55%", transform: "translate(-50%, -50%) rotate(-15deg)" }}
              />
              <Sparkles className="absolute top-4 right-8 w-5 h-5 text-amber-400 sparkle-1" />
              <Sparkles className="absolute bottom-6 left-6 w-4 h-4 text-sky-400 sparkle-2" />
            </div>
          </div>

          {/* 실시간 작업 안내 */}
          <div className="text-center mb-6">
            <p className="text-lg font-semibold text-slate-800 mb-1">
              지금은 <span className="text-sky-600">{info.label}</span> 작업을 합니다
            </p>
            <p className="text-sm text-slate-500">{info.desc}</p>
            {message && (
              <p className="mt-2 text-sm text-sky-600 font-medium">{message}</p>
            )}
          </div>

          {/* 프로그레스 바 */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-600">진행률</span>
              <span className="font-semibold text-sky-600">{progress}%</span>
            </div>
            <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-sky-500 to-indigo-500 rounded-full transition-all duration-500 relative overflow-hidden"
                style={{ width: `${progress}%` }}
              >
                <div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -skew-x-12"
                  style={{ animation: "shimmer 1.5s ease-in-out infinite" }}
                />
              </div>
            </div>
          </div>
        </>
      )}

      {done && (
        <div className="flex items-center gap-3">
          <div className="flex-1 h-3 bg-slate-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="text-sm font-medium text-slate-600 w-10">{progress}%</span>
        </div>
      )}

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      <style>{`
        .pen-animate {
          animation: penWrite 1.8s ease-in-out infinite;
        }
        @keyframes penWrite {
          0%, 100% { transform: translate(-50%, -50%) rotate(-15deg) scale(1); }
          50% { transform: translate(-50%, -55%) rotate(-8deg) scale(1.08); }
        }
        .sparkle-1 { animation: sparkle 2s ease-in-out infinite; }
        .sparkle-2 { animation: sparkle 2s ease-in-out infinite 0.8s; }
        @keyframes sparkle {
          0%, 100% { opacity: 0.5; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.2); }
        }
        @keyframes shimmer {
          0% { transform: translateX(-100%) skewX(-12deg); }
          100% { transform: translateX(200%) skewX(-12deg); }
        }
      `}</style>
    </div>
  );
}
