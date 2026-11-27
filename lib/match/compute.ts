// 궁합: 두 사람의 사주(각각 두 엔진이 합의한 값)와, 있으면 관상으로 궁합을 계산한다.
// 점수는 전통 궁합에서 보는 요소(일간 합, 일지 합·충·원진, 띠, 서로 부족한 기운을 채워 주는지, 앞으로의 흐름)로만 낸다.
import { BRANCHES, ELEMENT_COLOR_NAME, GENERATES, CONTROLS, tenGodOf, type Element } from "../saju/constants";
import type { SajuConsensus } from "../saju/types";
import type { FeatureScores } from "../face/physiognomy";
import { DAY_MASTER } from "../reading/compose";
import type { Section, SectionItem } from "../reading/types";

export const RELATIONS = [
  { id: "crush", label: "혼자 좋아하는 중" },
  { id: "some", label: "썸 타는 사이" },
  { id: "lover", label: "연인 사이" },
  { id: "married", label: "부부 사이" },
  { id: "ex", label: "헤어진 사이" },
] as const;
export type Relation = (typeof RELATIONS)[number]["id"];

export type Person = { name: string; gender: "남" | "여"; saju: SajuConsensus; face: FeatureScores | null };

export type MatchResult = {
  createdAt: string;
  relation: Relation;
  names: [string, string];
  total: number;
  headline: string;
  summary: string;
  scores: { key: string; label: string; value: number; note: string }[];
  leader: string; // 주도권
  bestMonth: string | null;
  sections: Section[];
  hasFace: boolean;
};

// ── 전통 궁합 관계표 ──────────────
const STEM_HAP = ["甲己", "乙庚", "丙辛", "丁壬", "戊癸"];
const BRANCH_HAP = ["子丑", "寅亥", "卯戌", "辰酉", "巳申", "午未"];
const SAMHAP = ["申子辰", "亥卯未", "寅午戌", "巳酉丑"];
const WONJIN = ["子未", "丑午", "寅酉", "卯申", "辰亥", "巳戌"];
const ZODIAC: Record<string, string> = { 子: "쥐", 丑: "소", 寅: "호랑이", 卯: "토끼", 辰: "용", 巳: "뱀", 午: "말", 未: "양", 申: "원숭이", 酉: "닭", 戌: "개", 亥: "돼지" };
const pair = (list: string[], a: string, b: string) => list.some((p) => (p[0] === a && p[1] === b) || (p[0] === b && p[1] === a));
const sameSamhap = (a: string, b: string) => a !== b && SAMHAP.some((g) => g.includes(a) && g.includes(b));
const chung = (a: string, b: string) => {
  const i = BRANCHES.indexOf(a as (typeof BRANCHES)[number]);
  const j = BRANCHES.indexOf(b as (typeof BRANCHES)[number]);
  return i >= 0 && j >= 0 && Math.abs(i - j) === 6;
};
const SCORE: Record<string, number> = { 식신: 2, 정재: 2, 정관: 2, 정인: 2, 편재: 1, 비견: 0, 편인: 0, 상관: -1, 겁재: -1, 편관: -1 };
const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, Math.round(v)));

/** 두 엔진이 합의한 기둥만 */
const pillar = (s: SajuConsensus, key: "year" | "day") => {
  const p = s.pillars.find((x) => x.key === key);
  return p && p.agreed && !p.unknown ? p : null;
};

// ── 상대가 나를 어떻게 보는가 (상대 일간 기준으로 본 내 일간) ──────────────
const VIEW: Record<string, string> = {
  비견: "편한 친구 같은 사람으로 봅니다. 대등하고 말이 잘 통하지만, 서로 양보는 어려울 수 있어요.",
  겁재: "자극을 주는 라이벌 같은 사람으로 봅니다. 끌리면서도 은근히 지고 싶지 않아 합니다.",
  식신: "돌봐 주고 싶은 사람으로 봅니다. 함께 있으면 마음이 편하고 뭐든 챙겨 주고 싶어 합니다.",
  상관: "자꾸 말을 걸고 싶은 사람으로 봅니다. 재미있지만 그만큼 잔소리도 늘 수 있어요.",
  편재: "설레고 갖고 싶은 사람으로 봅니다. 강하게 끌리지만 붙잡기 어렵다고 느낍니다.",
  정재: "곁에 오래 두고 싶은 사람으로 봅니다. 함께 미래를 그리고 싶어지는 상대입니다.",
  편관: "긴장되게 만드는 사람으로 봅니다. 강하게 끌리면서도 가끔은 버겁게 느낍니다.",
  정관: "믿고 기대고 싶은 사람으로 봅니다. 존중하고, 이 사람 앞에서는 잘 보이고 싶어 합니다.",
  편인: "알 듯 모를 듯한 사람으로 봅니다. 자꾸 생각나게 하고 깊이 빠져들게 합니다.",
  정인: "품어 주는 사람으로 봅니다. 함께 있으면 위로받고 보살핌을 받는 느낌입니다.",
};

const ACTION: Record<Relation, { best: string; worst: string }> = {
  crush: { best: "마음을 전하기 좋은 달", worst: "고백은 미루고 거리를 지키는 달" },
  some: { best: "관계를 한 단계 진전시키기 좋은 달", worst: "확인받으려 재촉하지 말아야 할 달" },
  lover: { best: "여행·기념일·미래 이야기를 하기 좋은 달", worst: "사소한 말다툼이 커지기 쉬운 달" },
  married: { best: "이사·재테크 같은 큰 결정을 함께하기 좋은 달", worst: "피로가 쌓여 서로 예민해지기 쉬운 달" },
  ex: { best: "다시 연락해 볼 만한 달", worst: "감정적으로 연락하면 후회하는 달" },
};

const hasBatchim = (w: string) => (w.charCodeAt(w.length - 1) - 0xac00) % 28 !== 0;
const eun = (w: string) => `${w}${hasBatchim(w) ? "은" : "는"}`;
const gwa = (w: string) => `${w}${hasBatchim(w) ? "과" : "와"}`;
/** "있음" → "있습니다", "통함" → "통합니다" */
const polite = (t: string) => {
  const s = t.replace(/함$/, "합니다").replace(/음$/, "습니다");
  return s.endsWith(".") ? s : `${s}.`;
};

export function computeMatch(a: Person, b: Person, relation: Relation, worry: string): MatchResult {
  const A = a.saju;
  const B = b.saju;
  const na = a.name || "나";
  const nb = b.name || "상대";
  const sa = A.dayMaster.stem;
  const sb = B.dayMaster.stem;
  const ea = A.dayMaster.element;
  const eb = B.dayMaster.element;
  const da = pillar(A, "day")?.branch ?? "";
  const db = pillar(B, "day")?.branch ?? "";
  const ya = pillar(A, "year")?.branch ?? "";
  const yb = pillar(B, "year")?.branch ?? "";

  const stemHap = pair(STEM_HAP, sa, sb);
  const dayHap = Boolean(da && db && pair(BRANCH_HAP, da, db));
  const daySam = Boolean(da && db && sameSamhap(da, db));
  const dayChung = Boolean(da && db && chung(da, db));
  const dayWon = Boolean(da && db && pair(WONJIN, da, db));
  const tgAB = tenGodOf(sa, sb); // 내가 상대를 보는 별
  const tgBA = tenGodOf(sb, sa); // 상대가 나를 보는 별
  const loveStar = (tg: string, g: "남" | "여") => (g === "남" ? ["정재", "편재"] : ["정관", "편관"]).includes(tg);

  // 1. 끌림
  let attraction = 10 + (stemHap ? 6 : 0) + (dayHap ? 4 : daySam ? 2 : 0) + (loveStar(tgAB, a.gender) ? 3 : 0) + (loveStar(tgBA, b.gender) ? 3 : 0) - (dayChung ? 3 : 0);
  // 2. 대화
  const gen = GENERATES[ea] === eb || GENERATES[eb] === ea;
  const ctl = CONTROLS[ea] === eb || CONTROLS[eb] === ea;
  let talk = 11 + (ea === eb ? 3 : 0) + (gen ? 5 : 0) - (ctl ? 2 : 0) - (dayWon ? 3 : 0);
  // 3. 서로 채워 줌: 내가 필요한 기운을 상대가 얼마나 가졌나
  const cover = (need: Element[], other: SajuConsensus) => (need.length ? Math.min(1, need.reduce((s, e) => s + other.fiveElements[e], 0) / 3) : 0.6);
  const covA = cover(A.yongsin, B);
  const covB = cover(B.yongsin, A);
  const fill = 4 + 16 * ((covA + covB) / 2);
  // 4. 생활
  const yearHap = Boolean(ya && yb && pair(BRANCH_HAP, ya, yb));
  const yearSam = Boolean(ya && yb && sameSamhap(ya, yb));
  const yearChung = Boolean(ya && yb && chung(ya, yb));
  const yearWon = Boolean(ya && yb && pair(WONJIN, ya, yb));
  const strong = (s: SajuConsensus) => s.strength === "strong";
  const weak = (s: SajuConsensus) => s.strength === "weak";
  let life = 12 + (yearHap || yearSam ? 4 : 0) - (yearChung ? 4 : 0) - (yearWon ? 2 : 0) - (dayChung ? 2 : 0) + ((strong(A) && weak(B)) || (weak(A) && strong(B)) ? 2 : 0) - (strong(A) && strong(B) ? 2 : 0);
  // 5. 앞으로: 올해·내년 두 사람의 흐름 + 12개월 중 함께 좋은 달
  const yearFlow = [0, 1].reduce((s, i) => s + (SCORE[A.years[i]?.tenGod] ?? 0) + (SCORE[B.years[i]?.tenGod] ?? 0), 0);
  const months = A.months
    .map((m) => {
      const o = B.months.find((x) => x.label === m.label);
      if (!o) return null;
      const bad = (da && chung(m.ganzhi[1], da)) || (db && chung(o.ganzhi[1], db));
      return { label: m.label, month: m.month, v: (SCORE[m.tenGod] ?? 0) + (SCORE[o.tenGod] ?? 0) - (bad ? 3 : 0), bad };
    })
    .filter(Boolean) as { label: string; month: number; v: number; bad: boolean }[];
  const goodMonths = months.filter((m) => m.v >= 3).length;
  let future = 10 + yearFlow * 1.2 + goodMonths * 0.6;

  // 관상 (두 사람 모두 사진이 있을 때)
  const hasFace = Boolean(a.face && b.face);
  if (a.face && b.face) {
    const fa = a.face;
    const fb = b.face;
    const keys = Object.keys(fa) as (keyof FeatureScores)[];
    const sim = 1 - keys.reduce((s, k) => s + Math.abs(fa[k] - fb[k]), 0) / keys.length;
    attraction += (sim - 0.75) * 12;
    if (fa.smile > 0.55 && fb.smile > 0.55) talk += 2;
  }

  attraction = clamp(attraction, 5, 20);
  talk = clamp(talk, 5, 20);
  const fillV = clamp(fill, 5, 20);
  life = clamp(life, 5, 20);
  future = clamp(future, 5, 20);
  const total = clamp(attraction + talk + fillV + life + future, 40, 99);

  // 주도권
  const power = (s: SajuConsensus, f: FeatureScores | null) =>
    (s.strength === "strong" ? 2 : s.strength === "weak" ? 0 : 1) + ((s.tenGodCounts["비견"] ?? 0) + (s.tenGodCounts["겁재"] ?? 0)) * 0.5 + (f ? (f.cheek + f.eyeTilt - 1) * 2 : 0);
  const pa = power(A, a.face);
  const pb = power(B, b.face);
  const leader = Math.abs(pa - pb) < 0.6 ? "번갈아 쥐는 사이" : pa > pb ? `${na} 쪽` : `${nb} 쪽`;

  const sorted = [...months].sort((x, y) => y.v - x.v);
  const best = sorted.filter((m) => !m.bad).slice(0, 2);
  const worst = [...months].sort((x, y) => x.v - y.v).filter((m) => m.v < 0 || m.bad).slice(0, 2);

  const headline =
    total >= 85 ? "서로를 완성하는 인연" : total >= 75 ? "함께할수록 깊어지는 사이" : total >= 65 ? "노력하면 단단해지는 사이" : total >= 55 ? "다름을 배우며 크는 인연" : "부딪치며 단단해지는 인연";

  const scores = [
    { key: "attraction", label: "끌림", value: attraction, note: stemHap ? "타고난 기운이 서로 끌어당기는 짝입니다" : dayHap ? "가까워질수록 편안해지는 짝입니다" : "천천히 스며드는 끌림입니다" },
    { key: "talk", label: "대화", value: talk, note: gen ? "한 사람이 다른 사람을 살려 주는 대화" : ea === eb ? "같은 결이라 말이 잘 통함" : ctl ? "생각이 달라 부딪힐 수 있음" : "무난하게 통함" },
    { key: "fill", label: "채움", value: fillV, note: covA + covB > 1.2 ? "서로 모자란 기운을 채워 줌" : "각자 채울 부분이 남아 있음" },
    { key: "life", label: "생활", value: life, note: yearChung || dayChung ? "생활 방식이 부딪치는 지점이 있음" : "함께 사는 리듬이 잘 맞음" },
    { key: "future", label: "앞날", value: future, note: goodMonths >= 4 ? "앞으로 함께 좋은 시기가 많음" : "때를 골라 움직이면 좋음" },
  ];

  const weakest = [...scores].sort((x, y) => x.value - y.value)[0];
  const summary = `${na}님과 ${nb}님은 ‘${headline}’입니다. 가장 잘 맞는 부분은 ${[...scores].sort((x, y) => y.value - x.value)[0].label}, 함께 신경 쓸 부분은 ${weakest.label}입니다.`;

  // ── 풀이 ──────────────
  const sections: Section[] = [];
  const nameIs = (n: string) => `${n}님은`;
  sections.push({
    id: "m-people",
    eyebrow: "",
    title: "두 사람의 타고난 기질",
    body: [DAY_MASTER[sa]?.replace("당신은", `${nameIs(na)}`) ?? "", DAY_MASTER[sb]?.replace("당신은", `${nameIs(nb)}`) ?? ""],
  });

  const view: SectionItem[] = [
    { label: `${nb}님 눈에 비친 ${na}님`, rows: [{ k: "속마음", v: VIEW[tgBA] }] },
    { label: `${na}님 눈에 비친 ${nb}님`, rows: [{ k: "속마음", v: VIEW[tgAB] }] },
  ];
  sections.push({ id: "m-view", eyebrow: "", title: "서로를 어떻게 보고 있을까", body: ["타고난 기운으로 본 서로의 첫 느낌과 속마음입니다.", ...view.map((v) => `${v.label} — ${v.rows[0].v}`)], items: view });

  const attract: string[] = [];
  if (stemHap) attract.push("두 사람의 중심 기운이 서로 합을 이루는 짝입니다. 처음 만났을 때부터 묘하게 끌렸다면 이 때문입니다.");
  if (dayHap) attract.push("배우자 자리가 서로 합을 이뤄, 가까워질수록 편안하고 오래 붙어 있고 싶어지는 사이입니다.");
  else if (daySam) attract.push("배우자 자리가 같은 무리에 속해, 같은 목표를 볼 때 가장 강하게 하나가 됩니다.");
  if (loveStar(tgAB, a.gender)) attract.push(`${nb}님은 ${na}님 사주에서 ‘이성의 별’에 해당합니다. ${na}님 쪽 끌림이 분명한 짝입니다.`);
  if (loveStar(tgBA, b.gender)) attract.push(`${na}님 역시 ${nb}님 사주에서 ‘이성의 별’입니다. ${nb}님도 쉽게 눈을 떼지 못합니다.`);
  if (dayChung) attract.push("배우자 자리가 서로 부딪쳐, 끌리면서도 자주 다투는 ‘불꽃형’ 사이입니다. 다툼 뒤 화해가 빠를수록 깊어집니다.");
  if (!attract.length) attract.push("첫눈에 반하는 사이보다는 시간을 두고 스며드는 사이입니다. 함께 보낸 시간이 곧 끌림이 됩니다.");
  sections.push({ id: "m-attract", eyebrow: "", title: "끌림", body: attract });

  const conflict: SectionItem[] = [];
  if (ctl) conflict.push({ label: "생각의 방향", rows: [{ k: "왜", v: `${gwa(ELEMENT_COLOR_NAME[ea])} ${ELEMENT_COLOR_NAME[eb]}처럼 한쪽이 다른 쪽을 누르는 관계라, 의견이 갈리면 한 사람이 눌린다고 느끼기 쉽습니다` }, { k: "해법", v: "결론을 내리기 전에 상대 의견을 한 번 요약해서 말해 주세요" }] });
  if (strong(A) && strong(B)) conflict.push({ label: "고집", rows: [{ k: "왜", v: "둘 다 기운이 강해 물러서지 않습니다" }, { k: "해법", v: "분야를 나눠 각자 결정권을 가지세요. 돈은 한 사람, 여행은 다른 사람처럼" }] });
  if (weak(A) && weak(B)) conflict.push({ label: "결정", rows: [{ k: "왜", v: "둘 다 상대에게 맞추려 해서 결정이 늦어집니다" }, { k: "해법", v: "작은 일은 동전 던지기라도 해서 빨리 정하는 규칙을 만드세요" }] });
  if (dayWon) conflict.push({ label: "서운함", rows: [{ k: "왜", v: "배우자 자리가 ‘원진’이라 사소한 말에 서운함이 쌓이기 쉽습니다" }, { k: "해법", v: "서운한 건 그날 안에, 짧게 말하기로 약속하세요" }] });
  if (yearChung) conflict.push({ label: "생활 리듬", rows: [{ k: "왜", v: `${ZODIAC[ya]}띠와 ${ZODIAC[yb]}띠는 서로 부딪치는 띠라 생활 습관이 다릅니다` }, { k: "해법", v: "잠·식사·청소 같은 생활 규칙을 미리 정해 두면 다툼이 크게 줄어듭니다" }] });
  if (!conflict.length) conflict.push({ label: "큰 충돌 없음", rows: [{ k: "다만", v: "편한 만큼 표현이 줄어들 수 있습니다. 고마운 건 말로 꺼내세요" }] });
  sections.push({ id: "m-conflict", eyebrow: "", title: "부딪히는 지점과 해법", body: ["사이가 좋아도 반복되기 쉬운 다툼의 이유입니다.", ...conflict.map((c) => `${c.label} — ${c.rows.map((r) => `${r.k}: ${r.v}`).join(". ")}`)], items: conflict });

  const fillBody: string[] = [];
  const coverLine = (me: string, other: string, need: Element[], c: number) =>
    `${me}님에게 필요한 기운은 ${need.map((e) => ELEMENT_COLOR_NAME[e]).join("·")}입니다. ` +
    (c >= 0.67
      ? `${other}님이 이 기운을 넉넉히 가지고 있어 곁에 있으면 힘이 됩니다.`
      : c >= 0.34
        ? `${other}님이 이 기운을 조금 가지고 있어 함께 있으면 도움이 됩니다.`
        : `${other}님에게는 이 기운이 적어, 취미나 생활 습관으로 따로 채우면 좋습니다.`);
  if (A.yongsin.length) fillBody.push(coverLine(na, nb, A.yongsin, covA));
  if (B.yongsin.length) fillBody.push(coverLine(nb, na, B.yongsin, covB));
  if (fillBody.length) sections.push({ id: "m-fill", eyebrow: "", title: "서로 채워 주는 것", body: fillBody });

  if (ya && yb) {
    const zt = yearHap || yearSam ? "서로 돕는 띠입니다. 집안끼리도 잘 어울리는 짝으로 봅니다." : yearChung ? "서로 부딪치는 띠입니다. 다만 띠는 궁합의 일부일 뿐이니 생활 규칙으로 충분히 풀 수 있습니다." : yearWon ? "서운함이 쌓이기 쉬운 띠입니다. 표현을 자주 하면 문제없습니다." : "무난하게 어울리는 띠입니다.";
    sections.push({ id: "m-zodiac", eyebrow: "", title: "띠 궁합", body: [`${na}님은 ${ZODIAC[ya]}띠, ${nb}님은 ${ZODIAC[yb]}띠. ${zt}`] });
  }

  if (months.length) {
    const act = ACTION[relation];
    const items: SectionItem[] = [
      ...best.map((m) => ({ label: m.label, badge: "★★★★★", title: act.best, rows: [{ k: "이렇게", v: "두 사람의 흐름이 함께 좋아지는 달입니다. 중요한 이야기는 이달에 꺼내세요" }] })),
      ...worst.map((m) => ({ label: m.label, badge: "★★☆☆☆", title: act.worst, rows: [{ k: "조심", v: "한 사람이라도 기운이 흔들리는 달입니다. 큰 결정과 감정적인 말은 미루세요" }] })),
    ];
    sections.push({ id: "m-timing", eyebrow: "", title: "둘에게 좋은 달, 조심할 달", body: ["앞으로 12개월 중 두 사람의 흐름을 겹쳐 본 결과입니다.", ...items.map((i) => `${i.label} — ${i.title}. ${i.rows[0].v}`)], items });
  }

  if (a.face && b.face) {
    const fa = a.face;
    const fb = b.face;
    const fl: string[] = [];
    const keys = Object.keys(fa) as (keyof FeatureScores)[];
    const sim = 1 - keys.reduce((s, k) => s + Math.abs(fa[k] - fb[k]), 0) / keys.length;
    fl.push(sim > 0.8 ? "두 사람의 얼굴 비율이 꽤 닮았습니다. 관상에서는 닮은 얼굴을 ‘오래 함께할 상’으로 봅니다." : "두 사람의 얼굴은 서로 다른 장점을 가졌습니다. 관상에서는 서로 다른 얼굴이 만나 부족한 운을 채운다고 봅니다.");
    if (fa.smile > 0.55 && fb.smile > 0.55) fl.push("둘 다 입꼬리가 올라간 상이라 함께 있으면 웃음이 끊이지 않는 짝입니다.");
    else if (fa.smile < 0.45 && fb.smile < 0.45) fl.push("둘 다 진지한 입꼬리라 표현이 부족해 보일 수 있습니다. 서로 먼저 웃어 주면 운이 열립니다.");
    if (Math.abs(fa.eyes - fb.eyes) > 0.2) fl.push(`${fa.eyes > fb.eyes ? na : nb}님은 감정을 드러내는 눈, ${fa.eyes > fb.eyes ? nb : na}님은 마음을 깊이 담아 두는 눈입니다. 표현 방식이 달라도 마음의 크기는 같다는 걸 기억하세요.`);
    if (fa.nose + fb.nose > 1.15) fl.push("두 사람 모두 재물궁인 코가 듬직해, 함께 모으는 재물이 큰 짝입니다.");
    if (fa.jaw + fb.jaw + fa.chin + fb.chin > 2.2) fl.push("둘 다 턱이 든든해 말년운이 좋은 짝입니다. 오래갈수록 더 편안해집니다.");
    const faceLead = fa.cheek + fa.eyeTilt >= fb.cheek + fb.eyeTilt ? na : nb;
    fl.push(
      leader.startsWith(faceLead)
        ? `광대와 눈꼬리가 더 또렷한 ${faceLead}님 쪽이 관상으로도 주도권을 쥐는 상입니다.`
        : `광대와 눈꼬리로 보면 ${faceLead}님이 조금 더 앞에 서는 상이지만, 사주까지 합치면 주도권은 ${leader}입니다.`,
    );
    sections.push({ id: "m-face", eyebrow: "", title: "관상 궁합", body: fl });
  }

  const w = worry.trim();
  if (w) {
    const topics: [RegExp, string][] = [
      [/연락|답장|카톡|문자|읽씹/, "연락 문제는 사랑의 크기보다 생활 리듬의 차이인 경우가 많습니다. 연락 횟수 대신 ‘하루 한 번 꼭’ 같은 약속을 정해 보세요."],
      [/결혼|상견례|프러포즈|청혼/, `결혼 이야기는 두 사람의 흐름이 함께 좋은 ${best[0]?.label ?? "시기"}에 꺼내는 것이 좋습니다.`],
      [/돈|경제|월급|빚|대출|생활비/, "돈 문제는 감정이 아니라 숫자로 이야기하세요. 공동 통장과 각자 용돈을 나누면 다툼이 줄어듭니다."],
      [/싸움|다툼|싸워|싸우|화가|화를/, "다툴 때는 ‘너는’ 대신 ‘나는’으로 시작해 보세요. 이 사이는 화해가 빠를수록 더 단단해집니다."],
      [/바람|믿음|의심|질투|집착|신뢰/, "믿음이 흔들릴 때는 확인보다 안심을 주는 습관이 필요합니다. 일정과 약속을 먼저 공유해 주세요."],
      [/가족|부모|시댁|처가|시어머니|장모/, "가족 문제는 각자 자기 가족을 맡는 것이 원칙입니다. 상대 가족과의 일은 내가 앞에 서 주세요."],
      [/권태|설렘|지루|식었|식은/, "권태는 관계가 안정됐다는 신호이기도 합니다. 처음 가 보는 곳, 처음 해 보는 일을 함께 하세요."],
      [/고백|짝사랑|좋아하는|마음을/, `마음을 전하기 가장 좋은 때는 ${best[0]?.label ?? "두 사람 모두 여유가 있을 때"}입니다. 부담 없는 자리에서 짧고 솔직하게 전하세요.`],
      [/재회|헤어|이별|다시/, "다시 만나고 싶다면 먼저 헤어진 이유가 바뀌었는지 스스로 점검하세요. 연락은 감정이 가라앉은 뒤에 한 번이면 충분합니다."],
    ];
    const hits = topics.filter(([re]) => re.test(w)).map(([, t]) => t);
    if (!hits.length) hits.push(`적어 주신 고민은 두 사람의 ‘${weakest.label}’ 부분과 맞닿아 있습니다. ${polite(weakest.note)} 이 부분을 함께 이야기해 보세요.`);
    sections.push({ id: "m-worry", eyebrow: "", title: "적어 주신 고민에 대해", body: [`“${w.length > 60 ? w.slice(0, 60) + "…" : w}”`, ...hits] });
  }

  sections.push({
    id: "m-advice",
    eyebrow: "",
    title: "두 사람에게 드리는 당부",
    body: [
      `가장 잘 맞는 ${eun([...scores].sort((x, y) => y.value - x.value)[0].label)} 이 관계의 무기입니다. 힘들 때일수록 이 장점을 떠올리세요.`,
      `${eun(weakest.label)} 노력으로 채울 수 있는 부분입니다. ${polite(weakest.note)}`,
      "궁합은 정해진 답이 아니라 서로를 이해하는 지도입니다. 결국 관계를 만드는 건 두 사람의 선택입니다.",
    ],
  });
  sections.forEach((s, i) => (s.eyebrow = String(i + 1).padStart(2, "0")));

  return {
    createdAt: new Date().toISOString(),
    relation,
    names: [na, nb],
    total,
    headline,
    summary,
    scores,
    leader,
    bestMonth: best[0]?.label ?? null,
    sections,
    hasFace,
  };
}
