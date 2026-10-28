"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import AuthGate from "@/components/AuthGate";
import { Back } from "@/components/Header";
import { analyze, NoFaceError, RESULT_KEY, type Step as AnalyzeStep } from "@/lib/analyze";
import { preloadLandmarker } from "@/lib/face/landmarker";
import { Q, Select, Working } from "@/components/FunnelUI";

const thisYear = new Date().getFullYear();
const YEARS = Array.from({ length: 100 }, (_, i) => thisYear - i);
const range = (a: number, b: number) => Array.from({ length: b - a + 1 }, (_, i) => a + i);

const STEPS = ["birth", "time", "gender", "photo"] as const;
type Step = (typeof STEPS)[number];

const ANALYZE_TEXT: Record<AnalyzeStep, string> = {
  saju: "사주팔자를 계산하고 있어요",
  face: "얼굴을 읽고 있어요",
  common: "사주와 관상이 같이 말하는 걸 찾고 있어요",
  ai: "풀이를 정리하고 있어요",
  done: "거의 다 됐어요",
};

export default function AnalyzePage() {
  return (
    <AuthGate>
      <Funnel />
    </AuthGate>
  );
}

function Funnel() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("birth");
  const [calendar, setCalendar] = useState<"solar" | "lunar">("solar");
  const [leap, setLeap] = useState(false);
  const [year, setYear] = useState(1990);
  const [month, setMonth] = useState(1);
  const [day, setDay] = useState(1);
  const [hour, setHour] = useState(12);
  const [minute, setMinute] = useState(0);
  const [timeKnown, setTimeKnown] = useState(true);
  const [gender, setGender] = useState<"남" | "여" | null>(null);
  const [photo, setPhoto] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [working, setWorking] = useState<AnalyzeStep | null>(null);
  const [error, setError] = useState<string | null>(null);
  const camRef = useRef<HTMLInputElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => preloadLandmarker(), []);
  // 첫 화면에서 넣은 생년월일 이어받기 (?y=1990&m=5&d=17&cal=lunar&h=14 | h=none)
  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    const n = (k: string) => Number(q.get(k));
    if (n("y") >= YEARS[YEARS.length - 1] && n("y") <= thisYear) setYear(n("y"));
    if (n("m") >= 1 && n("m") <= 12) setMonth(n("m"));
    if (n("d") >= 1 && n("d") <= 31) setDay(n("d"));
    if (q.get("cal") === "lunar") setCalendar("lunar");
    if (q.get("h") === "none") setTimeKnown(false);
    else if (q.has("h") && n("h") >= 0 && n("h") <= 23) setHour(n("h"));
  }, []);
  useEffect(() => () => void (preview && URL.revokeObjectURL(preview)), [preview]);

  const maxDay = useMemo(() => (calendar === "lunar" ? 30 : new Date(year, month, 0).getDate()), [calendar, year, month]);
  useEffect(() => {
    if (day > maxDay) setDay(maxDay);
  }, [maxDay, day]);

  const idx = STEPS.indexOf(step);
  const go = (s: Step) => {
    setError(null);
    setStep(s);
    window.scrollTo(0, 0);
  };
  const back = () => (idx === 0 ? router.push("/") : go(STEPS[idx - 1]));

  const pick = (f: File | undefined | null) => {
    if (!f) return;
    if (!f.type.startsWith("image/")) return setError("사진 파일만 올릴 수 있어요.");
    setError(null);
    setPhoto(f);
    setPreview(URL.createObjectURL(f));
  };

  const run = async (withPhoto: boolean) => {
    if (!gender) return go("gender");
    setError(null);
    try {
      const result = await analyze(
        { year, month, day, hour: timeKnown ? hour : null, minute, calendar, leap: calendar === "lunar" && leap, gender },
        withPhoto ? photo : null,
        setWorking,
      );
      // 사진은 즉시 메모리에서 삭제
      setPhoto(null);
      setPreview(null);
      sessionStorage.setItem(RESULT_KEY, JSON.stringify(result));
      router.push("/result");
    } catch (e) {
      setWorking(null);
      if (e instanceof NoFaceError) {
        setError("사진에서 얼굴을 찾지 못했어요. 밝은 곳에서 정면으로 다시 찍어 주세요.");
      } else {
        console.error(e);
        setError("잠시 문제가 생겼어요. 다시 한 번 눌러 주세요.");
      }
    }
  };

  return (
    <div className="min-h-screen px-5">
      {/* 상단 바 + 진행 막대 */}
      <div className="sticky top-0 z-30 -mx-5 bg-paper px-5">
        <div className="flex h-14 items-center">
          <button onClick={back} aria-label="뒤로" className="-ml-2 p-2">
            <Back />
          </button>
        </div>
        <div className="h-1 overflow-hidden rounded-full bg-smoke">
          <motion.div className="h-full rounded-full bg-accent" animate={{ width: `${((idx + 1) / STEPS.length) * 100}%` }} transition={{ duration: 0.35 }} />
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 24 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -24 }}
          transition={{ duration: 0.25 }}
          className="pb-40 pt-8"
        >
          {step === "birth" && (
            <>
              <Q title="생일이 언제예요?" sub="사주는 생일과 태어난 시간으로 봐요." />
              <div className="mt-8 flex gap-2">
                <button type="button" className="chip" data-on={calendar === "solar"} onClick={() => setCalendar("solar")}>
                  양력
                </button>
                <button type="button" className="chip" data-on={calendar === "lunar"} onClick={() => setCalendar("lunar")}>
                  음력
                </button>
              </div>
              <div className="mt-3 grid grid-cols-[1.3fr_1fr_1fr] gap-2">
                <Select value={year} onChange={setYear} options={YEARS} suffix="년" label="태어난 해" />
                <Select value={month} onChange={setMonth} options={range(1, 12)} suffix="월" label="태어난 달" />
                <Select value={day} onChange={setDay} options={range(1, maxDay)} suffix="일" label="태어난 날" />
              </div>
              {calendar === "lunar" && (
                <label className="mt-4 flex items-center gap-2 text-[15px] text-sub">
                  <input type="checkbox" checked={leap} onChange={(e) => setLeap(e.target.checked)} className="h-5 w-5 accent-accent" />
                  윤달이에요
                </label>
              )}
            </>
          )}

          {step === "time" && (
            <>
              <Q title="태어난 시간은요?" sub="몰라도 괜찮아요. 시간 없이도 볼 수 있어요." />
              <div className="mt-8 grid grid-cols-2 gap-2">
                <Select value={hour} onChange={setHour} options={range(0, 23)} suffix="시" label="태어난 시" />
                <Select value={minute} onChange={setMinute} options={range(0, 59)} suffix="분" label="태어난 분" />
              </div>
            </>
          )}

          {step === "gender" && (
            <>
              <Q title="성별을 알려 주세요" sub="10년 단위 흐름을 계산할 때 필요해요." />
              <div className="mt-8 grid grid-cols-2 gap-3">
                {(["남", "여"] as const).map((g) => (
                  <button
                    key={g}
                    type="button"
                    onClick={() => {
                      setGender(g);
                      setTimeout(() => go("photo"), 150);
                    }}
                    data-on={gender === g}
                    className="chip h-32 flex-col gap-2 text-[17px]"
                  >
                    <span className="text-[34px]" aria-hidden>
                      {g === "남" ? "🙋‍♂️" : "🙋‍♀️"}
                    </span>
                    {g === "남" ? "남성" : "여성"}
                  </button>
                ))}
              </div>
            </>
          )}

          {step === "photo" && (
            <>
              <Q title="얼굴 사진을 보여 주세요" sub="사진은 이 폰 안에서만 분석하고 바로 지워요." />
              {preview ? (
                <div className="relative mt-8 overflow-hidden rounded-card bg-smoke">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={preview} alt="고른 얼굴 사진" className="aspect-[4/5] w-full object-cover" />
                  <button
                    type="button"
                    onClick={() => {
                      setPhoto(null);
                      setPreview(null);
                    }}
                    className="absolute right-3 top-3 rounded-full bg-ink/70 px-4 py-2 text-[14px] font-semibold text-paper"
                  >
                    다시 고르기
                  </button>
                </div>
              ) : (
                <div className="mt-8 space-y-3">
                  <button type="button" onClick={() => camRef.current?.click()} className="flex w-full items-center gap-4 rounded-card bg-smoke p-5 text-left active:scale-[0.99]">
                    <span className="flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-[24px]" aria-hidden>
                      📷
                    </span>
                    <span>
                      <span className="block text-[17px] font-semibold">지금 찍기</span>
                      <span className="block text-[14px] text-mute">정면, 밝은 곳, 앞머리는 넘겨 주세요</span>
                    </span>
                  </button>
                  <button type="button" onClick={() => fileRef.current?.click()} className="flex w-full items-center gap-4 rounded-card bg-smoke p-5 text-left active:scale-[0.99]">
                    <span className="flex h-12 w-12 items-center justify-center rounded-full bg-paper text-[24px]" aria-hidden>
                      🖼️
                    </span>
                    <span className="block text-[17px] font-semibold">앨범에서 고르기</span>
                  </button>
                </div>
              )}
              <input ref={camRef} type="file" accept="image/*" capture="user" hidden onChange={(e) => pick(e.target.files?.[0])} />
              <input ref={fileRef} type="file" accept="image/*" hidden onChange={(e) => pick(e.target.files?.[0])} />
              <p className="mt-6 text-center text-[13px] text-mute">
                시작하면 <Link href="/disclaimer" className="underline">면책조항</Link>과{" "}
                <Link href="/privacy" className="underline">개인정보처리방침</Link>에 동의한 것으로 봐요.
              </p>
            </>
          )}

          {error && <p className="mt-6 rounded-2xl bg-warn/10 px-4 py-3 text-[15px] font-medium text-warn">{error}</p>}
        </motion.div>
      </AnimatePresence>

      {/* 하단 버튼 */}
      <div className="bottom-cta space-y-2">
        {step === "birth" && (
          <button className="btn-primary w-full" onClick={() => go("time")}>
            다음
          </button>
        )}
        {step === "time" && (
          <>
            <button
              className="btn-primary w-full"
              onClick={() => {
                setTimeKnown(true);
                go("gender");
              }}
            >
              다음
            </button>
            <button
              className="btn-ghost w-full"
              onClick={() => {
                setTimeKnown(false);
                go("gender");
              }}
            >
              시간을 몰라요
            </button>
          </>
        )}
        {step === "gender" && (
          <button className="btn-primary w-full" disabled={!gender} onClick={() => go("photo")}>
            다음
          </button>
        )}
        {step === "photo" && (
          <>
            <button className="btn-primary w-full" disabled={!photo || working !== null} onClick={() => run(true)}>
              결과 보기
            </button>
            <button className="btn-ghost w-full" disabled={working !== null} onClick={() => run(false)}>
              사진 없이 사주만 볼게요
            </button>
          </>
        )}
      </div>

      <AnimatePresence>{working && <Working text={ANALYZE_TEXT[working]} />}</AnimatePresence>
    </div>
  );
}
