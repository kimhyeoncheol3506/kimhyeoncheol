import type { ApprovalGate } from "@prisma/client";

/**
 * AI 에이전트 조직도. 각 에이전트는 초안·분석만 만들고, 외부로 나가는 결과(답변 발송·계약·게시)는
 * 사람의 결재(ApprovalGate)를 거친다. autonomy 는 사람 승인 없이 할 수 있는 범위.
 */
export interface AgentDef {
  key: string;
  name: string;
  emoji: string;
  mission: string;
  inputs: string;
  outputs: string;
  autonomy: string;
  handsOffTo: ApprovalGate | null;
  auditActions: string[];
  href: string;
}

export const AI_AGENTS: AgentDef[] = [
  {
    key: "intake",
    name: "접수 에이전트",
    emoji: "📥",
    mission: "고객 문의 원문을 읽고 브랜드·업종·링크·키워드·요청 매체·질문을 정리합니다.",
    inputs: "크몽·전화·메일 문의 원문",
    outputs: "문의 분석표, 고객에게 더 물어볼 목록",
    autonomy: "분석만 수행 (외부 연락 없음)",
    handsOffTo: null,
    auditActions: ["inquiry.create", "inquiry.reanalyze"],
    href: "/inquiries",
  },
  {
    key: "strategist",
    name: "전략 에이전트",
    emoji: "🧭",
    mission: "업종과 요청에 맞는 매체를 추천하고 실속·표준·집중 3안 견적과 답변 초안을 만듭니다.",
    inputs: "문의 분석표, 서비스 상품 가격표",
    outputs: "추천 매체, 3안 견적, 고객 답변 초안",
    autonomy: "초안까지 — 견적 발송·계약은 결재 후",
    handsOffTo: "QUOTE",
    auditActions: ["inquiry.quote", "inquiry.convert"],
    href: "/inquiries",
  },
  {
    key: "copywriter",
    name: "카피 에이전트",
    emoji: "✍️",
    mission: "캠페인·게시물 문맥에 맞는 홍보 문구 초안을 씁니다 (광고 표시 포함, 허위 체험담 금지).",
    inputs: "의뢰서, 브랜드 프로필, 연결 게시물",
    outputs: "댓글·게시물·블로그·쇼츠 문구 초안",
    autonomy: "초안까지 — 게시는 결재 후",
    handsOffTo: "CONTENT",
    auditActions: ["content.generate"],
    href: "/content",
  },
  {
    key: "compliance",
    name: "컴플라이언스 에이전트",
    emoji: "🛡️",
    mission: "모든 결재 요청을 사람보다 먼저 검토합니다. 광고 표시 누락·허위 체험담·금지 표현·성과 보장·직거래 유도는 차단합니다.",
    inputs: "결재 요청된 문구·견적·답변",
    outputs: "AI 1차 검토 결과 (차단/주의)",
    autonomy: "차단 판정 시 사람도 승인 불가 (수정 후 재요청)",
    handsOffTo: null,
    auditActions: ["approval.request"],
    href: "/approvals",
  },
  {
    key: "publisher",
    name: "집행 에이전트",
    emoji: "🚀",
    mission: "승인된 문구를 사전검사 후 매체에 게시하고(모의/실제), 매체별 집행 작업 진행을 추적합니다.",
    inputs: "최종 승인된 문구, 계약된 작업",
    outputs: "게시 기록, 집행 작업 현황",
    autonomy: "승인된 것만 실행",
    handsOffTo: null,
    auditActions: ["publication.success", "publication.failed", "threads.post.live", "task.update"],
    href: "/executions",
  },
  {
    key: "analyst",
    name: "리포트 에이전트",
    emoji: "📈",
    mission: "실행 결과·실적·비용을 출처(모의/데모/실측)별로 집계하고 월간 보고서를 만듭니다.",
    inputs: "게시 기록, 실적, 비용",
    outputs: "대시보드, CSV, 월간 보고서",
    autonomy: "읽기 전용 집계",
    handsOffTo: null,
    auditActions: ["report.export"],
    href: "/reports",
  },
];
