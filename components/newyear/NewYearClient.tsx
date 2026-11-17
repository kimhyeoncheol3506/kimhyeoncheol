"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Q, Select, Working } from "@/components/FunnelUI";
import SectionCard from "@/components/SectionCard";
import { computeSaju } from "@/lib/saju/consensus";
import type { SajuConsensus } from "@/lib/saju/types";
import { NEWYEAR, NEWYEAR_NOW, composeNewYear, type NewYearReport } from "@/lib/newyear/compose";
import { compactDraft } from "@/lib/reading/compact";
import type { ResultPayload, Section } from "@/lib/reading/types";
import { track } from "@/lib/track";

const KEY = "newyear-result";
const thisYear = new Date().getFullYear();
const YEARS = Array.from({ length: 100 }, (_, i) => thisYear - i);
const range = (a: number, b: number) => Array.from({ length: b - a + 1 }, (_, i) => a + i);
type Saved = { report: NewYearReport; saju: SajuConsensus };

export default function NewYearClient({ locked }: { locked: boolean }) {
  const [saved, setSaved] = useState<Saved | null>(null);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(KEY);
      if (raw) setSaved(JSON.parse(raw));
    } catch {
      /* 없으면 입력부터 */
    }
    setReady(true);
    track("start", { flow: "newyear" });
  }, []);
  if (!ready) return null;
  return saved ? <Report saved={saved} locked={locked} onReset={() => { sessionStorage.removeItem(KEY); setSaved(null); }} /> : <Form onDone={setSaved} />;
}

function Form({ onDone }: { onDone: (s: Saved) => void }) {
  const [name, setName] = useState("");
  const [gender, setGender] = useState<"남" | "여" | null>(null);
  const [calendar, setCalendar] = useState<"solar" | "lunar">("solar");
  const [leap, setLeap] = useState(false);
  const [year, setYear] = useState(1990);
  const [month, setMonth] = useState(1);
  const [day, setDay] = useState(1);
  const [hour, setHour] = useState(12);
  const [minute, setMinute] = useState(0);
  const [timeKnown, setTimeKnown] = useState(false);
  const [working, setWorking] = useState<string | null>(null);
  const maxDay = useMemo(() => (calendar === "lunar" ? 30 : new Date(year, month, 0).getDate()), [calendar, year, month]);
  useEffect(() => {
    if (day > maxDay) setDay(maxDay);
  }, [day, maxDay]);

  const run = async () => {
    if (!gender) return;
    track("input_complete", { flow: "newyear" });
    setWorking("2027년 열두 달을 계산하고 있어요");
    const birth = { year, month, day, hour: timeKnown ? hour : null, minute, calendar, leap: calendar === "lunar" && leap, gender };
    const saju = computeSaju(birth, NEWYEAR_NOW());
    let report = composeNewYear(saju, gender, name);
    // AI 개인화: 서버에 키가 있을 때만 (없으면 규칙 기반 그대로)
    try {
      setWorking("한 해의 흐름을 정리하고 있어요");
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), 40000);
      const res = await fetch("/api/interpret", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mode: "newyear",
          gender,
          age: saju.age,
          saju: { dayMaster: saju.dayMaster, fiveElements: saju.fiveElements, strength: saju.strength, yongsin: saju.yongsin, year2027: saju.years[0] },
          draft: compactDraft({ headline: report.headline, summary: report.summary, sections: [...report.free, ...report.detail], advice: report.advice }),
        }),
        signal: ctrl.signal,
      });
      clearTimeout(timer);
      if (res.ok) {
        const ai = (await res.json()) as { headline?: string; summary?: string; sections?: Section[]; advice?: string[] };
        if (ai.sections?.length) {
          const merge = (list: Section[]) =>
            list.map((s) => {
              const a = ai.sections!.find((x) => x.id === s.id);
              return a && !s.items?.length ? { ...s, body: a.body } : s; // 표 항목(날짜·별점)은 규칙 기반 값을 유지
            });
          report = { ...report, headline: ai.headline || report.headline, summary: ai.summary || report.summary, free: merge(report.free), detail: merge(report.detail), advice: ai.advice?.length ? ai.advice : report.advice, source: "ai" };
        }
      }
    } catch {
      /* AI 실패 시 규칙 기반 */
    }
    const s = { report, saju };
    try {
      sessionStorage.setItem(KEY, JSON.stringify(s));
    } catch {
      /* 저장 실패해도 화면은 보여 줌 */
    }
    setWorking(null);
    window.scrollTo(0, 0);
    onDone(s);
  };

  return (
    <div className="px-5 pb-44 pt-6">
      <p className="eyebrow">2027 · {NEWYEAR.ko}</p>
      <Q title="2027년, 나의 한 해는?" sub="생일만 넣으면 총운과 달마다 운세를 바로 보여 드려요. 입력값은 이 기기 안에서만 계산해요." />
      <div className="mt-8 space-y-6">
        <input className="field" maxLength={10} placeholder="이름 (선택)" value={name} onChange={(e) => setName(e.target.value)} />
        <div>
          <p className="mb-2 text-[14px] font-semibold text-mute">성별</p>
          <div className="grid grid-cols-2 gap-2">
            {(["남", "여"] as const).map((g) => (
              <button key={g} type="button" className="chip h-12" data-on={gender === g} onClick={() => setGender(g)}>
                {g === "남" ? "남성" : "여성"}
              </button>
            ))}
          </div>
        </div>
        <div>
          <p className="mb-2 text-[14px] font-semibold text-mute">생일</p>
          <div className="flex gap-2">
            <button type="button" className="chip" data-on={calendar === "solar"} onClick={() => setCalendar("solar")}>양력</button>
            <button type="button" className="chip" data-on={calendar === "lunar"} onClick={() => setCalendar("lunar")}>음력</button>
          </div>
          <div className="mt-3 grid grid-cols-[1.3fr_1fr_1fr] gap-2">
            <Select value={year} onChange={setYear} options={YEARS} suffix="년" label="태어난 해" />
            <Select value={month} onChange={setMonth} options={range(1, 12)} suffix="월" label="태어난 달" />
            <Select value={day} onChange={setDay} options={range(1, maxDay)} suffix="일" label="태어난 날" />
          </div>
          {calendar === "lunar" && (
            <label className="mt-3 flex items-center gap-2 text-[15px] text-sub">
              <input type="checkbox" checked={leap} onChange={(e) => setLeap(e.target.checked)} className="h-5 w-5 accent-accent" />
              윤달이에요
            </label>
          )}
        </div>
        <div>
          <label className="flex items-center gap-2 text-[15px] text-sub">
            <input type="checkbox" checked={timeKnown} onChange={(e) => setTimeKnown(e.target.checked)} className="h-5 w-5 accent-accent" />
            태어난 시간도 알아요 (선택)
          </label>
          {timeKnown && (
            <div className="mt-3 grid grid-cols-2 gap-2">
              <Select value={hour} onChange={setHour} options={range(0, 23)} suffix="시" label="태어난 시" />
              <Select value={minute} onChange={setMinute} options={range(0, 59)} suffix="분" label="태어난 분" />
            </div>
          )}
        </div>
        <p className="text-center text-[13px] text-mute">
          시작하면 <Link href="/terms" className="underline">이용약관</Link>에 동의하고 <Link href="/privacy" className="underline">개인정보처리방침</Link>을 확인한 것으로 봐요.
        </p>
      </div>
      <div className="bottom-cta">
        <button className="btn-primary w-full" disabled={!gender || working !== null} onClick={run}>
          {gender ? "2027년 운세 보기 (무료)" : "성별을 골라 주세요"}
        </button>
      </div>
      {working && <Working text={working} />}
    </div>
  );
}

function Report({ saved, locked, onReset }: { saved: Saved; locked: boolean; onReset: () => void }) {
  const { report: r, saju } = saved;
  const [pdf, setPdf] = useState<"idle" | "making" | "failed">("idle");
  useEffect(() => track("result_view", { flow: "newyear", locked }), [locked]);

  const downloadPdf = async () => {
    setPdf("making");
    const payload: ResultPayload = {
      createdAt: r.createdAt,
      name: r.name,
      gender: r.gender,
      saju,
      face: null,
      common: r.keywords.map((label) => ({ key: "independence", label, saju: 0, face: 0, sajuReason: "", faceReason: "", strong: false })),
      reading: {
        headline: `2027 ${NEWYEAR.ko} · ${r.headline}`,
        summary: r.summary,
        sections: [...r.free, ...r.detail],
        advice: r.advice,
        source: r.source,
      },
    };
    try {
      const res = await fetch("/api/pdf", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ result: payload, name: r.name }) });
      if (!res.ok) throw new Error(String(res.status));
      const url = URL.createObjectURL(await res.blob());
      const a = document.createElement("a");
      a.href = url;
      a.download = `2027_신년운세_${r.name ?? "나"}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
      track("pdf_download", { flow: "newyear", method: "server" });
      setPdf("idle");
    } catch {
      setPdf("failed");
    }
  };

  return (
    <div className="pb-32">
      <section className="px-5 pt-6 text-center">
        <p className="eyebrow">2027 · {NEWYEAR.ko}</p>
        <h1 className="mt-3 font-serif text-[26px] font-bold leading-snug">{r.headline}</h1>
        <p className="mt-2 text-[22px] tracking-[2px] text-accent" aria-label="한 해 흐름 별점">{r.overall}</p>
        <div className="mt-4 flex flex-wrap justify-center gap-2">
          {r.keywords.map((k) => (
            <span key={k} className="rounded-full bg-smoke px-3.5 py-1.5 text-[13px] font-semibold text-sub">{k}</span>
          ))}
        </div>
        <p className="mt-5 text-[17px] leading-[1.7] text-sub">{r.summary}</p>
      </section>

      <div className="space-y-3 px-4 pt-6">
        {r.free.map((s) => (
          <SectionCard key={s.id} s={s} />
        ))}

        <div className="card">
          <h2 className="text-title font-bold">달마다 한 줄 운세</h2>
          <p className="mt-1 text-[14px] text-mute">사주의 한 해는 입춘(2월 4일 무렵)부터 시작해요.</p>
          <ul className="mt-4 divide-y divide-line">
            {r.monthLines.map((m) => (
              <li key={m.label} className="py-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-[15px] font-bold">{m.label.replace("2027년 ", "")}</p>
                  <span className="text-[13px] tracking-[1px] text-accent">{m.stars}</span>
                </div>
                <p className="mt-0.5 text-[15px] text-sub">{m.theme}</p>
                <p className="mt-0.5 text-[13px] text-mute">좋은 일 {m.good}</p>
              </li>
            ))}
          </ul>
        </div>

        {locked ? (
          <div className="card text-center">
            <p className="eyebrow">Premium Report</p>
            <h2 className="mt-2 font-serif text-[20px] font-bold">상세 리포트는 12월에 열려요</h2>
            <p className="mt-2 text-[14px] leading-relaxed text-mute">지금 보신 총운과 달마다 한 줄 운세는 무료예요. 아래 상세 리포트는 12월 첫 주에 공개될 예정입니다.</p>
            <ul className="mt-5 space-y-2 text-left">
              {r.detail.map((s) => (
                <li key={s.id} className="rounded-2xl bg-smoke px-4 py-3">
                  <p className="text-[15px] font-semibold">{s.title}</p>
                  <p className="mt-1 select-none text-[14px] text-sub blur-[5px]" aria-hidden>{s.body[0]}</p>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <>
            {r.detail.map((s) => (
              <SectionCard key={s.id} s={s} />
            ))}
            <div className="card bg-accent text-paper">
              <p className="text-[15px] font-semibold text-paper/80">2027년을 위한 당부</p>
              <ul className="mt-3 space-y-3">
                {r.advice.map((a) => (
                  <li key={a} className="text-[16px] font-medium leading-relaxed">{a}</li>
                ))}
              </ul>
            </div>
            <div className="card">
              <h2 className="text-title font-bold">2027 신년운세 PDF 받기</h2>
              <p className="mt-1 text-[14px] text-mute">조선 사당풍 운명첩 디자인으로 한 해 리포트를 저장해 두세요.</p>
              <button className="btn-primary mt-4 w-full" disabled={pdf === "making"} onClick={downloadPdf}>
                {pdf === "making" ? "만드는 중…" : "PDF 받기"}
              </button>
              {pdf === "failed" && <p className="mt-2 text-center text-[14px] text-warn">PDF를 만들지 못했어요. 잠시 뒤 다시 눌러 주세요.</p>}
            </div>
          </>
        )}

        <p className="px-2 pt-2 text-center text-[13px] leading-relaxed text-mute">
          신년운세는 전통 명리학의 일반적인 해석을 적용한 재미·참고용이며 미래를 단정하지 않습니다.{r.source === "ai" ? " 문장은 AI가 다듬었습니다." : ""}{" "}
          <Link href="/guide/sipsin" className="underline">해마다 들어오는 별 이야기</Link>
        </p>
      </div>
      <div className="bottom-cta grid grid-cols-2 gap-2">
        <button className="btn-ghost" onClick={onReset}>다른 생일로 보기</button>
        <Link href="/analyze" className="btn-primary">내 사주·관상 보기</Link>
      </div>
    </div>
  );
}
