import { FAKE_EXPERIENCE_PATTERNS } from "@/lib/ai/guardrails";
import { findRiskyPhrases } from "@/lib/analysis/engine";

/**
 * 컴플라이언스 에이전트의 AI 1차 검토 (규칙 기반).
 * block: 사람이 승인할 수 없는 위반 / warn: 결재자가 확인해야 할 주의 사항
 */
export interface Finding {
  severity: "block" | "warn";
  message: string;
}

export interface AiReview {
  agent: "compliance";
  passed: boolean;
  findings: Finding[];
}

const DISCLOSURE = /(광고|협찬|유료|#ad|sponsored)/i;

function done(findings: Finding[]): AiReview {
  return { agent: "compliance", passed: !findings.some((f) => f.severity === "block"), findings };
}

export function reviewContent(c: { body: string; disclosure: string; warnings: string[]; bannedPhrases: string[]; ownAccount?: boolean }): AiReview {
  const f: Finding[] = [];
  const text = `${c.body}\n${c.disclosure}`;
  // 고객(가게) 본인 계정 게시물은 광고 표시가 필요 없다. 제3자 계정·후기형 게시는 반드시 표시
  if (!c.ownAccount && !DISCLOSURE.test(text)) f.push({ severity: "block", message: "광고·협찬 표시가 없습니다." });
  const fake = FAKE_EXPERIENCE_PATTERNS.filter((p) => c.body.includes(p));
  if (fake.length) f.push({ severity: "block", message: `허위 체험담 의심 표현: ${fake.join(", ")}` });
  const banned = c.bannedPhrases.filter((p) => p && c.body.toLowerCase().includes(p.toLowerCase()));
  if (banned.length) f.push({ severity: "block", message: `고객 금지 표현 포함: ${banned.join(", ")}` });
  const risky = findRiskyPhrases(c.body);
  if (risky.length) f.push({ severity: "warn", message: `과장·단정 표현: ${risky.join(", ")}` });
  for (const w of c.warnings.filter((w) => w.startsWith("필수 표현"))) f.push({ severity: "warn", message: w });
  return done(f);
}

export function reviewQuote(q: { reply: string; total: number; mediaSpendSeparate: boolean }): AiReview {
  const f: Finding[] = [];
  if (/(상위\s*노출\s*보장|매출\s*보장|100\s*%|무조건|확실히\s*(?:올려|보장))/.test(q.reply)) f.push({ severity: "block", message: "성과 보장 표현이 있습니다 (상위노출·매출 보장 등)." });
  if (/(계좌|입금|직거래|카톡으로\s*결제|현금\s*결제)/.test(q.reply)) f.push({ severity: "block", message: "플랫폼 밖 직접 결제를 유도하는 표현이 있습니다." });
  if (!/광고·협찬 표시|광고 표시/.test(q.reply)) f.push({ severity: "warn", message: "답변에 광고 표시 안내가 없습니다." });
  if (q.mediaSpendSeparate && !/매체비/.test(q.reply)) f.push({ severity: "warn", message: "매체비 별도 안내가 빠졌습니다." });
  if (q.total <= 0) f.push({ severity: "block", message: "견적 금액이 0원입니다." });
  return done(f);
}
