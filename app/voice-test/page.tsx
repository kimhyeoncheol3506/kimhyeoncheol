"use client";
import { useEffect, useMemo, useState } from "react";
import VoicePlayer from "@/components/VoicePlayer";
import { Script, toSpoken } from "@/lib/narration";
import { VOICE_TESTS, VOICE_WORDS } from "@/lib/voice/testScript";

// 평가 항목과 가중치 (발음 정확도 40, 띄어읽기 25, 억양 20, 숫자·영문 10, 반복 안정성 5)
const CRITERIA = [
  { key: "phoneme", label: "자음·모음 정확도", hint: "받침, 연음, 된소리, 비음화", weight: 40 },
  { key: "spacing", label: "띄어읽기", hint: "단어 간격과 의미 단위별 호흡", weight: 25 },
  { key: "intonation", label: "억양", hint: "평서문·의문문·감탄문 구별", weight: 20 },
  { key: "natural", label: "자연스러움", hint: "사람이 말하는 듯한 리듬", weight: 0 },
  { key: "numbers", label: "숫자·영문", hint: "날짜, 금액, 약어 발음", weight: 10 },
  { key: "long", label: "긴 문장 안정성", hint: "문장 후반의 발음 저하 여부", weight: 0 },
  { key: "speed", label: "속도 조절", hint: "빠르거나 느릴 때의 명료성", weight: 0 },
  { key: "stable", label: "일관성", hint: "반복해도 발음이 안정적인가", weight: 5 },
] as const;
type Scores = Record<string, number>;
const STORE = "voice-test-scores";
const VOICE_TABS = [
  { id: "male", label: "남성 목소리" },
  { id: "female", label: "여성 목소리" },
] as const;

export default function VoiceTestPage() {
  const [tab, setTab] = useState<"male" | "female">("male");
  const [all, setAll] = useState<Record<string, Scores>>({ male: {}, female: {} });
  const [notes, setNotes] = useState<Record<string, string>>({ male: "", female: "" });
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(STORE) ?? "null");
      if (saved?.all) setAll(saved.all);
      if (saved?.notes) setNotes(saved.notes);
    } catch {
      /* 없으면 새로 시작 */
    }
  }, []);
  const persist = (a: typeof all, n: typeof notes) => {
    try {
      localStorage.setItem(STORE, JSON.stringify({ all: a, notes: n }));
    } catch {
      /* 저장 실패해도 화면은 동작 */
    }
  };

  const scores = all[tab] ?? {};
  const setScore = (k: string, v: number) => {
    const next = { ...all, [tab]: { ...scores, [k]: v } };
    setAll(next);
    persist(next, notes);
  };
  const total = CRITERIA.reduce((s, c) => s + (scores[c.key] ?? 3), 0);
  const weighted = Math.round(CRITERIA.reduce((s, c) => s + (c.weight * (scores[c.key] ?? 3)) / 5, 0));

  const testCues = useMemo(
    () => VOICE_TESTS.map((t) => t.lines.reduce((sc, l) => sc.add("body", l, 600), new Script()).cues),
    [],
  );
  const wordCues = useMemo(() => VOICE_WORDS.reduce((sc, w) => sc.add("body", w.word, 700), new Script()).cues, []);

  const copy = async () => {
    const label = VOICE_TABS.find((v) => v.id === tab)!.label;
    const text = [
      `[${label}] 한국어 발음 평가`,
      ...CRITERIA.map((c) => `- ${c.label}: ${scores[c.key] ?? 3}/5`),
      `총점 ${total}/40 · 평균 ${(total / CRITERIA.length).toFixed(2)}/5 · 가중 점수 ${weighted}/100`,
      notes[tab] ? `오류 기록: ${notes[tab]}` : "",
    ]
      .filter(Boolean)
      .join("\n");
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* 클립보드 권한 없음 */
    }
  };
  const reset = () => {
    const next = { ...all, [tab]: {} };
    const nn = { ...notes, [tab]: "" };
    setAll(next);
    setNotes(nn);
    persist(next, nn);
  };

  return (
    <div className="space-y-3 px-4 pb-24 pt-2">
      <section className="px-1 pb-2">
        <p className="text-[15px] font-semibold text-accent">운영자용</p>
        <h1 className="mt-1 text-headline font-bold">목소리 발음 테스트</h1>
        <p className="mt-2 text-[15px] leading-relaxed text-sub">
          실제 앱과 같은 목소리·같은 변환 규칙으로 읽습니다. 각 테스트를 남성·여성 목소리로 들어 보고 아래 평가표에 점수를 매겨 주세요. 같은 문장을 3번 들어 보면 안정성도 확인할 수 있어요.
        </p>
      </section>

      {VOICE_TESTS.map((t, i) => (
        <div key={t.id} className="card">
          <p className="text-[13px] font-semibold text-mute">테스트 {i + 1}</p>
          <h2 className="mt-1 text-title font-bold">{t.title}</h2>
          <ul className="mt-3 space-y-1">
            {t.focus.map((f) => (
              <li key={f} className="text-[14px] leading-relaxed text-mute">
                · {f}
              </li>
            ))}
          </ul>
          <ol className="mt-4 space-y-2">
            {t.lines.map((l) => {
              const spoken = toSpoken(l);
              return (
                <li key={l} className="rounded-2xl bg-smoke px-4 py-3 text-[15px] leading-relaxed text-ink">
                  {l}
                  {spoken !== l && <span className="mt-1 block text-[13px] text-accent">읽는 글: {spoken}</span>}
                </li>
              );
            })}
          </ol>
          <div className="mt-4 border-t border-line pt-4">
            <VoicePlayer cues={testCues[i]} />
          </div>
        </div>
      ))}

      <div className="card">
        <p className="text-[13px] font-semibold text-mute">추가 테스트</p>
        <h2 className="mt-1 text-title font-bold">발음 규칙 낱말</h2>
        <div className="mt-4 grid grid-cols-3 gap-2 text-center">
          {VOICE_WORDS.map((w) => (
            <div key={w.word} className="rounded-2xl bg-smoke px-2 py-3">
              <p className="text-[12px] text-mute">{w.rule}</p>
              <p className="mt-0.5 text-[17px] font-bold">{w.word}</p>
              <p className="text-[13px] text-accent">[{w.sound}]</p>
            </div>
          ))}
        </div>
        <div className="mt-4 border-t border-line pt-4">
          <VoicePlayer cues={wordCues} />
        </div>
      </div>

      <div className="card">
        <h2 className="text-title font-bold">평가표</h2>
        <div className="mt-3 flex gap-2">
          {VOICE_TABS.map((v) => (
            <button key={v.id} type="button" className="chip h-10 px-4 text-[14px]" data-on={tab === v.id} onClick={() => setTab(v.id)}>
              {v.label}
            </button>
          ))}
        </div>
        <div className="mt-4 divide-y divide-line">
          {CRITERIA.map((c) => (
            <div key={c.key} className="py-3">
              <div className="flex items-baseline justify-between">
                <p className="text-[16px] font-bold">{c.label}</p>
                {c.weight > 0 && <span className="text-[12px] font-semibold text-accent">가중치 {c.weight}%</span>}
              </div>
              <p className="text-[13px] text-mute">{c.hint}</p>
              <div className="mt-2 grid grid-cols-5 gap-1.5">
                {[1, 2, 3, 4, 5].map((n) => (
                  <button key={n} type="button" className="chip h-10 text-[15px]" data-on={(scores[c.key] ?? 3) === n} onClick={() => setScore(c.key, n)}>
                    {n}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
        <textarea
          className="field mt-4 h-24 resize-none py-3 text-[15px]"
          placeholder="오류 단어 기록 예: 국밥 → 평음으로 발음, 꽃이 → 연음 오류"
          value={notes[tab] ?? ""}
          onChange={(e) => {
            const nn = { ...notes, [tab]: e.target.value };
            setNotes(nn);
            persist(all, nn);
          }}
        />
        <div className="mt-4 rounded-2xl bg-accent-soft px-4 py-4 text-center">
          <p className="text-[14px] text-sub">
            총점 {total} / 40 · 평균 {(total / CRITERIA.length).toFixed(2)} / 5
          </p>
          <p className="mt-1 text-[28px] font-bold text-accent">가중 점수 {weighted} / 100</p>
        </div>
        <div className="mt-3 grid grid-cols-2 gap-2">
          <button type="button" className="btn-primary" onClick={copy}>
            {copied ? "복사했어요" : "평가 결과 복사"}
          </button>
          <button type="button" className="btn-ghost" onClick={reset}>
            점수 초기화
          </button>
        </div>
      </div>
    </div>
  );
}
