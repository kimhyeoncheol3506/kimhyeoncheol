"use client";

/** 사진 업로드 전 별도 동의 체크박스 */
export default function ConsentCheck({ checked, onChange, children }: { checked: boolean; onChange: (v: boolean) => void; children: React.ReactNode }) {
  return (
    <label className={`flex cursor-pointer items-start gap-3 rounded-btn px-4 py-3.5 text-[14px] leading-relaxed ring-1 ring-inset transition ${checked ? "bg-accent-soft ring-accent/50" : "bg-paper ring-line"}`}>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} className="mt-0.5 h-5 w-5 shrink-0 accent-accent" />
      <span className="text-sub">{children}</span>
    </label>
  );
}
