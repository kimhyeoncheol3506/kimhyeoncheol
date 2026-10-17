"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { Back } from "@/components/Header";
import { Q, Select, Working } from "@/components/FunnelUI";
import { preloadLandmarker } from "@/lib/face/landmarker";
import { NoFaceError } from "@/lib/analyze";
import { RELATIONS, type Relation } from "@/lib/match/compute";
import { MATCH_KEY, runMatch } from "@/lib/match/run";

const thisYear = new Date().getFullYear();
const YEARS = Array.from({ length: 100 }, (_, i) => thisYear - i);
const range = (a: number, b: number) => Array.from({ length: b - a + 1 }, (_, i) => a + i);

const STEPS = ["relation", "me", "partner", "photo", "worry"] as const;
type Step = (typeof STEPS)[number];

type P = {
  name: string;
  gender: "남" | "여" | null;
  calendar: "solar" | "lunar";
  leap: boolean;
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  timeKnown: boolean;
  photo: File | null;
  preview: string | null;
};
const blank = (year: number): P => ({ name: "", gender: null, calendar: "solar", leap: false, year, month: 1, day: 1, hour: 12, minute: 0, timeKnown: true, photo: null, preview: null });

export default function MatchPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("relation");
  const [relation, setRelation] = useState<Relation | null>(null);
  const [me, setMe] = useState<P>(blank(1995));
  const [partner, setPartner] = useState<P>(blank(1995));
  const [worry, setWorry] = useState("");
  const [working, setWorking] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => preloadLandmarker(), []);

  const idx = STEPS.indexOf(step);
  const go = (s: Step) => {
    setError(null);
    setStep(s);
    window.scrollTo(0, 0);
  };
  const back = () => (idx === 0 ? router.push("/") : go(STEPS[idx - 1]));
  const ready = (p: P) => Boolean(p.gender);
  const clearPhotos = () => {
    for (const p of [me, partner]) if (p.preview) URL.revokeObjectURL(p.preview);
    setMe((p) => ({ ...p, photo: null, preview: null }));
    setPartner((p) => ({ ...p, photo: null, preview: null }));
  };

  const run = async (withPhoto: boolean) => {
    if (!relation || !me.gender || !partner.gender) return;
    setError(null);
    const toInput = (p: P) => ({
      name: p.name,
      photo: withPhoto ? p.photo : null,
      birth: { year: p.year, month: p.month, day: p.day, hour: p.timeKnown ? p.hour : null, minute: p.minute, calendar: p.calendar, leap: p.calendar === "lunar" && p.leap, gender: p.gender! },
    });
    try {
      const result = await runMatch(toInput(me), toInput(partner), relation, worry, setWorking);
      clearPhotos();
      sessionStorage.setItem(MATCH_KEY, JSON.stringify(result));
      router.push("/match/result");
    } catch (e) {
      setWorking(null);
      if (e instanceof NoFaceError) {
        go("photo");
        setError(`${e.message} 사진에서 얼굴을 찾지 못했어요. 한 사람만 나온 밝은 정면 사진으로 다시 골라 주세요.`);
      } else {
        console.error(e);
        setError("잠시 문제가 생겼어요. 다시 한 번 눌러 주세요.");
      }
    }
  };

  return (
    <div className="min-h-screen px-5">
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
        <motion.div key={step} initial={{ opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -24 }} transition={{ duration: 0.25 }} className="pb-44 pt-8">
          {step === "relation" && (
            <>
              <Q title="두 사람은 어떤 사이예요?" sub="사이에 맞춰 풀이와 좋은 때를 골라 드려요." />
              <div className="mt-8 space-y-2">
                {RELATIONS.map((r) => (
                  <button
                    key={r.id}
                    type="button"
                    data-on={relation === r.id}
                    className="chip h-14 w-full justify-start px-5 text-[17px]"
                    onClick={() => {
                      setRelation(r.id);
                      setTimeout(() => go("me"), 150);
                    }}
                  >
                    {r.label}
                  </button>
                ))}
              </div>
            </>
          )}

          {step === "me" && (
            <>
              <Q title="먼저 내 정보를 알려 주세요" sub="이름은 결과 화면에만 쓰여요." />
              <PersonFields p={me} set={setMe} namePlaceholder="내 이름 (선택)" />
            </>
          )}

          {step === "partner" && (
            <>
              <Q title="이제 그 사람 정보를 알려 주세요" sub="정확한 시간을 몰라도 생일만으로 볼 수 있어요." />
              <PersonFields p={partner} set={setPartner} namePlaceholder="그 사람 이름 (선택)" />
            </>
          )}

          {step === "photo" && (
            <>
              <Q title="두 사람 얼굴도 볼까요?" sub="둘 다 넣으면 관상 궁합까지 봐요. 사진은 이 폰 안에서만 쓰고 바로 지워요." />
              <div className="mt-8 grid grid-cols-2 gap-3">
                <PhotoSlot label={me.name || "나"} p={me} set={setMe} />
                <PhotoSlot label={partner.name || "그 사람"} p={partner} set={setPartner} />
              </div>
            </>
          )}

          {step === "worry" && (
            <>
              <Q title="요즘 둘 사이에 마음 쓰이는 게 있어요?" sub="있으면 편하게 적어 주세요. 이 폰 안에서 풀이에만 쓰고 어디에도 보내지 않아요." />
              <textarea
                className="field mt-8 h-40 resize-none py-4 leading-relaxed"
                maxLength={300}
                placeholder="한 줄이어도 괜찮아요. 예: 연락 문제로 자주 다퉈요"
                value={worry}
                onChange={(e) => setWorry(e.target.value)}
              />
              <p className="mt-2 text-right text-[13px] text-mute">{worry.length} / 300</p>
              <p className="mt-6 text-center text-[13px] text-mute">
                시작하면 <Link href="/disclaimer" className="underline">면책조항</Link>과{" "}
                <Link href="/privacy" className="underline">개인정보처리방침</Link>에 동의한 것으로 봐요.
              </p>
            </>
          )}

          {error && <p className="mt-6 rounded-2xl bg-warn/10 px-4 py-3 text-[15px] font-medium text-warn">{error}</p>}
        </motion.div>
      </AnimatePresence>

      <div className="bottom-cta space-y-2">
        {step === "relation" && (
          <button className="btn-primary w-full" disabled={!relation} onClick={() => go("me")}>
            다음
          </button>
        )}
        {step === "me" && (
          <button className="btn-primary w-full" disabled={!ready(me)} onClick={() => go("partner")}>
            {ready(me) ? "다음" : "성별을 골라 주세요"}
          </button>
        )}
        {step === "partner" && (
          <button className="btn-primary w-full" disabled={!ready(partner)} onClick={() => go("photo")}>
            {ready(partner) ? "다음" : "성별을 골라 주세요"}
          </button>
        )}
        {step === "photo" && (
          <>
            <button className="btn-primary w-full" disabled={!me.photo || !partner.photo} onClick={() => go("worry")}>
              {me.photo && partner.photo ? "다음" : "두 사람 사진을 모두 넣어 주세요"}
            </button>
            <button
              className="btn-ghost w-full"
              onClick={() => {
                clearPhotos();
                go("worry");
              }}
            >
              사진 없이 사주로만 볼게요
            </button>
          </>
        )}
        {step === "worry" && (
          <>
            <button className="btn-primary w-full" disabled={working !== null} onClick={() => run(true)}>
              궁합 결과 보기
            </button>
            {!worry && (
              <button className="btn-ghost w-full" disabled={working !== null} onClick={() => run(true)}>
                괜찮아요, 넘어갈게요
              </button>
            )}
          </>
        )}
      </div>

      <AnimatePresence>{working && <Working text={working} />}</AnimatePresence>
    </div>
  );
}

function PersonFields({ p, set, namePlaceholder }: { p: P; set: React.Dispatch<React.SetStateAction<P>>; namePlaceholder: string }) {
  const up = (patch: Partial<P>) => set((x) => ({ ...x, ...patch }));
  const maxDay = useMemo(() => (p.calendar === "lunar" ? 30 : new Date(p.year, p.month, 0).getDate()), [p.calendar, p.year, p.month]);
  useEffect(() => {
    if (p.day > maxDay) set((x) => ({ ...x, day: maxDay }));
  }, [maxDay, p.day, set]);

  return (
    <div className="mt-8 space-y-6">
      <input className="field" maxLength={10} placeholder={namePlaceholder} value={p.name} onChange={(e) => up({ name: e.target.value })} />

      <div>
        <p className="mb-2 text-[14px] font-semibold text-mute">성별</p>
        <div className="grid grid-cols-2 gap-2">
          {(["남", "여"] as const).map((g) => (
            <button key={g} type="button" className="chip h-12" data-on={p.gender === g} onClick={() => up({ gender: g })}>
              {g === "남" ? "남성" : "여성"}
            </button>
          ))}
        </div>
      </div>

      <div>
        <p className="mb-2 text-[14px] font-semibold text-mute">생일</p>
        <div className="flex gap-2">
          <button type="button" className="chip" data-on={p.calendar === "solar"} onClick={() => up({ calendar: "solar" })}>
            양력
          </button>
          <button type="button" className="chip" data-on={p.calendar === "lunar"} onClick={() => up({ calendar: "lunar" })}>
            음력
          </button>
        </div>
        <div className="mt-3 grid grid-cols-[1.3fr_1fr_1fr] gap-2">
          <Select value={p.year} onChange={(v) => up({ year: v })} options={YEARS} suffix="년" label="태어난 해" />
          <Select value={p.month} onChange={(v) => up({ month: v })} options={range(1, 12)} suffix="월" label="태어난 달" />
          <Select value={p.day} onChange={(v) => up({ day: v })} options={range(1, maxDay)} suffix="일" label="태어난 날" />
        </div>
        {p.calendar === "lunar" && (
          <label className="mt-3 flex items-center gap-2 text-[15px] text-sub">
            <input type="checkbox" checked={p.leap} onChange={(e) => up({ leap: e.target.checked })} className="h-5 w-5 accent-accent" />
            윤달이에요
          </label>
        )}
      </div>

      <div>
        <p className="mb-2 text-[14px] font-semibold text-mute">태어난 시간</p>
        {p.timeKnown && (
          <div className="grid grid-cols-2 gap-2">
            <Select value={p.hour} onChange={(v) => up({ hour: v })} options={range(0, 23)} suffix="시" label="태어난 시" />
            <Select value={p.minute} onChange={(v) => up({ minute: v })} options={range(0, 59)} suffix="분" label="태어난 분" />
          </div>
        )}
        <label className="mt-3 flex items-center gap-2 text-[15px] text-sub">
          <input type="checkbox" checked={!p.timeKnown} onChange={(e) => up({ timeKnown: !e.target.checked })} className="h-5 w-5 accent-accent" />
          시간을 몰라요
        </label>
      </div>
    </div>
  );
}

function PhotoSlot({ label, p, set }: { label: string; p: P; set: React.Dispatch<React.SetStateAction<P>> }) {
  const ref = useRef<HTMLInputElement>(null);
  const pick = (f: File | undefined) => {
    if (!f || !f.type.startsWith("image/")) return;
    if (p.preview) URL.revokeObjectURL(p.preview);
    set((x) => ({ ...x, photo: f, preview: URL.createObjectURL(f) }));
  };
  return (
    <button type="button" onClick={() => ref.current?.click()} className="relative flex aspect-[3/4] flex-col items-center justify-center overflow-hidden rounded-card bg-smoke text-center active:scale-[0.99]">
      {p.preview ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={p.preview} alt={`${label} 사진`} className="absolute inset-0 h-full w-full object-cover" />
      ) : (
        <>
          <span className="text-[34px]" aria-hidden>
            📷
          </span>
          <span className="mt-2 text-[15px] font-semibold text-sub">{label}</span>
          <span className="text-[13px] text-mute">사진 넣기</span>
        </>
      )}
      {p.preview && <span className="absolute bottom-2 left-2 rounded-full bg-ink/70 px-3 py-1 text-[13px] font-semibold text-paper">{label}</span>}
      <input ref={ref} type="file" accept="image/*" hidden onChange={(e) => pick(e.target.files?.[0])} />
    </button>
  );
}
