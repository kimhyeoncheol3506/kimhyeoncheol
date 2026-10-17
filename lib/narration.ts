// 더빙 대본 만들기.
// 1) 숫자·날짜·시간을 한국어 읽기로 바꾸고 (6월 → 유월, 5시 → 다섯 시, 1,900원 → 천구백 원)
// 2) 기호·괄호·영문 약어를 소리 내 읽기 좋게 다듬고 (발음 사전)
// 3) 제목·요약·본문을 나눠 말투(속도·높낮이)와 쉼을 다르게 줍니다.
import type { Section } from "./reading/types";

export type CueKind = "title" | "lead" | "body";
/** 한 번에 읽을 한 덩어리 */
export type Cue = { text: string; kind: CueKind; pause: number };

// ── 숫자 읽기 ──────────────
const D = ["", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"];
function sino4(n: number) {
  let out = "";
  const units: [number, string][] = [[1000, "천"], [100, "백"], [10, "십"]];
  for (const [u, name] of units) {
    const d = Math.floor(n / u) % 10;
    if (d) out += (d === 1 ? "" : D[d]) + name;
  }
  return out + D[n % 10];
}
/** 한자어 수: 2026 → 이천이십육 */
export function sino(n: number): string {
  if (!Number.isFinite(n)) return String(n);
  if (n === 0) return "영";
  const parts: string[] = [];
  const big = ["", "만", "억", "조"];
  let i = 0;
  while (n > 0 && i < big.length) {
    const g = n % 10000;
    if (g) parts.unshift((g === 1 && i === 1 ? "" : sino4(g)) + big[i]);
    n = Math.floor(n / 10000);
    i++;
  }
  return parts.join(" ");
}
const TENS = ["", "열", "스물", "서른", "마흔", "쉰", "예순", "일흔", "여든", "아흔"];
const ONES = ["", "한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉"];
/** 고유어 수(세는 말 앞): 3 → 세, 20 → 스무, 21 → 스물한 */
export function native(n: number): string {
  if (n <= 0 || n >= 100) return sino(n);
  if (n === 20) return "스무";
  return TENS[Math.floor(n / 10)] + ONES[n % 10];
}
const MONTH = ["", "일월", "이월", "삼월", "사월", "오월", "유월", "칠월", "팔월", "구월", "시월", "십일월", "십이월"];
const WEEKDAY: Record<string, string> = { 월: "월요일", 화: "화요일", 수: "수요일", 목: "목요일", 금: "금요일", 토: "토요일", 일: "일요일" };
const num = (s: string) => Number(s.replace(/,/g, ""));

// ── 발음 사전 (TTS가 자주 틀리는 표기) ──────────────
const DICT: [RegExp, string][] = [
  [/SNS/g, "에스엔에스"],
  [/PDF/g, "피디에프"],
  [/\bAI\b/g, "에이아이"],
  [/\bTOP\b/gi, "탑"],
  [/\bvs\b/gi, "대"],
  [/\bNEW\b/g, "새로운"],
  [/×/g, " 그리고 "],
  [/&/g, " 그리고 "],
  [/±/g, "플러스 마이너스 "],
];

/** 화면 글을 '읽는 글'로 바꾸기 */
export function toSpoken(input: string): string {
  let s = input;
  // 별점·이모지·장식 기호
  s = s.replace(/[★☆✦◆●■□▲▼♥♡]/g, "").replace(/[\uD83C-\uDBFF][\uDC00-\uDFFF]|[\u2600-\u27BF]\uFE0F?/g, "");
  // 17일(토) → 17일 토요일
  s = s.replace(/(\d+일)\s*\(([월화수목금토일])\)/g, (_, d, w) => `${d} ${WEEKDAY[w]}`);
  // 범위: 4~8일 → 4일에서 8일
  s = s.replace(/(\d+)\s*~\s*(\d+)\s*(년|개월|월|일|시간|시|분|세|살|개|명|번|가지|점)/g, "$1$3에서 $2$3");
  s = s.replace(/\s*~\s*/g, "부터 ");
  // 괄호: 한자·영문 근거 표기는 빼고, 우리말 보충은 쉼표로 이어 읽기
  s = s.replace(/\(([^)]*)\)(?=([가-힣])?)/g, (_, inner: string, next?: string) =>
    /[一-鿿A-Za-z]/.test(inner) || !inner.trim() ? "" : `, ${inner.trim()}${next ? "" : ","}`,
  );
  s = s.replace(/[一-鿿]+/g, "");
  // 숫자 + 단위
  s = s.replace(/(\d+)\s*\/\s*(100|20|10|5)(?!\d)\s*점?/g, (_, a, b) => `${sino(num(b))} 점 만점에 ${sino(num(a))} 점`);
  s = s.replace(/(\d{1,3}(?:,\d{3})+|\d+)\s*원/g, (_, n) => `${sino(num(n))} 원`);
  s = s.replace(/(\d+)\s*%/g, (_, n) => `${sino(num(n))} 퍼센트`);
  s = s.replace(/(\d+)\s*년/g, (_, n) => `${sino(num(n))} 년`);
  s = s.replace(/(\d+)\s*개월/g, (_, n) => `${sino(num(n))} 개월`);
  s = s.replace(/(\d+)\s*월(?!요일)/g, (m, n) => (num(n) >= 1 && num(n) <= 12 ? MONTH[num(n)] : m));
  s = s.replace(/(\d+)\s*일/g, (_, n) => `${sino(num(n))} 일`);
  s = s.replace(/(\d+)\s*시간/g, (_, n) => `${native(num(n))} 시간`);
  s = s.replace(/(\d+)\s*시(?![작대기절험])/g, (_, n) => `${num(n) >= 1 && num(n) <= 12 ? native(num(n)) : sino(num(n))} 시`);
  s = s.replace(/(\d+)\s*분/g, (_, n) => `${sino(num(n))} 분`);
  s = s.replace(/(\d+)\s*(살|가지|명|번째|번|곳|개|잔|달)/g, (_, n, u) => `${native(num(n))} ${u}`);
  s = s.replace(/(\d+)\s*(세|점|위|등|층|호|대)/g, (_, n, u) => `${sino(num(n))} ${u}`);
  for (const [re, to] of DICT) s = s.replace(re, to);
  // 문장 부호: 가운뎃점·대시·슬래시는 쉼, 따옴표는 빼기
  s = s
    .replace(/·/g, ", ")
    .replace(/:\s/g, ", ")
    .replace(/[—–]/g, ", ")
    .replace(/\s\/\s/g, ", ")
    .replace(/[‘’“”"']/g, "")
    .replace(/…+/g, ".")
    .replace(/\s+,/g, ",")
    .replace(/,\s*(,\s*)+/g, ", ")
    .replace(/,\s*([.!?])/g, "$1")
    .replace(/\s+/g, " ")
    .replace(/^\s*,\s*/, "")
    .trim();
  return s;
}

/** 문장 단위로 쪼개기 */
export function splitSentences(text: string): string[] {
  return text
    .replace(/\s+/g, " ")
    .split(/(?<=[.!?])\s+/)
    .map((x) => x.trim())
    .filter(Boolean);
}

/** 너무 긴 덩어리는 문장 경계에서 나눠 자연스럽게 숨 쉬게 */
function chunk(text: string, max = 220): string[] {
  const out: string[] = [];
  let cur = "";
  for (const s of splitSentences(text)) {
    if (cur && (cur + " " + s).length > max) {
      out.push(cur);
      cur = s;
    } else cur = cur ? `${cur} ${s}` : s;
  }
  if (cur) out.push(cur);
  return out;
}

const PAUSE: Record<CueKind, number> = { title: 450, lead: 350, body: 220 };
const end = (t: string) => (/[.!?]$/.test(t) ? t : `${t}.`);

/** 대본 만들기 도우미 */
export class Script {
  cues: Cue[] = [];
  add(kind: CueKind, raw: string | undefined | null, pause?: number) {
    if (!raw) return this;
    const spoken = toSpoken(raw);
    if (!spoken) return this;
    const parts = kind === "title" ? [end(spoken)] : chunk(end(spoken));
    parts.forEach((t, i) => this.cues.push({ text: t, kind, pause: i === parts.length - 1 ? pause ?? PAUSE[kind] : PAUSE[kind] }));
    return this;
  }
  /** 섹션 끝: 마지막 덩어리 뒤 쉼을 길게 */
  breath(ms = 750) {
    const last = this.cues.at(-1);
    if (last) last.pause = Math.max(last.pause, ms);
    return this;
  }
}

const ORDINAL = ["첫 번째", "두 번째", "세 번째", "네 번째", "다섯 번째", "여섯 번째", "일곱 번째", "여덟 번째", "아홉 번째", "열 번째", "열한 번째", "열두 번째", "열세 번째", "열네 번째", "열다섯 번째"];
/** 듣기용으로 꼭 필요한 줄만 (표의 모든 칸을 읽으면 너무 길어짐) */
const SPOKEN_ROWS: Record<string, string> = {
  "잘되는 일": "잘되는 일은",
  "조심할 일": "조심할 일은",
  "좋은 일": "좋은 일은",
  조심: "조심할 것은",
  주의: "주의할 점은",
  "좋은 날": "좋은 날은",
  "조심할 날": "조심할 날은",
  "할 일": "이달에 해 볼 일은",
  해법: "해법은",
  이렇게: "",
  속마음: "",
};

/** 풀이 한 장을 대본으로 */
export function addSection(sc: Script, s: Section, i: number) {
  sc.add("title", `${ORDINAL[i] ?? `${i + 1}번째`}, ${s.title}`);
  if (s.items?.length) {
    sc.add("lead", s.body[0]);
    for (const it of s.items) {
      const rows = it.rows.filter((r) => r.k in SPOKEN_ROWS).slice(0, 2);
      sc.add("body", [`${it.label}.`, it.title ? end(it.title) : "", ...rows.map((r) => `${SPOKEN_ROWS[r.k]} ${end(r.v)}`.trim())].filter(Boolean).join(" "));
    }
  } else {
    s.body.forEach((p) => sc.add("body", p));
  }
  sc.breath();
}

/** 예전 방식(문자열 하나)도 대본으로 */
export function cuesFromText(text: string): Cue[] {
  return new Script().add("body", text).cues;
}
