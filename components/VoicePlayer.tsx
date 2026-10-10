"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { WebSpeechEngine, chunkSentences, createEngine, speakable, splitSentences, type TtsEngine } from "@/lib/tts";

type State = "idle" | "playing" | "paused" | "ended";

/** 결과 전체를 목소리로 읽어주는 큰 플레이 버튼 */
export default function VoicePlayer({ script }: { script: string }) {
  const sentences = useMemo(() => chunkSentences(splitSentences(script).map(speakable).filter(Boolean)), [script]);
  const engine = useRef<TtsEngine | null>(null);
  const idx = useRef(0);
  const [i, setI] = useState(0);
  const [state, setState] = useState<State>("idle");
  const [supported, setSupported] = useState(true);

  useEffect(() => {
    let alive = true;
    engine.current = new WebSpeechEngine();
    setSupported(engine.current.supported);
    createEngine().then((e) => {
      if (!alive) return;
      engine.current = e;
      setSupported(true);
    });
    return () => {
      alive = false;
      engine.current?.stop();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const playFrom = (n: number) => {
    const e = engine.current;
    if (!e) return;
    idx.current = n;
    e.stop();
    if (n >= sentences.length) {
      setState("ended");
      return;
    }
    setI(n);
    setState("playing");
    if (sentences[n + 1]) e.prefetch?.(sentences[n + 1]);
    e.speak(sentences[n], () => {
      if (idx.current === n) playFrom(n + 1);
    });
  };

  const toggle = () => {
    if (state !== "playing") engine.current?.unlock?.();
    if (state === "playing") {
      // 일부 모바일 브라우저는 pause가 불안정해서, 멈춘 문장부터 다시 읽는 방식 사용
      idx.current = -1;
      engine.current?.stop();
      setState("paused");
    } else if (state === "paused") {
      playFrom(i);
    } else {
      playFrom(0);
    }
  };
  const replay = () => {
    engine.current?.unlock?.();
    playFrom(0);
  };

  const progress = sentences.length ? ((state === "ended" ? sentences.length : i) / sentences.length) * 100 : 0;

  if (!supported) {
    return <p className="text-sm text-paper/60">이 브라우저는 음성 낭독을 지원하지 않아요. Chrome·Safari 최신 버전에서 열어 주세요.</p>;
  }

  return (
    <div>
      <div className="flex items-center gap-5">
        <button
          onClick={toggle}
          aria-label={state === "playing" ? "일시정지" : "재생"}
          className="flex h-24 w-24 shrink-0 items-center justify-center bg-accent text-paper transition-transform hover:scale-[1.04] active:scale-95 md:h-28 md:w-28"
        >
          {state === "playing" ? (
            <svg width="34" height="34" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
              <path d="M6 4h4v16H6zM14 4h4v16h-4z" />
            </svg>
          ) : (
            <svg width="36" height="36" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
              <path d="M7 4.5v15l12-7.5z" />
            </svg>
          )}
        </button>
        <div className="min-w-0 flex-1">
          <p className="text-2xl font-black tracking-tight md:text-3xl">
            {state === "playing" ? "읽는 중" : state === "paused" ? "일시정지" : state === "ended" ? "다 읽었어요" : "전체 듣기"}
          </p>
          <p className="mt-1 line-clamp-2 text-sm text-paper/60">
            {state === "idle" ? "결과를 처음부터 끝까지 읽어드립니다." : sentences[Math.min(i, sentences.length - 1)]}
          </p>
        </div>
        {state !== "idle" && (
          <button onClick={replay} className="hidden h-14 shrink-0 border border-paper/30 px-5 text-sm font-semibold hover:bg-paper hover:text-ink sm:block">
            다시 듣기
          </button>
        )}
      </div>
      <div className="mt-6 h-[3px] w-full bg-paper/15">
        <div className="h-full bg-accent transition-all duration-500" style={{ width: `${progress}%` }} />
      </div>
      {state !== "idle" && (
        <button onClick={replay} className="mt-4 h-12 w-full border border-paper/30 text-sm font-semibold sm:hidden">
          다시 듣기
        </button>
      )}
    </div>
  );
}
