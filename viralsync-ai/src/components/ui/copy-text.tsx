"use client";
import { useState } from "react";

/** 사람이 직접 보낼 메시지 초안 — 수정 가능한 칸 + 복사 버튼 (자동 발송 없음) */
export function CopyText({ id, label, text, rows = 6 }: { id: string; label: string; text: string; rows?: number }) {
  const [value, setValue] = useState(text);
  const [copied, setCopied] = useState(false);
  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="label">{label}</label>
      <textarea id={id} value={value} onChange={(e) => setValue(e.target.value)} rows={rows} className="input font-[inherit] text-sm" />
      <button
        type="button"
        className="rounded-lg bg-slate-800 px-3 py-1.5 text-xs font-medium text-white hover:bg-slate-700"
        onClick={async () => {
          try {
            await navigator.clipboard.writeText(value);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
          } catch {
            setCopied(false);
          }
        }}
      >
        {copied ? "복사했습니다 ✓" : "복사하기"}
      </button>
    </div>
  );
}
