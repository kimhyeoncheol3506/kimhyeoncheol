// 금액은 서버가 문자열(Decimal)로 보낸다. 부동소수 변환 없이 문자열로 천단위 구분한다.
export function fmtAmount(v: unknown): string {
  if (v === null || v === undefined || v === "") return "-";
  const s = String(v).trim();
  const m = /^(-?)(\d+)(?:\.(\d+))?$/.exec(s);
  if (!m) return s;
  const int = m[2].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  const frac = m[3] ? m[3].replace(/0+$/, "") : "";
  return `${m[1]}${int}${frac ? "." + frac : ""}`;
}

export const RATE_STATUS_LABEL: Record<string, string> = {
  NEW: "신규", REMOVED: "소멸", NO_CHANGE: "변동없음", "N/A_ZERO_BASE": "산정불가(0기준)",
  SIGN_CHANGE: "부호전환", RATE: "",
};

export function fmtRate(rate: unknown, status?: string): string {
  if (status && status !== "RATE") return RATE_STATUS_LABEL[status] ?? status;
  if (rate === null || rate === undefined || rate === "") return "-";
  const n = Number(rate) * 100;
  if (!isFinite(n)) return "-";
  return `${n > 0 ? "+" : ""}${n.toFixed(2)}%`;
}

export const STATUS_LABEL: Record<string, string> = {
  PASS: "통과", WARNING: "경고", FAIL: "실패", REVIEW_REQUIRED: "검토필요", NOT_APPLICABLE: "해당없음", NOT_RUN: "미수행",
  RUNNING: "처리중", FAILED: "처리실패", BLOCKED: "차단", READY_FOR_REVIEW: "검토대기", REVIEWED: "검토완료",
  APPROVED: "승인", FINALIZED: "확정", REJECTED: "반려", DRAFT: "초안", ACTIVE: "활성", INACTIVE: "비활성",
  SUPERSEDED: "이전버전", PARSED: "판독완료", ERROR: "판독오류",
};

export const STATUS_ICON: Record<string, string> = {
  PASS: "✓", WARNING: "!", FAIL: "✕", REVIEW_REQUIRED: "?", NOT_APPLICABLE: "–", NOT_RUN: "○",
  BLOCKED: "✕", READY_FOR_REVIEW: "…", REVIEWED: "✓", APPROVED: "✓", FINALIZED: "■", FAILED: "✕", REJECTED: "✕",
};

export function fmtBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

export function fmtTime(s?: string | null): string {
  if (!s) return "-";
  return s.replace("T", " ").replace(/\+.*$/, "");
}
