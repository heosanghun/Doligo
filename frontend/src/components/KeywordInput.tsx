interface KeywordInputProps {
  value: string;
  onChange: (v: string) => void;
}

export function KeywordInput({ value, onChange }: KeywordInputProps) {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
      <label className="block text-sm font-medium text-slate-700 mb-2">키워드</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="예: AI 플랫폼, 스마트 헬스케어, 디지털 전환..."
        className="w-full h-24 px-3 py-2 border border-slate-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        rows={4}
      />
    </div>
  );
}
