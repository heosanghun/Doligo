import { useState, useRef, useCallback, useEffect } from "react";
import { Mic, MicOff, Plus, X } from "lucide-react";

interface VoiceInputProps {
  value: string;
  onChange: (v: string) => void;
  onSend: (text: string, images?: File[]) => void;
  attachedImages: File[];
  onAttachedImagesChange: (files: File[]) => void;
  disabled?: boolean;
}

const ERROR_MESSAGES: Record<string, string> = {
  "not-allowed": "마이크 권한이 거부되었습니다. 브라우저 설정에서 마이크를 허용해 주세요.",
  "no-speech": "음성이 감지되지 않았습니다. 다시 시도해 주세요.",
  "audio-capture": "마이크에 접근할 수 없습니다. 다른 앱이 사용 중인지 확인하세요.",
  "network":
    "음성 인식 서버에 연결할 수 없습니다. VPN·방화벽을 확인하거나, Microsoft Edge에서 시도해 보세요. 직접 입력도 가능합니다.",
  "aborted": "음성 인식이 중단되었습니다.",
};

export function VoiceInput({ value, onChange, onSend, attachedImages, onAttachedImagesChange, disabled }: VoiceInputProps) {
  const [isListening, setIsListening] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const accumulatedRef = useRef(value);

  useEffect(() => {
    accumulatedRef.current = value;
  }, [value]);

  const startListening = useCallback(() => {
    setVoiceError(null);
    accumulatedRef.current = value;
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceError("이 브라우저는 음성 인식을 지원하지 않습니다. Chrome 또는 Edge를 사용해 주세요.");
      return;
    }
    if (!window.isSecureContext) {
      setVoiceError("음성 인식은 HTTPS 또는 localhost에서만 사용할 수 있습니다.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = "ko-KR";
    recognition.maxAlternatives = 1;

    recognition.onresult = (e: SpeechRecognitionEvent) => {
      let transcript = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) {
          transcript += e.results[i][0].transcript;
        }
      }
      if (transcript) {
        accumulatedRef.current += transcript;
        onChange(accumulatedRef.current);
      }
    };

    recognition.onerror = (e: Event & { error?: string }) => {
      const err = (e as { error?: string }).error ?? "unknown";
      const msg = ERROR_MESSAGES[err] || `음성 인식 오류: ${err}`;
      setVoiceError(msg);
      setIsListening(false);
    };
    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;
    try {
      recognition.start();
      setIsListening(true);
    } catch (err) {
      setVoiceError("마이크를 시작할 수 없습니다. 다른 탭에서 마이크를 사용 중인지 확인하세요.");
    }
  }, [value, onChange]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
  }, []);

  const handleSend = () => {
    const t = value.trim();
    if (t || attachedImages.length > 0) {
      onSend(t || "(이미지)", attachedImages.length > 0 ? [...attachedImages] : undefined);
      onChange("");
      onAttachedImagesChange([]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const images = files.filter((f) => f.type.startsWith("image/"));
    if (images.length > 0) {
      onAttachedImagesChange([...attachedImages, ...images].slice(0, 5));
    }
    e.target.value = "";
  };

  const removeImage = (index: number) => {
    onAttachedImagesChange(attachedImages.filter((_, i) => i !== index));
  };

  return (
    <div className="w-full">
      <p className="text-center text-slate-600 mb-4 text-sm">준비되면 얘기해 주세요.</p>
      {voiceError && (
        <p className="text-center text-amber-600 text-sm mb-2 px-2">{voiceError}</p>
      )}
      {attachedImages.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {attachedImages.map((file, i) => (
            <div key={i} className="relative group">
              <img
                src={URL.createObjectURL(file)}
                alt=""
                className="w-16 h-16 object-cover rounded-lg border border-slate-200"
              />
              <button
                type="button"
                onClick={() => removeImage(i)}
                className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center opacity-80 hover:opacity-100"
                aria-label="삭제"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}
      <div className="flex items-center gap-3 px-4 py-3 bg-white rounded-2xl border-2 border-slate-200 shadow-sm hover:border-sky-300 transition-colors">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          className="hidden"
          onChange={handleFileSelect}
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="p-2 rounded-full hover:bg-slate-100 text-slate-500 disabled:opacity-50"
          aria-label="이미지 첨부"
        >
          <Plus className="w-5 h-5" />
        </button>
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="무엇이든 물어보세요"
          className="flex-1 bg-transparent outline-none text-slate-800 placeholder-slate-400"
          disabled={disabled}
        />
        <button
          type="button"
          onClick={isListening ? stopListening : startListening}
          disabled={disabled}
          className={`p-2 rounded-full transition-all ${
            isListening ? "bg-amber-400 text-white animate-pulse" : "hover:bg-slate-100 text-slate-600"
          }`}
          aria-label={isListening ? "음성 종료" : "음성 입력"}
        >
          {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
        </button>
      </div>
    </div>
  );
}
