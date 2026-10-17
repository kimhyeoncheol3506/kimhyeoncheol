"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { VOICES, WebSpeechEngine, createEngine, type TtsEngine, type VoiceId } from "@/lib/tts";
import { cuesFromText, type Cue } from "@/lib/narration";

type State = "idle" | "playing" | "paused" | "ended";
const SPEEDS = [0.9, 1, 1.15, 1.3];
const PREF_KEY = "voice-pref";

function loadPref(): { voice: VoiceId; speed: number } {
  try {
    const p = JSON.parse(localStorage.getItem(PREF_KEY) ?? "{}");
    return { voice: p.voice === "female" ? "female" : "male", speed: SPEEDS.includes(p.speed) ? p.speed : 1 };
  } catch {
    return { voice: "male", speed: 1 };
  }
}
function savePref(p: { voice: VoiceId; speed: number }) {
  try {
    localStorage.setItem(PREF_KEY, JSON.stringify(p));
  } catch {
    /* 저장이 안 돼도 재생에는 문제없음 */
  }
}

/** 결과 전체를 목소리로 읽어주는 큰 플레이 버튼 */
export default function VoicePlayer({ cues: given, script }: { cues?: Cue[]; script?: string }) {
  const cues = useMemo(() => given ?? cuesFromText(script ?? ""), [given, script]);
  const engine = useRef<TtsEngine | null>(null);
  const idx = useRef(0);
  const gap = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [i, setI] = useState(0);
  const [state, setState] = useState<State>("idle");
  const [supported, setSupported] = useState(true);
  const [voice, setVoice] = useState<VoiceId>("male");
  const [speed, setSpeed] = useState(1);

  useEffect(() => {
    let alive = true;
    const pref = loadPref();
    setVoice(pref.voice);
    setSpeed(pref.speed);
    const web = new WebSpeechEngine();
    engine.current = web;
    setSupported(web.supported);
    createEngine().then((e) => {
      if (!alive) return;
      e.setVoice(pref.voice);
      e.setSpeed(pref.speed);
      engine.current = e;
      setSupported(true);
    });
    return () => {
      alive = false;
      if (gap.current) clearTimeout(gap.current);
      engine.current?.stop();
    };
  }, []);

  const halt = () => {
    if (gap.current) clearTimeout(gap.current);
    engine.current?.stop();
  };

  const playFrom = (n: number) => {
    const e = engine.current;
    if (!e) return;
    idx.current = n;
    halt();
    if (n >= cues.length) {
      setState("ended");
      return;
    }
    setI(n);
    setState("playing");
    // 끊김 없이 이어지도록 다음 두 덩어리를 미리 준비
    for (const c of cues.slice(n + 1, n + 3)) e.prefetch?.(c);
    e.speak(cues[n], () => {
      if (idx.current !== n) return;
      // 제목 뒤·섹션 사이에는 숨 쉬는 쉼
      gap.current = setTimeout(() => idx.current === n && playFrom(n + 1), cues[n].pause / speed);
    });
  };

  const toggle = () => {
    if (state !== "playing") engine.current?.unlock?.();
    if (state === "playing") {
      // 일부 모바일 브라우저는 pause가 불안정해서, 멈춘 덩어리부터 다시 읽는 방식 사용
      idx.current = -1;
      halt();
      setState("paused");
    } else if (state === "paused") {
      playFrom(i);
    } else {
      playFrom(0);
    }
  };
  /** 다음 이야기(다음 제목)로 건너뛰기 */
  const nextIdx = cues.findIndex((c, k) => k > i && c.kind === "title");
  const skip = () => {
    if (nextIdx < 0) return;
    engine.current?.unlock?.();
    playFrom(nextIdx);
  };
  const replay = () => {
    engine.current?.unlock?.();
    playFrom(0);
  };

  const changeVoice = (v: VoiceId) => {
    setVoice(v);
    savePref({ voice: v, speed });
    engine.current?.setVoice(v);
    if (state === "playing") playFrom(i); // 바뀐 목소리로 지금 덩어리부터 다시
  };
  const changeSpeed = () => {
    const next = SPEEDS[(SPEEDS.indexOf(speed) + 1) % SPEEDS.length];
    setSpeed(next);
    savePref({ voice, speed: next });
    engine.current?.setSpeed(next);
  };

  const progress = cues.length ? ((state === "ended" ? cues.length : i) / cues.length) * 100 : 0;
  const totalChars = useMemo(() => cues.reduce((s, c) => s + c.text.length, 0), [cues]);
  const minutes = Math.max(1, Math.round(totalChars / 6.5 / 60 / speed)); // 한국어 낭독 약 6~7자/초

  if (!supported) {
    return <p className="text-[15px] text-mute">이 브라우저는 음성 낭독을 지원하지 않아요. Chrome이나 Safari 최신 버전에서 열어 주세요.</p>;
  }

  return (
    <div>
      <div className="flex items-center gap-4">
        <button
          onClick={toggle}
          aria-label={state === "playing" ? "일시정지" : "재생"}
          className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-accent text-paper transition active:scale-95"
        >
          {state === "playing" ? (
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
              <path d="M6 4h4v16H6zM14 4h4v16h-4z" />
            </svg>
          ) : (
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
              <path d="M7 4.5v15l12-7.5z" />
            </svg>
          )}
        </button>
        <div className="min-w-0 flex-1">
          <p className="text-[17px] font-semibold">
            {state === "playing" ? "읽는 중" : state === "paused" ? "일시정지" : state === "ended" ? "다 읽었어요" : "목소리로 듣기"}
          </p>
          <p className="mt-0.5 line-clamp-1 text-[14px] text-mute">
            {state === "idle" ? `처음부터 끝까지 약 ${minutes}분` : cues[Math.min(i, cues.length - 1)]?.text}
          </p>
        </div>
        {state !== "idle" && (
          <button onClick={replay} className="shrink-0 rounded-full bg-smoke px-3 py-2 text-[13px] font-semibold text-sub">
            처음부터
          </button>
        )}
      </div>

      {state !== "idle" && state !== "ended" && nextIdx > 0 && (
        <button type="button" onClick={skip} className="mt-3 w-full rounded-2xl bg-smoke py-2.5 text-[14px] font-semibold text-sub active:scale-[0.99]">
          다음 이야기로 건너뛰기 · {cues[nextIdx].text.replace(/^[^,]+,\s*/, "").replace(/\.$/, "")}
        </button>
      )}
      {state !== "idle" && (
        <div className="mt-4 h-1 w-full overflow-hidden rounded-full bg-smoke">
          <div className="h-full rounded-full bg-accent transition-all duration-500" style={{ width: `${progress}%` }} />
        </div>
      )}

      <div className="mt-4 flex items-center gap-2">
        {(Object.keys(VOICES) as VoiceId[]).map((v) => (
          <button key={v} type="button" onClick={() => changeVoice(v)} data-on={voice === v} className="chip h-9 px-3 text-[13px]">
            {VOICES[v].label}
          </button>
        ))}
        <button type="button" onClick={changeSpeed} aria-label="읽는 속도" className="chip ml-auto h-9 px-3 text-[13px]">
          {speed}배속
        </button>
      </div>
    </div>
  );
}
