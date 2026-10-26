"use client";
export function PrintButton() {
  return (
    <button type="button" onClick={() => window.print()} className="rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700">
      인쇄 / PDF 저장
    </button>
  );
}
