"use client";
import { useEffect, useRef, useState, type DragEvent } from "react";
import { useActionForm } from "@/components/ui/use-action-form";
import { publishQuickPostAction } from "@/app/actions/threads";
import { threadsLength, THREADS_TEXT_LIMIT, withAdDisclosure } from "@/lib/threads/text";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

const ACCEPT = ["image/png", "image/jpeg"];

export function ThreadsComposer({ canLive, liveProblems, accountName }: { canLive: boolean; liveProblems: string[]; accountName: string | null }) {
  const { state, pending, onSubmit, formRef } = useActionForm(publishQuickPostAction, { resetOnSuccess: true });
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [fileInfo, setFileInfo] = useState<string | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);
  const [caption, setCaption] = useState("");
  const [isAd, setIsAd] = useState(false);
  const [dragging, setDragging] = useState(false);

  const setFile = (file: File | null) => {
    setLocalError(null);
    if (!file) return;
    if (!ACCEPT.includes(file.type)) {
      setLocalError("JPG 또는 PNG 이미지만 올릴 수 있습니다.");
      return;
    }
    if (file.size > 8 * 1024 * 1024) {
      setLocalError("8MB 이하 이미지만 올릴 수 있습니다.");
      return;
    }
    const dt = new DataTransfer();
    dt.items.add(file);
    if (inputRef.current) inputRef.current.files = dt.files;
    setPreview((old) => {
      if (old) URL.revokeObjectURL(old);
      return URL.createObjectURL(file);
    });
    setFileInfo(`${file.name || "붙여넣은 이미지"} · ${(file.size / 1024).toFixed(0)}KB`);
  };

  // Ctrl+V 로 스크린샷 붙여넣기
  useEffect(() => {
    const onPaste = (e: ClipboardEvent) => {
      const item = [...(e.clipboardData?.items ?? [])].find((i) => i.type.startsWith("image/"));
      if (!item) return;
      const f = item.getAsFile();
      if (f) {
        e.preventDefault();
        setFile(new File([f], `screenshot-${Date.now()}.${f.type === "image/jpeg" ? "jpg" : "png"}`, { type: f.type }));
      }
    };
    window.addEventListener("paste", onPaste);
    return () => window.removeEventListener("paste", onPaste);
  }, []);

  // 성공하면 미리보기·문구 초기화
  useEffect(() => {
    if (state.ok) {
      setPreview((old) => {
        if (old) URL.revokeObjectURL(old);
        return null;
      });
      setFileInfo(null);
      setCaption("");
      setIsAd(false);
    }
  }, [state]);

  const finalText = withAdDisclosure(caption, isAd);
  const len = threadsLength(finalText);
  const over = len > THREADS_TEXT_LIMIT;
  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    setFile(e.dataTransfer.files?.[0] ?? null);
  };

  return (
    <form ref={formRef} method="post" encType="multipart/form-data" onSubmit={onSubmit} className="grid gap-6 lg:grid-cols-2" noValidate>
      <div>
        <label
          htmlFor="th-image"
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          className={`flex min-h-72 cursor-pointer flex-col items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed text-center transition ${
            dragging ? "border-brand-500 bg-brand-50" : "border-slate-300 bg-white hover:border-slate-400"
          }`}
        >
          {preview ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={preview} alt="게시할 이미지 미리보기" className="max-h-96 w-full object-contain" />
          ) : (
            <span className="px-6 text-sm text-slate-500">
              <span className="mb-2 block text-4xl" aria-hidden>🖼️</span>
              <strong className="text-slate-700">사진·스크린샷을 끌어다 놓거나 클릭해서 선택</strong>
              <br />
              또는 화면 캡처 후 <kbd className="rounded bg-slate-100 px-1.5 py-0.5 text-xs">Ctrl</kbd>+<kbd className="rounded bg-slate-100 px-1.5 py-0.5 text-xs">V</kbd>
              <br />
              <span className="text-xs text-slate-400">JPG·PNG, 8MB 이하</span>
            </span>
          )}
        </label>
        <input
          ref={inputRef}
          id="th-image"
          name="image"
          type="file"
          accept="image/png,image/jpeg"
          className="sr-only"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        {fileInfo && <p className="mt-2 text-xs text-slate-500">{fileInfo}</p>}
        {localError && <p role="alert" className="mt-2 text-xs font-medium text-rose-600">{localError}</p>}
      </div>

      <div className="flex flex-col gap-3">
        <div>
          <label htmlFor="th-caption" className="label">문구 (선택)</label>
          <textarea id="th-caption" name="caption" rows={8} value={caption} onChange={(e) => setCaption(e.target.value)} className="input" placeholder="스레드에 함께 올릴 글을 쓰세요" />
          <p className={`mt-1 text-right text-xs ${over ? "font-semibold text-rose-600" : "text-slate-400"}`}>
            {len} / {THREADS_TEXT_LIMIT}자 (이모지는 더 많이 셉니다)
          </p>
        </div>
        <label className="flex items-start gap-2 rounded-lg bg-amber-50 p-3 text-sm text-amber-900">
          <input type="checkbox" name="isAd" checked={isAd} onChange={(e) => setIsAd(e.target.checked)} className="mt-0.5" />
          <span>
            광고·협찬(대가를 받은) 게시물입니다
            <span className="block text-xs text-amber-700">체크하면 광고 표시가 없을 때 ‘#광고’가 자동으로 붙습니다.</span>
          </span>
        </label>
        {isAd && finalText !== caption.trim() && (
          <p className="text-xs text-slate-500">실제 게시 문구 끝에 <code>#광고</code> 가 추가됩니다.</p>
        )}
        <FormMessage state={state} />
        <div className="mt-auto flex flex-wrap gap-2">
          <SubmitButton pending={pending} name="mode" value="LIVE" disabled={!canLive || over || !preview} pendingText="스레드에 올리는 중… (최대 1분)">
            {accountName ? `${accountName} 스레드에 바로 게시` : "스레드에 바로 게시"}
          </SubmitButton>
          <SubmitButton pending={pending} name="mode" value="SIMULATED" variant="secondary" disabled={over || !preview} pendingText="처리 중…">
            모의 게시 (테스트)
          </SubmitButton>
        </div>
        {!canLive && (
          <ul className="list-inside list-disc text-xs text-slate-500">
            {liveProblems.map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        )}
      </div>
    </form>
  );
}
