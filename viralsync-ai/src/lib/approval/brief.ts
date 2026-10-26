import type { ApprovalGate, RiskLevel } from "@prisma/client";
import { RISK_LABEL } from "@/lib/labels";
import { won } from "@/lib/format";

export interface RequestBrief {
  target: string;
  change: string;
  cost: string;
  risk: string;
  undo: string;
}

const TIER_LABEL: Record<string, string> = { BASIC: "실속형", STANDARD: "표준형", PREMIUM: "집중형" };

/** 결재 요청서 — 결재자가 판단에 필요한 다섯 가지를 한눈에 (대상·변경 내용·비용·위험·되돌리는 법) */
export function requestBrief(r: { gate: ApprovalGate; title: string; amount: number | null; risk: RiskLevel; payload?: unknown; blocked: boolean }): RequestBrief {
  const risk = `${RISK_LABEL[r.risk]}${r.blocked ? " · AI 1차 검토 차단 항목 있음 (승인 불가)" : ""}`;
  if (r.gate === "CONTENT")
    return {
      target: r.title,
      change: "초안 → 승인됨. 승인 후 ‘실행 관리’에서 게시 대기 등록이 가능해집니다 (자동 게시 없음).",
      cost: "결재 자체 0원 · 실제 게시는 매체 연결 후, 모의 실행은 0원",
      risk,
      undo: "게시 전: 수정 후 재결재. 게시 후: 매체에서 직접 삭제하고 실행 기록에 남김.",
    };
  if (r.gate === "QUOTE")
    return {
      target: r.title,
      change: "견적·답변 초안 → 발송 가능 상태. 실제 발송은 담당자가 복사해 크몽 등에서 직접 보냅니다.",
      cost: `견적 총액 ${won(r.amount)} (고객 청구 기준, 매체비 별도 여부는 답변에 표기)`,
      risk,
      undo: "발송 전: 견적 재작성. 발송 후: 고객에게 정정 안내 (자동 철회 불가).",
    };
  const tier = (r.payload as { tier?: string } | null)?.tier;
  return {
    target: r.title,
    change: `계약 전환${tier ? ` (${TIER_LABEL[tier] ?? tier})` : ""} → 고객·캠페인·매체별 집행 작업이 자동 생성됩니다.`,
    cost: `계약 금액 ${won(r.amount)}`,
    risk,
    undo: "생성된 캠페인은 ‘캠페인 보관(삭제)’으로 정리, 문의는 미계약 처리.",
  };
}
