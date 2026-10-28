"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import HeroArt from "@/components/HeroArt";
import { useAuth } from "@/lib/auth/AuthProvider";
import { runEngineA } from "@/lib/saju/engineA";
import { runEngineB } from "@/lib/saju/engineB";
import { computeSaju } from "@/lib/saju/consensus";
import { BRANCH_ELEMENT, BRANCH_KO, ELEMENT_COLOR_NAME, STEM_ELEMENT, STEM_KO, type Element } from "@/lib/saju/constants";
import type { BirthInput, PillarKey } from "@/lib/saju/types";
import { THEMES } from "@/lib/reading/themes";

/* ───────── 그림: 오른쪽에 고정된 무대 ───────── */

export type Pic = { key: string; src: string; w: number; h: number; alt: string; caption: string; pos: string };

export const PICS: Pic[] = [
  {
    key: "yun",
    src: "/pictures/yun-duseo.jpg",
    w: 1200,
    h: 2247,
    alt: "윤두서 자화상. 수염을 한 올씩 그린 얼굴이 정면을 똑바로 바라본다",
    caption: "윤두서 자화상, 18세기 초. 얼굴 하나에 사람의 정신을 담으려 한 조선 초상화",
    pos: "50% 22%",
  },
  {
    key: "star",
    src: "/pictures/star-chart.jpg",
    w: 760,
    h: 900,
    alt: "검은 돌에 새긴 천상열차분야지도의 둥근 별자리 그림",
    caption: "천상열차분야지도 복각비. 1395년 조선의 하늘을 돌에 새긴 별자리 지도",
    pos: "50% 50%",
  },
  {
    key: "chart",
    src: "/pictures/face-chart-1817.jpg",
    w: 1200,
    h: 1882,
    alt: "얼굴의 이마·눈·코·입 자리에 한자로 이름을 적은 옛 목판 얼굴 그림",
    caption: "면부찰색도, 1817년 목판본. 얼굴의 자리마다 이름을 붙여 읽었다",
    pos: "50% 8%",
  },
  {
    key: "yeongjo",
    src: "/pictures/yeongjo.jpg",
    w: 1200,
    h: 2139,
    alt: "붉은 곤룡포에 익선관을 쓴 영조의 반신 초상",
    caption: "영조 어진. 1744년 원본을 1900년에 옮겨 그린 임금의 초상",
    pos: "50% 30%",
  },
];

/** 구획이 화면 가운데에 오면 그 구획의 그림으로 천천히 바뀐다. 등장 효과도 여기서 켠다. */
export function Stage() {
  const [on, setOn] = useState(PICS[0].key);

  useEffect(() => {
    const root = document.documentElement;
    root.classList.add("rise-on");
    const rise = new IntersectionObserver(
      (es) =>
        es.forEach((e) => {
          if (!e.isIntersecting) return;
          e.target.classList.add("in");
          rise.unobserve(e.target);
        }),
      { rootMargin: "0px 0px -8% 0px" },
    );
    document.querySelectorAll("[data-rise]").forEach((el) => rise.observe(el));

    const secs = new IntersectionObserver(
      (es) => es.forEach((e) => e.isIntersecting && setOn((e.target as HTMLElement).dataset.pic!)),
      { rootMargin: "-45% 0px -45% 0px" },
    );
    document.querySelectorAll("[data-pic]").forEach((el) => secs.observe(el));
    return () => {
      rise.disconnect();
      secs.disconnect();
      root.classList.remove("rise-on");
    };
  }, []);

  return (
    <div className="stage">
      {PICS.map((p, i) => (
        <figure key={p.key} data-on={p.key === on}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={p.src} width={p.w} height={p.h} alt={p.alt} style={{ objectPosition: p.pos }} loading={i === 0 ? "eager" : "lazy"} decoding="async" />
        </figure>
      ))}
      <p className="stage-caption" aria-live="polite">{PICS.find((p) => p.key === on)!.caption}</p>
    </div>
  );
}

/** 휴대폰에서는 고정 무대 대신 구획마다 그림이 한 장씩 들어간다 */
export function InlinePic({ k, className = "" }: { k: string; className?: string }) {
  const p = PICS.find((x) => x.key === k)!;
  return (
    <figure className={`pic-inline ${className}`}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={p.src} width={p.w} height={p.h} alt={p.alt} style={{ objectPosition: p.pos }} loading={k === "yun" ? "eager" : "lazy"} decoding="async" />
      <figcaption className="caption">{p.caption}</figcaption>
    </figure>
  );
}

/* ───────── 표지 카드의 링크 줄 ───────── */

export function CoverLinks() {
  const { user, enabled, signOut } = useAuth();
  return (
    <nav className="cover-links" aria-label="바로가기">
      <a className="link" href="#how">어떻게 보나요</a>
      <Link className="link" href="/match">궁합 보기</Link>
      <a className="link" href="#faq">자주 묻는 질문</a>
      {enabled &&
        (user ? (
          <button type="button" className="link" onClick={signOut}>
            로그아웃
          </button>
        ) : (
          <Link className="link" href="/login">로그인</Link>
        ))}
    </nav>
  );
}

export function DevMark() {
  const branch = process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_REF;
  if (!branch || branch === "main") return null;
  return <span className="small" style={{ color: "var(--warn)", marginLeft: 10 }}>개발 버전</span>;
}

/* ───────── 살아 있는 것: 두 엔진이 계산한 여덟 글자 ───────── */

const ORDER: PillarKey[] = ["hour", "day", "month", "year"];
const COL_LABEL: Record<PillarKey, string> = { hour: "시", day: "일", month: "월", year: "년" };
const thisYear = new Date().getFullYear();
const YEARS = Array.from({ length: 100 }, (_, i) => thisYear - i);
const range = (a: number, b: number) => Array.from({ length: b - a + 1 }, (_, i) => a + i);
// 시진: 자시(23~1시)부터 두 시간 간격, 대표 시각으로 계산
const HOURS: { v: number; label: string }[] = [
  { v: -1, label: "모름" },
  ...["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"].map((n, i) => {
    const h = (i * 2 + 24) % 24;
    return { v: h, label: `${n}시 ${String((h + 23) % 24).padStart(2, "0")}~${String((h + 1) % 24).padStart(2, "0")}시` };
  }),
];

function pillarsOf(input: BirthInput) {
  try {
    return { a: runEngineA(input).out.pillars, b: runEngineB(input).pillars };
  } catch {
    return null;
  }
}

const readKo = (g: string) => `${STEM_KO[g[0]] ?? ""}${BRANCH_KO[g[1]] ?? ""}`;
const elOf = (g: string) => `${ELEMENT_COLOR_NAME[STEM_ELEMENT[g[0]]] ?? ""}·${ELEMENT_COLOR_NAME[BRANCH_ELEMENT[g[1]]] ?? ""}`;

export function EightChars() {
  const [cal, setCal] = useState<"solar" | "lunar">("solar");
  const [year, setYear] = useState(1990);
  const [month, setMonth] = useState(5);
  const [day, setDay] = useState(17);
  const [hour, setHour] = useState(12);
  const maxDay = cal === "lunar" ? 30 : new Date(year, month, 0).getDate();
  const d = Math.min(day, maxDay);

  const res = useMemo(
    () => pillarsOf({ year, month, day: d, hour: hour < 0 ? null : hour, minute: 0, calendar: cal, leap: false, gender: "남" }),
    [year, month, d, hour, cal],
  );
  const known = hour >= 0;
  const keys = known ? ORDER : ORDER.filter((k) => k !== "hour");
  const agreed = res ? keys.reduce((n, k) => n + [0, 1].filter((i) => res.a[k][i] === res.b[k][i]).length, 0) : 0;
  const href = `/analyze?y=${year}&m=${month}&d=${d}&cal=${cal}&h=${known ? hour : "none"}`;

  return (
    <>
      <div className="seg-row">
        <div className="seg" role="group" aria-label="달력">
          <button type="button" aria-pressed={cal === "solar"} onClick={() => setCal("solar")}>양력</button>
          <button type="button" aria-pressed={cal === "lunar"} onClick={() => setCal("lunar")}>음력</button>
        </div>
      </div>
      <div className="controls">
        <label>
          태어난 해
          <select value={year} onChange={(e) => setYear(Number(e.target.value))}>
            {YEARS.map((y) => <option key={y} value={y}>{y}년</option>)}
          </select>
        </label>
        <label>
          달
          <select value={month} onChange={(e) => setMonth(Number(e.target.value))}>
            {range(1, 12).map((m) => <option key={m} value={m}>{m}월</option>)}
          </select>
        </label>
        <label>
          날
          <select value={d} onChange={(e) => setDay(Number(e.target.value))}>
            {range(1, maxDay).map((x) => <option key={x} value={x}>{x}일</option>)}
          </select>
        </label>
        <label className="wide">
          태어난 시간
          <select value={hour} onChange={(e) => setHour(Number(e.target.value))}>
            {HOURS.map((h) => <option key={h.v} value={h.v}>{h.label}</option>)}
          </select>
        </label>
      </div>

      <div className="board" data-ui aria-live="polite">
        {res ? (
          <>
            <table>
              <caption className="sr-only">두 사주 엔진이 계산한 네 기둥과 두 엔진이 같은 값을 낸 글자</caption>
              <thead>
                <tr>
                  <th scope="col"><span className="sr-only">엔진</span></th>
                  {ORDER.map((k) => <th key={k} scope="col">{COL_LABEL[k]}주</th>)}
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="row">엔진 A · ssaju</th>
                  {ORDER.map((k) => <td key={k} className={known || k !== "hour" ? (res.a[k] === res.b[k] ? "" : "off") : ""}>{known || k !== "hour" ? res.a[k] : "—"}</td>)}
                </tr>
                <tr>
                  <th scope="row">엔진 B · lunar</th>
                  {ORDER.map((k) => <td key={k} className={known || k !== "hour" ? (res.a[k] === res.b[k] ? "" : "off") : ""}>{known || k !== "hour" ? res.b[k] : "—"}</td>)}
                </tr>
                <tr className="final">
                  <th scope="row">쓰는 글자</th>
                  {ORDER.map((k) =>
                    !known && k === "hour" ? (
                      <td key={k} className="held">시간 모름</td>
                    ) : res.a[k] === res.b[k] ? (
                      <td key={k}>
                        {res.a[k]}
                        <small title={elOf(res.a[k])}>{readKo(res.a[k])}</small>
                      </td>
                    ) : (
                      <td key={k} className="held">판단 보류</td>
                    ),
                  )}
                </tr>
              </tbody>
            </table>
            <div className="foot">
              <span>두 엔진이 같은 글자 {agreed} / {keys.length * 2}</span>
              <span>나(일간) {res.a.day[0]} · {ELEMENT_COLOR_NAME[STEM_ELEMENT[res.a.day[0]]]}</span>
            </div>
          </>
        ) : (
          <p className="foot">이 날짜는 계산할 수 없어요. 음력이면 날짜를 다시 확인해 주세요.</p>
        )}
      </div>

      <div className="after">
        <Link href={href} className="btn-lp">
          이 생일로 이어서 보기
          <span className="bars" aria-hidden><i /><i /><i /></span>
        </Link>
      </div>
    </>
  );
}

/* ───────── 어떻게 보나요: 네 단계를 끌어서 넘긴다 ───────── */

const STAGES = [
  {
    name: "두 번 계산",
    clause: "먼저, 사주를 두 번 계산합니다",
    text: "서로 다른 두 만세력 엔진에 같은 생년월일을 넣습니다. 여덟 글자가 같게 나온 칸만 해석에 쓰고, 다르면 ‘판단 보류’로 남깁니다.",
  },
  {
    name: "얼굴 478점",
    clause: "다음, 얼굴의 478점을 잽니다",
    text: "사진 속 얼굴에서 점 478개를 찾아 이마·눈·코·입·턱의 비율을 잽니다. 이 계산은 휴대폰 브라우저 안에서 끝나고, 사진은 서버로 가지 않습니다.",
  },
  {
    name: "겹치는 것만",
    clause: "그리고, 겹치는 말만 남깁니다",
    text: "사주가 가리키는 성향과 관상이 가리키는 성향을 아홉 가지 테마로 맞춰 봅니다. 양쪽이 함께 가리킨 것만 ‘우리 의견’이 됩니다.",
  },
  {
    name: "읽어 드림",
    clause: "끝으로, 처음부터 읽어 드립니다",
    text: "성격부터 재물, 연애, 건강, 앞으로 3년, 주의할 점까지 이어집니다. 재생 버튼 하나면 AI 목소리가 끝까지 읽어 줍니다.",
  },
];

const SAMPLE: BirthInput = { year: 1990, month: 5, day: 17, hour: 12, minute: 0, calendar: "solar", leap: false, gender: "남" };

export function HowSlider() {
  const [i, setI] = useState(0);
  const sample = useMemo(() => pillarsOf(SAMPLE), []);
  const s = STAGES[i];

  return (
    <>
      <div className="how-field">
        <div data-on={i === 0} aria-hidden={i !== 0}>
          <div className="ui" data-ui>
            <div className="ui-pad">
              <p className="ui-title">예시 · 1990년 5월 17일 낮 12시</p>
              {sample &&
                (["a", "b"] as const).map((e) => (
                  <div className="row" key={e}>
                    <span>{e === "a" ? "엔진 A · ssaju" : "엔진 B · lunar"}</span>
                    <span className="hanja">{ORDER.map((k) => sample[e][k]).join(" ")}</span>
                  </div>
                ))}
              <div className="row">
                <span>같은 글자</span>
                <span className="tag">8 / 8 · 모두 씀</span>
              </div>
            </div>
          </div>
        </div>
        <div data-on={i === 1} aria-hidden={i !== 1}>
          <div data-ui style={{ display: "grid", placeItems: "center" }}>
            <HeroArt className="mesh" color="#2f737d" keyColor="#06525c" />
          </div>
        </div>
        <div data-on={i === 2} aria-hidden={i !== 2}>
          <div className="ui" data-ui>
            <div className="ui-pad">
              <p className="ui-title">예시 · 테마 맞춰 보기</p>
              {[
                { t: THEMES.expression.label, s: true, f: true },
                { t: THEMES.willpower.label, s: true, f: true },
                { t: THEMES.wealth.label, s: true, f: false },
                { t: THEMES.sensitivity.label, s: false, f: true },
              ].map((r) => (
                <div className="row" key={r.t}>
                  <span>
                    {r.t}
                    <br />
                    <span style={{ color: "#5b7175", fontSize: 13 }}>
                      사주 {r.s ? "○" : "—"} · 관상 {r.f ? "○" : "—"}
                    </span>
                  </span>
                  <span className={`tag ${r.s && r.f ? "" : "no"}`} style={{ alignSelf: "center" }}>
                    {r.s && r.f ? "남김" : "뺌"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div data-on={i === 3} aria-hidden={i !== 3}>
          <div className="ui" data-ui>
            <div className="ui-pad">
              <div className="player">
                <span className="play" aria-hidden>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M7 4v16l13-8z" /></svg>
                </span>
                <div style={{ flex: 1 }}>
                  <p className="ui-title">전체 풀이 듣기</p>
                  <div className="bar"><i /></div>
                  <p className="num" style={{ marginTop: 6, color: "#5b7175", fontSize: 13 }}>2:06 / 6:10</p>
                </div>
              </div>
              <div style={{ marginTop: 12 }}>
                {[
                  ["성격 · 강점", "0:00"],
                  ["재물 · 직업", "1:12"],
                  ["연애 · 인간관계", "2:04"],
                  ["건강", "3:01"],
                  ["앞으로 3년", "3:48"],
                ].map(([t, at], n) => (
                  <div className="row" key={t} style={n === 2 ? { fontWeight: 700, color: "#06525c" } : undefined}>
                    <span>{t}</span>
                    <span className="num">{at}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="track" style={{ ["--fill" as string]: `${(i / 3) * 100}%` }}>
        <span className="rail" aria-hidden />
        <span className="fill" aria-hidden />
        <input
          type="range"
          min={0}
          max={3}
          step={1}
          value={i}
          onChange={(e) => setI(Number(e.target.value))}
          aria-label="단계"
          aria-valuetext={`${i + 1}단계, ${s.name}`}
        />
      </div>
      <div className="stops">
        {STAGES.map((x, n) => (
          <button key={x.name} type="button" aria-current={n === i} onClick={() => setI(n)}>
            {x.name}
          </button>
        ))}
      </div>
      <p className="head clause" aria-live="polite">{s.clause}</p>
      <p className="clause-text">{s.text}</p>
    </>
  );
}

/* ───────── 결과지 목록 ───────── */

type SheetDoc = { name: string; title: string; lede: string; src: string[]; body: string[] };

export function SheetIndex() {
  const saju = useMemo(() => {
    try {
      return computeSaju(SAMPLE);
    } catch {
      return null;
    }
  }, []);
  const years = saju?.years ?? [];
  const [topEl, topN] = saju ? (Object.entries(saju.fiveElements) as [Element, number][]).sort((a, b) => b[1] - a[1])[0] : (["화", 5] as [Element, number]);
  const docs: SheetDoc[] = [
    {
      name: "성격 · 강점",
      title: "말과 결과물로 자신을 드러낼 때 가장 빛납니다",
      lede: THEMES.expression.trait,
      src: ["사주: 표현의 기운(식신·상관)이 두 자리에 있습니다", "관상: 입이 넓고 입꼬리가 올라가 있습니다"],
      body: [THEMES.willpower.trait],
    },
    {
      name: "재물 · 직업",
      title: "드러내는 일, 오래 쌓는 일에 운이 붙습니다",
      lede: THEMES.expression.career,
      src: ["사주: 표현과 의지의 기운이 함께 강합니다", "관상: 턱이 넓고 단단해 끈기가 보입니다"],
      body: [THEMES.willpower.career],
    },
    {
      name: "연애 · 인간관계",
      title: "솔직한 표현이 가장 큰 매력입니다",
      lede: THEMES.expression.love,
      src: ["사주: 일지에 표현의 기운이 앉아 있습니다", "관상: 눈매가 부드럽고 입술이 도톰합니다"],
      body: [THEMES.willpower.love],
    },
    {
      name: "건강",
      title: "쉬는 날을 달력에 먼저 적어 두세요",
      lede: `${ELEMENT_COLOR_NAME[topEl]} 기운이 강해 그쪽 장기에 무리가 가지 않도록 생활 리듬을 조절하세요.`,
      src: [`사주: 여덟 글자 중 ${ELEMENT_COLOR_NAME[topEl]}(${topEl})의 기운이 ${topN}자리입니다`, "관상: 이 항목은 사주만 봅니다"],
      body: [
        "에너지가 넘치는 만큼 과로를 과로로 느끼지 못할 수 있습니다.",
        "건강 내용은 오락용 참고이며, 몸에 이상이 있다면 반드시 의료 전문가와 상담하세요.",
      ],
    },
    {
      name: "앞으로 3년",
      title: "해마다 들어오는 기운이 다릅니다",
      lede: "올해부터 3년, 그해의 간지가 나에게 어떤 역할로 들어오는지 봅니다.",
      src: years.map((y) => `${y.year}년 ${y.ganzhi}(${readKo(y.ganzhi)}) · ${y.tenGod}의 해`),
      body: ["실제 결과에는 이번 달부터 12달의 흐름과 앞으로 2주의 좋은 날도 함께 나옵니다."],
    },
  ];
  const [sel, setSel] = useState(0);
  const [shown, setShown] = useState(0);
  const [fading, setFading] = useState(false);

  useEffect(() => {
    if (sel === shown) return;
    setFading(true);
    const t = setTimeout(() => {
      setShown(sel);
      setFading(false);
    }, 200);
    return () => clearTimeout(t);
  }, [sel, shown]);

  const doc = docs[shown];
  return (
    <>
      <div className="index">
        <h2 className="head" data-rise>결과지에 담기는 것</h2>
        <ul data-rise style={{ ["--i" as string]: 1 }}>
          {docs.map((x, n) => (
            <li key={x.name}>
              <button type="button" aria-pressed={n === sel} onClick={() => setSel(n)}>
                {x.name}
              </button>
            </li>
          ))}
        </ul>
        <p className="intro" data-rise style={{ ["--i" as string]: 2 }}>
          예시 결과지입니다. 실제 결과에는 타고난 기운, 행운의 색·숫자·날, 인생의 큰 흐름과 주의사항까지 이어집니다.
        </p>
      </div>
      <div className="sheet-stage" data-rise style={{ ["--i" as string]: 1 }}>
        <article className="sheet" data-ui data-fading={fading} aria-live="polite">
          <div className="meta">
            <span>얼굴과 운명 · 예시 결과지</span>
            <span>1990. 5. 17 낮 12시</span>
          </div>
          <h3>{doc.title}</h3>
          <p className="lede">{doc.lede}</p>
          <div className="src">
            {doc.src.map((s) => (
              <p key={s}>
                <b>○</b> {s}
              </p>
            ))}
          </div>
          {doc.body.map((b) => (
            <p className="body" key={b}>{b}</p>
          ))}
        </article>
      </div>
    </>
  );
}

/* ───────── 마지막: 열려 있는 첫 단계 ───────── */

/** 1990. 5. 17 / 1990-05-17 / 19900517 / 1990년 5월 17일 … 무엇이든 받는다 */
function parseDate(s: string): { y: number; m: number; d: number } | null {
  const digits = s.replace(/\s/g, "");
  let y: number, m: number, d: number;
  if (/^\d{8}$/.test(digits)) {
    y = +digits.slice(0, 4);
    m = +digits.slice(4, 6);
    d = +digits.slice(6, 8);
  } else {
    const n = s.match(/\d+/g);
    if (!n || n.length < 3) return null;
    [y, m, d] = n.map(Number);
    if (y < 100) y += y > thisYear % 100 ? 1900 : 2000;
  }
  if (y < thisYear - 99 || y > thisYear || m < 1 || m > 12 || d < 1 || d > 31) return null;
  return { y, m, d };
}

export function StartDialog() {
  const router = useRouter();
  const [text, setText] = useState("1990. 5. 17");
  const [cal, setCal] = useState<"solar" | "lunar">("solar");
  const [bad, setBad] = useState(false);

  const go = (e: React.FormEvent) => {
    e.preventDefault();
    const p = parseDate(text);
    if (!p) return setBad(true);
    router.push(`/analyze?y=${p.y}&m=${p.m}&d=${p.d}&cal=${cal}`);
  };

  return (
    <form className="dialog" data-ui onSubmit={go} data-rise style={{ ["--i" as string]: 2 }}>
      <h3>생일이 언제예요?</h3>
      <p>사주는 생일과 태어난 시간으로 봐요.</p>
      <label htmlFor="birth">생년월일</label>
      <input
        id="birth"
        type="text"
        inputMode="numeric"
        autoComplete="bday"
        value={text}
        onChange={(e) => {
          setText(e.target.value);
          setBad(false);
        }}
        aria-describedby="birth-hint"
        aria-invalid={bad}
      />
      <p id="birth-hint" className={`hint ${bad ? "bad" : ""}`}>
        {bad ? "연·월·일을 숫자로 적어 주세요. 예: 1990. 5. 17" : "1990-05-17, 19900517처럼 적어도 돼요"}
      </p>
      <div className="seg" role="group" aria-label="달력">
        <button type="button" aria-pressed={cal === "solar"} onClick={() => setCal("solar")}>양력</button>
        <button type="button" aria-pressed={cal === "lunar"} onClick={() => setCal("lunar")}>음력</button>
      </div>
      <button type="submit" className="go">이어서 시작하기</button>
    </form>
  );
}
