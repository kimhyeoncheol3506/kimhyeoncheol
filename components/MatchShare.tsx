"use client";
import { useRef, useState } from "react";
import MatchScoreCard from "@/components/MatchScoreCard";
import { relationLabel, toShareQuery } from "@/lib/match/share";
import type { MatchResult } from "@/lib/match/compute";
import { track } from "@/lib/track";

/** 궁합 점수 카드 + 이미지 저장 · 공유 · 링크 복사 */
export default function MatchShare({ data }: { data: MatchResult }) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const url = `${typeof window !== "undefined" ? window.location.origin : ""}/match/share?${toShareQuery(data)}`;
  const text = `우리 궁합은 ${data.total}점, “${data.headline}” — 너도 궁합 봐 볼래?`;
  const flash = (m: string) => {
    setMsg(m);
    setTimeout(() => setMsg(null), 2200);
  };

  const makePng = async () => {
    const { toPng } = await import("html-to-image");
    return toPng(cardRef.current!, { pixelRatio: 2, cacheBust: true, backgroundColor: "#FAF6EE" });
  };

  const save = async () => {
    try {
      const png = await makePng();
      const a = document.createElement("a");
      a.href = png;
      a.download = `궁합-${data.total}점.png`;
      a.click();
      track("share", { flow: "match", method: "image" });
      flash("이미지를 저장했어요");
    } catch {
      flash("이미지를 만들지 못했어요. 화면을 캡처해 주세요.");
    }
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(`${text} ${url}`);
      track("share", { flow: "match", method: "link" });
      flash("링크를 복사했어요");
    } catch {
      flash("복사하지 못했어요");
    }
  };

  const share = async () => {
    if (!navigator.share) return copy();
    try {
      // 이미지 파일까지 함께 보낼 수 있으면 같이 보냄
      let files: File[] | undefined;
      try {
        const blob = await (await fetch(await makePng())).blob();
        const f = new File([blob], `궁합-${data.total}점.png`, { type: "image/png" });
        if (navigator.canShare?.({ files: [f] })) files = [f];
      } catch {
        /* 이미지 없이 링크만 */
      }
      await navigator.share({ title: "얼굴과 운명 · 궁합", text, url, ...(files ? { files } : {}) });
      track("share", { flow: "match", method: files ? "native_image" : "native" });
    } catch {
      /* 사용자가 취소 */
    }
  };

  return (
    <div className="card">
      <h2 className="text-title font-bold">궁합 카드 공유하기</h2>
      <p className="mt-1 text-[14px] text-mute">생년월일·사진·고민은 담기지 않고 점수만 공유돼요.</p>
      <div ref={cardRef} className="mt-4">
        <MatchScoreCard names={data.names} relation={relationLabel(data.relation)} total={data.total} headline={data.headline} scores={data.scores.map((s) => s.value)} leader={data.leader} />
      </div>
      <div className="mt-4 grid grid-cols-3 gap-2">
        <button type="button" className="btn-primary !px-2 !text-[15px]" onClick={share}>
          공유하기
        </button>
        <button type="button" className="btn-ghost !px-2 !text-[15px]" onClick={save}>
          이미지 저장
        </button>
        <button type="button" className="btn-ghost !px-2 !text-[15px]" onClick={copy}>
          링크 복사
        </button>
      </div>
      {msg && <p className="mt-3 text-center text-[14px] font-semibold text-accent" role="status">{msg}</p>}
    </div>
  );
}
