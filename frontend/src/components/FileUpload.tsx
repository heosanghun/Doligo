import { useState } from "react";
import { Upload, FileText, Presentation, File, FileCode, Sparkles } from "lucide-react";

type OutputFormat = "pdf" | "ppt" | "hwp" | "md";

interface FileUploadProps {
  file: File | null;
  onFileChange: (f: File | null) => void;
  onStart: (jobId: string) => void;
  keywords: string;
  url: string;
  chatSummary: string;
}

const ALLOWED = [".pdf", ".pptx", ".hwp", ".hwpx"];

const OUTPUT_FORMATS: { value: OutputFormat; label: string; Icon: typeof FileText }[] = [
  { value: "pdf", label: "PDF", Icon: FileText },
  { value: "ppt", label: "PPT", Icon: Presentation },
  { value: "hwp", label: "HWP", Icon: File },
  { value: "md", label: "MD", Icon: FileCode },
];

export function FileUpload({ file, onFileChange, onStart, keywords, url, chatSummary }: FileUploadProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [outputFormat, setOutputFormat] = useState<OutputFormat>("pdf");

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    const ext = "." + f.name.split(".").pop()?.toLowerCase();
    if (!ALLOWED.includes(ext)) {
      setError(`지원 형식: ${ALLOWED.join(", ")}`);
      return;
    }
    setError("");
    onFileChange(f);
  };

  const handleSubmit = async () => {
    if (!file || !keywords.trim()) {
      setError("키워드와 파일을 모두 입력하세요.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const form = new FormData();
      form.append("keywords", keywords.trim());
      form.append("output_format", outputFormat);
      if (url.trim()) form.append("url", url.trim());
      if (chatSummary.trim()) form.append("chat_summary", chatSummary.trim());
      form.append("file", file);
      const res = await fetch("/api/generate", {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || res.statusText || "요청 실패");
      }
      const data = await res.json();
      onStart(data.job_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "오류");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm space-y-4">
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">양식 파일 (PDF, PPT, HWP)</label>
        <label className="flex items-center justify-center gap-2 px-4 py-3 border-2 border-dashed border-slate-300 rounded-xl cursor-pointer hover:border-sky-400 hover:bg-slate-50 transition-colors">
          <Upload className="w-5 h-5 text-slate-500" />
          <span className="text-sm text-slate-600">{file ? file.name : "파일 선택"}</span>
          <input type="file" accept={ALLOWED.join(",")} onChange={handleFile} className="hidden" />
        </label>
      </div>
      <div>
        <div className="flex justify-center gap-6">
          {OUTPUT_FORMATS.map(({ value, label, Icon }) => (
            <button
              key={value}
              type="button"
              onClick={() => setOutputFormat(value)}
              className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all ${
                outputFormat === value
                  ? "border-sky-500 bg-sky-50 text-sky-600"
                  : "border-slate-200 hover:border-slate-300 text-slate-500 hover:text-slate-700"
              }`}
            >
              <Icon className="w-10 h-10" strokeWidth={1.5} />
              <span className="text-sm font-medium">{label}</span>
            </button>
          ))}
        </div>
      </div>
      <div className="pt-2">
        <button
          onClick={handleSubmit}
          disabled={loading || !file || !keywords.trim()}
          className="w-full flex items-center justify-center gap-3 py-4 px-6 bg-gradient-to-r from-sky-600 to-indigo-600 text-white rounded-xl text-base font-semibold shadow-lg shadow-sky-500/30 hover:from-sky-700 hover:to-indigo-700 hover:shadow-xl hover:shadow-sky-500/40 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-lg transition-all"
        >
          <Sparkles className="w-5 h-5" />
          {loading ? "문서 생성 중..." : "문서 생성 시작"}
        </button>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
