import { Link2 } from "lucide-react";

interface UrlInputProps {
  value: string;
  onChange: (v: string) => void;
}

export function UrlInput({ value, onChange }: UrlInputProps) {
  return (
    <div className="flex items-center gap-2 px-4 py-3 bg-white/90 rounded-xl border border-slate-200/80">
      <Link2 className="w-5 h-5 text-sky-500 flex-shrink-0" />
      <input
        type="url"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="지원과제 공고 URL을 붙여넣기 하세요 (선택)"
        className="flex-1 bg-transparent outline-none text-slate-800 placeholder-slate-400 text-sm"
      />
    </div>
  );
}
