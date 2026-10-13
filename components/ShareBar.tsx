"use client";
import { useRef, useState } from "react";
import type { ResultPayload } from "@/lib/reading/types";

declare global {
  interface Window {
    Kakao?: {
      isInitialized(): boolean;
      init(key: string): void;
      Share: { sendDefault(opts: unknown): void };
    };
  }
}

const KAKAO_KEY = process.env.NEXT_PUBLIC_KAKAO_JS_KEY;

function loadKakao(): Promise<NonNullable<Window["Kakao"]>> {
  return new Promise((resolve, reject) => {
    if (window.Kakao) return resolve(window.Kakao);
    const s = document.createElement("script");
    s.src = "https://t1.kakaocdn.net/kakao_js_sdk/2.7.2/kakao.min.js";
    s.crossOrigin = "anonymous";
    s.onload = () => (window.Kakao ? resolve(window.Kakao) : reject());
    s.onerror = reject;
    document.head.appendChild(s);
  });
}

/** 공유 버튼 (카카오톡 · X · 이미지 저장 · 링크 복사). 생년월일 같은 개인정보는 공유 문구에 넣지 않습니다. */
export default function ShareBar({ result }: { result: ResultPayload }) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const site = typeof window !== "undefined" ? window.location.origin : "";
  const keywords = result.common.map((c) => c.label);
  const text = `사주와 관상이 동시에 말한 나: “${result.reading.headline}” — ${keywords.join(" · ")}. 당신도 무료로 확인해 보세요.`;

  const flash = (m: string) => {
    setMsg(m);
    setTimeout(() => setMsg(null), 2200);
  };

  const kakao = async () => {
    if (KAKAO_KEY) {
      try {
        const K = await loadKakao();
        if (!K.isInitialized()) K.init(KAKAO_KEY);
        K.Share.sendDefault({
          objectType: "feed",
          content: {
            title: result.reading.headline,
            description: keywords.join(" · "),
            imageUrl: `${site}/og.png`,
            link: { mobileWebUrl: site, webUrl: site },
          },
          buttons: [{ title: "나도 무료로 보기", link: { mobileWebUrl: site, webUrl: site } }],
        });
        return;
      } catch {
        /* 아래 대체 방식으로 */
      }
    }
    if (navigator.share) {
      try {
        await navigator.share({ title: "얼굴과 운명", text, url: site });
      } catch {
        /* 사용자가 취소 */
      }
      return;
    }
    await copy();
  };

  const x = () => {
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(site)}`;
    window.open(url, "_blank", "noopener,noreferrer");
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(`${text} ${site}`);
      flash("링크를 복사했어요");
    } catch {
      flash("복사에 실패했어요");
    }
  };

  const saveImage = async () => {
    if (!cardRef.current) return;
    try {
      const { toPng } = await import("html-to-image");
      const url = await toPng(cardRef.current, { pixelRatio: 2, cacheBust: true });
      const a = document.createElement("a");
      a.href = url;
      a.download = "my-fate.png";
      a.click();
      flash("이미지를 저장했어요");
    } catch {
      flash("이미지 저장에 실패했어요");
    }
  };

  return (
    <div>
      <div className="grid grid-cols-2 gap-2">
        <button onClick={kakao} className="btn bg-[#FEE500] text-[#191919]">카카오톡</button>
        <button onClick={x} className="btn-ghost">X (트위터)</button>
        <button onClick={saveImage} className="btn-ghost">이미지 저장</button>
        <button onClick={copy} className="btn-ghost">링크 복사</button>
      </div>
      {msg && <p className="mt-3 text-sm font-semibold text-accent">{msg}</p>}

      {/* 이미지 저장용 카드 (화면 밖에 렌더) */}
      <div className="pointer-events-none fixed left-[-9999px] top-0" aria-hidden>
        <div ref={cardRef} style={{ width: 540, height: 675 }} className="flex flex-col justify-between bg-paper p-12 text-ink">
          <div className="flex items-center gap-2 text-sm font-black">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-accent" /> 얼굴과 운명
          </div>
          <div>
            <p className="text-[13px] font-semibold uppercase tracking-[0.2em] text-accent">사주와 관상이 같이 말하는 나</p>
            <p className="mt-5 text-[46px] font-black leading-[1.05] tracking-[-0.04em]">{result.reading.headline}</p>
            <div className="mt-8 flex flex-wrap gap-2">
              {keywords.map((k) => (
                <span key={k} className="rounded-full bg-accent-soft px-3 py-1.5 text-sm font-semibold text-accent">
                  {k}
                </span>
              ))}
            </div>
          </div>
          <p className="text-sm text-mute">무료 사주 + 관상 · {site.replace(/^https?:\/\//, "")}</p>
        </div>
      </div>
    </div>
  );
}
