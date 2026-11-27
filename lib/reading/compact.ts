// AI 해석 요청용 초안 축약: 표 항목·긴 문단을 줄여 입력을 작게 만든다 (비용·입력 제한 대응).
import type { Reading } from "./types";

const cut = (s: string, n: number) => (s.length > n ? `${s.slice(0, n)}…` : s);

export type CompactDraft = {
  headline: string;
  summary: string;
  sections: { id: string; title: string; body: string[]; items?: string[] }[];
  advice: string[];
};

/** 섹션마다 문단 4개·각 140자, 표 항목은 '이름 — 제목' 한 줄씩 최대 14개만 남긴다 */
export function compactDraft(r: Pick<Reading, "headline" | "summary" | "sections" | "advice">, maxChars = 9000): CompactDraft {
  const build = (paras: number, len: number, items: number): CompactDraft => ({
    headline: cut(r.headline, 60),
    summary: cut(r.summary, 300),
    sections: r.sections.map((s) => ({
      id: s.id,
      title: s.title,
      body: (s.items?.length ? s.body.slice(0, 1) : s.body.slice(0, paras)).map((p) => cut(p, len)),
      ...(s.items?.length ? { items: s.items.slice(0, items).map((i) => cut(`${i.label} — ${i.title ?? i.rows[0]?.v ?? ""}`, 90)) } : {}),
    })),
    advice: r.advice.slice(0, 4).map((a) => cut(a, 160)),
  });
  // 정해진 크기 안에 들어올 때까지 단계적으로 더 줄임
  for (const [p, l, i] of [[4, 140, 14], [3, 110, 12], [2, 90, 8], [1, 70, 6]] as const) {
    const d = build(p, l, i);
    if (JSON.stringify(d).length <= maxChars) return d;
  }
  return build(1, 50, 4);
}
