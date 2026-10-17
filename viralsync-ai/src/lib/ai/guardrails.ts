import { findRiskyPhrases } from "@/lib/analysis/engine";

/** 허위 체험담·가짜 이용자 반응으로 의심되는 표현 */
export const FAKE_EXPERIENCE_PATTERNS = [
  "직접 써봤",
  "직접 사용해",
  "제가 써",
  "제가 사용",
  "내돈내산",
  "솔직 후기",
  "실사용 후기",
  "써보니까",
  "먹어봤",
  "다녀왔는데",
  "저도 샀",
  "강추합니다 진짜",
];

export function defaultDisclosure(clientName: string): string {
  return `[광고] 본 내용은 ${clientName}의 유료 광고(협찬)를 포함하고 있으며, AI 초안을 담당자가 검토했습니다.`;
}

/** 생성된 문구 검사 → 경고 목록. 경고가 있어도 저장은 하되, 검토자 화면에 표시하고 실행 사전검사에서 다시 확인한다. */
export function inspectDraft(body: string, opts: { bannedPhrases: string[]; requiredPhrases: string[] }): string[] {
  const warnings: string[] = [];
  const t = body.toLowerCase();
  const fake = FAKE_EXPERIENCE_PATTERNS.filter((p) => t.includes(p.toLowerCase()));
  if (fake.length) warnings.push(`허위 체험담 의심 표현: ${fake.join(", ")}`);
  const banned = opts.bannedPhrases.filter((p) => p && t.includes(p.toLowerCase()));
  if (banned.length) warnings.push(`금지 표현 포함: ${banned.join(", ")}`);
  const risky = findRiskyPhrases(body);
  if (risky.length) warnings.push(`과장·단정 표현: ${risky.join(", ")}`);
  const missing = opts.requiredPhrases.filter((p) => p && !t.includes(p.toLowerCase()));
  if (missing.length) warnings.push(`필수 표현 누락: ${missing.join(", ")}`);
  return warnings;
}
