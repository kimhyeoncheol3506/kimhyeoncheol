"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import AuthGate from "@/components/AuthGate";
import { analyze, NoFaceError, RESULT_KEY, type Step } from "@/lib/analyze";
import { preloadLandmarker } from "@/lib/face/landmarker";

const thisYear = new Date().getFullYear();
const YEARS = Array.from({ length: 100 }, (_, i) => thisYear - i);
const range = (a: number, b: number) => Array.from({ length: b - a + 1 }, (_, i) => a + i);

const STEP_TEXT: Record<Step, string> = {
  saju: "두 개의 사주 엔진으로 팔자를 계산하는 중",
  face: "얼굴 랜드마크 478점을 읽는 중",
  common: "사주와 관상의 공통점을 찾는 중",
  ai: "AI가 해석을 정리하는 중",
  done: "완료",
};
const STEP_ORDER: Step[] = ["saju", "face", "common", "ai"];

export default function AnalyzePage() {
  return (
    <AuthGate>
      <AnalyzeForm />
    </AuthGate>
  );
}

function AnalyzeForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [calendar, setCalendar] = useState<"solar" | "lunar">("solar");
  const [leap, setLeap] = useState(false);
  const [year, setYear] = useState(1990);
  const [month, setMonth] = useState(1);
  const [day, setDay] = useState(1);
  const [timeKnown, setTimeKnown] = useState(true);
  const [hour, setHour] = useState(12);
  const [minute, setMinute] = useState(0);
  const [gender, setGender] = useState<"남" | "여" | null>(null);
  const [photo, setPhoto] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [drag, setDrag] = useState(false);
  const [step, setStep] = useState<Step | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [noFace, setNoFace] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const camRef = useRef<HTMLInputElement>(null);

  useEffect(() => preloadLandmarker(), []);
  useEffect(() => () => void (preview && URL.revokeObjectURL(preview)), [preview]);

  const maxDay = useMemo(() => (calendar === "lunar" ? 30 : new Date(year, month, 0).getDate()), [calendar, year, month]);
  useEffect(() => {
    if (day > maxDay) setDay(maxDay);
  }, [maxDay, day]);

  const pick = (f: File | undefined | null) => {
    if (!f) return;
    if (!f.type.startsWith("image/")) return setError("이미지 파일만 올릴 수 있어요.");
    setError(null);
    setNoFace(false);
    setPhoto(f);
    setPreview(URL.createObjectURL(f));
  };
  const clearPhoto = () => {
    setPhoto(null);
    setPreview(null);
    if (fileRef.current) fileRef.current.value = "";
    if (camRef.current) camRef.current.value = "";
  };

  const run = async (withPhoto: boolean) => {
    if (!gender) return setError("성별을 선택해 주세요.");
    if (withPhoto && !photo) return setError("얼굴 사진을 올려 주세요.");
    setError(null);
    try {
      const result = await analyze(
        { year, month, day, hour: timeKnown ? hour : null, minute, calendar, leap: calendar === "lunar" && leap, gender },
        withPhoto ? photo : null,
        setStep,
        name,
      );
      clearPhoto(); // 사진은 즉시 메모리에서 삭제
      sessionStorage.setItem(RESULT_KEY, JSON.stringify(result));
      router.push("/result");
    } catch (e) {
      setStep(null);
      if (e instanceof NoFaceError) {
        setNoFace(true);
        setError("사진에서 얼굴을 찾지 못했어요. 정면이 잘 보이는 밝은 사진으로 다시 시도해 주세요.");
      } else {
        console.error(e);
        setError("분석 중 문제가 생겼어요. 입력값을 확인하고 다시 시도해 주세요.");
      }
    }
  };

  return (
    <div className="mx-auto max-w-page px-5 pb-28 pt-12 md:px-10 md:pt-20">
      <p className="label">Step 1 / 1</p>
      <h1 className="mt-4 text-headline font-black">
        당신을
        <br />
        알려 주세요.
      </h1>

      <div className="mt-14 grid gap-14 md:grid-cols-2 md:gap-20">
        {/* 왼쪽: 생년월일 */}
        <div className="space-y-10">
          <Field label="이름 또는 닉네임 (선택)">
            <input className="field" value={name} onChange={(e) => setName(e.target.value)} placeholder="결과 화면에만 표시돼요" maxLength={20} />
          </Field>

          <Field label="달력">
            <div className="flex">
              <button type="button" className="chip" data-on={calendar === "solar"} onClick={() => setCalendar("solar")}>양력</button>
              <button type="button" className="chip -ml-px" data-on={calendar === "lunar"} onClick={() => setCalendar("lunar")}>음력</button>
            </div>
            {calendar === "lunar" && (
              <label className="mt-3 flex items-center gap-2 text-sm">
                <input type="checkbox" checked={leap} onChange={(e) => setLeap(e.target.checked)} className="h-5 w-5 accent-ink" />
                윤달이에요
              </label>
            )}
          </Field>

          <Field label="생년월일">
            <div className="grid grid-cols-[1.4fr_1fr_1fr] gap-2">
              <Select value={year} onChange={setYear} options={YEARS} suffix="년" />
              <Select value={month} onChange={setMonth} options={range(1, 12)} suffix="월" />
              <Select value={day} onChange={setDay} options={range(1, maxDay)} suffix="일" />
            </div>
          </Field>

          <Field label="태어난 시간">
            <div className="grid grid-cols-[1fr_1fr] gap-2">
              <Select value={hour} onChange={setHour} options={range(0, 23)} suffix="시" disabled={!timeKnown} />
              <Select value={minute} onChange={setMinute} options={range(0, 59)} suffix="분" disabled={!timeKnown} />
            </div>
            <label className="mt-3 flex items-center gap-2 text-sm">
              <input type="checkbox" checked={!timeKnown} onChange={(e) => setTimeKnown(!e.target.checked)} className="h-5 w-5 accent-ink" />
              시간을 몰라요 (시주 없이 계산)
            </label>
          </Field>

          <Field label="성별">
            <div className="flex">
              <button type="button" className="chip" data-on={gender === "남"} onClick={() => setGender("남")}>남성</button>
              <button type="button" className="chip -ml-px" data-on={gender === "여"} onClick={() => setGender("여")}>여성</button>
            </div>
          </Field>
        </div>

        {/* 오른쪽: 사진 */}
        <div>
          <Field label="얼굴 사진">
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDrag(true);
              }}
              onDragLeave={() => setDrag(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDrag(false);
                pick(e.dataTransfer.files?.[0]);
              }}
              className={`relative flex aspect-[4/5] w-full flex-col items-center justify-center overflow-hidden border transition-colors ${
                drag ? "border-accent bg-accent/5" : "border-dashed border-ink/30 bg-smoke"
              }`}
            >
              {preview ? (
                <>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={preview} alt="업로드한 얼굴 사진 미리보기" className="h-full w-full object-cover grayscale-[20%]" />
                  <button type="button" onClick={clearPhoto} className="absolute right-3 top-3 bg-ink px-4 py-2 text-sm font-semibold text-paper">
                    다시 선택
                  </button>
                </>
              ) : (
                <div className="px-6 text-center">
                  <FaceIcon />
                  <p className="mt-6 text-xl font-bold tracking-tight">사진을 끌어다 놓으세요</p>
                  <p className="mt-2 text-sm text-mute">정면 · 밝은 곳 · 안경과 앞머리는 최대한 없이</p>
                </div>
              )}
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2">
              <button type="button" className="btn-ghost" onClick={() => fileRef.current?.click()}>사진 선택</button>
              <button type="button" className="btn-ghost" onClick={() => camRef.current?.click()}>카메라 촬영</button>
            </div>
            <input ref={fileRef} type="file" accept="image/*" hidden onChange={(e) => pick(e.target.files?.[0])} />
            <input ref={camRef} type="file" accept="image/*" capture="user" hidden onChange={(e) => pick(e.target.files?.[0])} />
            <p className="mt-4 flex items-start gap-2 text-xs leading-relaxed text-mute">
              <span className="mt-[3px] inline-block h-2 w-2 shrink-0 bg-accent" />
              사진은 서버로 전송되지 않고, 이 기기의 브라우저 안에서만 분석된 뒤 즉시 삭제됩니다.
            </p>
          </Field>
        </div>
      </div>

      {error && <p className="mt-10 border-l-4 border-accent bg-accent/5 px-4 py-3 text-sm font-medium text-accent">{error}</p>}

      <div className="mt-12 flex flex-col gap-3 md:flex-row md:items-center">
        <button type="button" onClick={() => run(true)} disabled={step !== null} className="btn-primary h-20 w-full text-xl md:w-auto md:px-16">
          분석 시작 <span aria-hidden>→</span>
        </button>
        {noFace && (
          <button type="button" onClick={() => run(false)} className="btn-ghost w-full md:w-auto">
            사진 없이 사주만 보기
          </button>
        )}
      </div>
      <p className="mt-6 text-xs text-mute">
        시작하면 <Link href="/disclaimer" className="underline">면책조항</Link>과{" "}
        <Link href="/privacy" className="underline">개인정보처리방침</Link>에 동의한 것으로 봅니다.
      </p>

      <AnimatePresence>{step && <Progress step={step} />}</AnimatePresence>
    </div>
  );
}

function Progress({ step }: { step: Step }) {
  const idx = STEP_ORDER.indexOf(step);
  return (
    <motion.div
      className="fixed inset-0 z-50 flex flex-col justify-end bg-ink p-6 text-paper md:p-14"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <p className="label !text-paper/50">Analyzing</p>
      <div className="mt-6 space-y-4">
        {STEP_ORDER.map((s, i) => (
          <motion.p
            key={s}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: i <= idx ? 1 : 0.2, x: 0 }}
            transition={{ delay: i * 0.08 }}
            className="flex items-center gap-4 text-xl font-bold tracking-tight md:text-4xl"
          >
            <span className={`inline-block h-3 w-3 ${i < idx ? "bg-paper" : i === idx ? "animate-pulse bg-accent" : "bg-paper/20"}`} />
            {STEP_TEXT[s]}
          </motion.p>
        ))}
      </div>
      <div className="mt-10 h-[3px] w-full bg-paper/10">
        <motion.div className="h-full bg-accent" animate={{ width: `${((idx + 1) / STEP_ORDER.length) * 100}%` }} transition={{ duration: 0.6 }} />
      </div>
    </motion.div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="label mb-3">{label}</p>
      {children}
    </div>
  );
}

function Select({
  value, onChange, options, suffix, disabled,
}: { value: number; onChange: (v: number) => void; options: number[]; suffix: string; disabled?: boolean }) {
  return (
    <div className="relative">
      <select
        className="field appearance-none pr-8 font-semibold disabled:bg-smoke disabled:text-mute"
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(Number(e.target.value))}
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
            {suffix}
          </option>
        ))}
      </select>
      <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs">▼</span>
    </div>
  );
}

function FaceIcon() {
  return (
    <svg width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" strokeWidth="1.5" className="mx-auto" aria-hidden>
      <path d="M8 18V8h10M46 8h10v10M56 46v10H46M18 56H8V46" strokeWidth="2.5" />
      <ellipse cx="32" cy="31" rx="13" ry="16" />
      <circle cx="27" cy="28" r="1.5" fill="currentColor" />
      <circle cx="37" cy="28" r="1.5" fill="currentColor" />
      <path d="M28 38c2.5 2 5.5 2 8 0" />
    </svg>
  );
}
