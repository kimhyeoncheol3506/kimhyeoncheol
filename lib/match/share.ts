// 궁합 결과 공유 주소: 생년월일·사진·고민 같은 개인정보 없이 '점수 요약'만 쿼리에 담는다.
import { RELATIONS, type MatchResult, type Relation } from "./compute";

export type MatchShare = {
  names: [string, string];
  relation: Relation;
  total: number;
  scores: number[]; // 끌림·대화·채움·생활·앞날 (각 0~20)
  headline: string;
  leader: string;
  bestMonth: string | null;
};

export const SCORE_LABELS = ["끌림", "대화", "채움", "생활", "앞날"];
const HEADLINES = ["서로를 완성하는 인연", "함께할수록 깊어지는 사이", "노력하면 단단해지는 사이", "다름을 배우며 크는 인연", "부딪치며 단단해지는 인연"];
const clean = (s: string, max = 10) => s.replace(/[<>"'&\n\r\t]/g, "").trim().slice(0, max);
const int = (v: string | null, lo: number, hi: number) => {
  const n = Number(v);
  return Number.isFinite(n) ? Math.max(lo, Math.min(hi, Math.round(n))) : null;
};

/** 결과 → 공유 쿼리 (n=이름,이름 r=관계 t=총점 s=점수5개 h=제목번호 l=주도권 b=좋은달) */
export function toShareQuery(r: MatchResult): string {
  const q = new URLSearchParams();
  q.set("n", `${clean(r.names[0])},${clean(r.names[1])}`);
  q.set("r", r.relation);
  q.set("t", String(r.total));
  q.set("s", r.scores.map((s) => s.value).join("."));
  q.set("h", String(Math.max(0, HEADLINES.indexOf(r.headline))));
  const [a, b] = r.names;
  q.set("l", r.leader.startsWith(a) ? "a" : r.leader.startsWith(b) ? "b" : "x");
  if (r.bestMonth) {
    const m = r.bestMonth.match(/(\d{4})년 (\d{1,2})월/);
    if (m) q.set("b", `${m[1]}-${m[2]}`);
  }
  return q.toString();
}

/** 공유 쿼리 → 화면용 데이터 (값이 이상하면 null) */
export function fromShareQuery(get: (k: string) => string | null): MatchShare | null {
  const names = (get("n") ?? "").split(",").map((x) => clean(x));
  const relation = RELATIONS.find((x) => x.id === get("r"))?.id;
  const total = int(get("t"), 0, 100);
  const scores = (get("s") ?? "").split(".").map((x) => int(x, 0, 20));
  if (!relation || total === null || scores.length !== 5 || scores.some((x) => x === null)) return null;
  const na = names[0] || "나";
  const nb = names[1] || "상대";
  const hi = int(get("h"), 0, HEADLINES.length - 1) ?? 2;
  const l = get("l");
  const bm = (get("b") ?? "").match(/^(\d{4})-(\d{1,2})$/);
  return {
    names: [na, nb],
    relation,
    total,
    scores: scores as number[],
    headline: HEADLINES[hi],
    leader: l === "a" ? `${na} 쪽` : l === "b" ? `${nb} 쪽` : "번갈아 쥐는 사이",
    bestMonth: bm ? `${bm[1]}년 ${Number(bm[2])}월` : null,
  };
}

export const relationLabel = (r: Relation) => RELATIONS.find((x) => x.id === r)?.label ?? "";
