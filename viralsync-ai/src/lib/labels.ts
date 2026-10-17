import type {
  CampaignGoal,
  CampaignStatus,
  ContentStatus,
  ContentType,
  CostType,
  IntegrationStatus,
  MetricSource,
  PlatformKey,
  PolicyReviewStatus,
  PublicationStatus,
  ReviewStatus,
  RiskLevel,
  Role,
  TargetType,
} from "@prisma/client";

export const ROLE_LABEL: Record<Role, string> = {
  ADMIN: "관리자",
  CAMPAIGN_MANAGER: "캠페인 매니저",
  CONTENT_WRITER: "콘텐츠 작성자",
  REVIEWER: "검토자",
  VIEWER: "읽기 전용",
};

export const CAMPAIGN_STATUS_LABEL: Record<CampaignStatus, string> = {
  DRAFT: "초안",
  ANALYZED: "AI 분석 완료",
  PENDING_REVIEW: "검토 대기",
  CHANGES_REQUESTED: "수정 요청",
  APPROVED: "승인 완료",
  READY_TO_RUN: "실행 대기",
  COMPLETED: "실행 완료",
  FAILED: "실행 실패",
};

export const CAMPAIGN_STATUS_ORDER: CampaignStatus[] = [
  "DRAFT",
  "ANALYZED",
  "PENDING_REVIEW",
  "APPROVED",
  "READY_TO_RUN",
  "COMPLETED",
];

export const TARGET_TYPE_LABEL: Record<TargetType, string> = {
  BLOG: "블로그",
  YOUTUBE: "유튜브",
  SHORTS: "쇼츠",
  REELS: "릴스",
  APP: "앱",
  PRODUCT: "상품",
  OTHER: "기타",
};

export const GOAL_LABEL: Record<CampaignGoal, string> = {
  VIEWS: "조회",
  CLICKS: "클릭",
  VISITS: "방문",
  INSTALLS: "설치",
  INQUIRIES: "문의",
  PURCHASES: "구매",
};

export const PLATFORM_LABEL: Record<PlatformKey, string> = {
  INSTAGRAM: "Instagram",
  TIKTOK: "TikTok",
  X: "X",
  FACEBOOK: "Facebook",
  YOUTUBE: "YouTube",
  BLOG: "블로그",
};

export const PLATFORMS: PlatformKey[] = ["INSTAGRAM", "TIKTOK", "X", "FACEBOOK", "YOUTUBE", "BLOG"];

export const INTEGRATION_STATUS_LABEL: Record<IntegrationStatus, string> = {
  DEMO_ONLY: "1. 데모 전용",
  API_READY: "2. API 연동 준비",
  AUTHENTICATED: "3. 인증 완료",
  PUBLISH_READY: "4. 게시 가능",
  RESTRICTED: "5. 게시 제한 또는 오류",
};

export const CONTENT_TYPE_LABEL: Record<ContentType, string> = {
  COMMENT: "대화형 댓글 초안",
  REPLY: "대댓글 초안",
  INFORMATIVE: "정보 제공형",
  QUESTION: "질문형",
  EMPATHY: "공감형",
  SNS_POST: "SNS 자체 게시물",
  YOUTUBE_META: "유튜브 제목·설명",
  SHORT_HOOK: "쇼츠·릴스 후킹",
  BLOG_COPY: "블로그 홍보 문안",
  AD_DISCLOSURE: "광고 표시 문구",
};

export const CONTENT_STATUS_LABEL: Record<ContentStatus, string> = {
  DRAFT: "초안",
  PENDING_REVIEW: "검토 대기",
  APPROVED: "승인",
  REJECTED: "반려",
  CHANGES_REQUESTED: "수정 요청",
};

export const REVIEW_STATUS_LABEL: Record<ReviewStatus, string> = {
  UNREVIEWED: "미검토",
  SUITABLE: "적합",
  UNSUITABLE: "부적합",
  ON_HOLD: "보류",
};

export const PUBLICATION_STATUS_LABEL: Record<PublicationStatus, string> = {
  QUEUED: "실행 대기",
  SUCCESS: "성공",
  FAILED: "실패",
  BLOCKED: "사전검사 차단",
};

export const METRIC_SOURCE_LABEL: Record<MetricSource, string> = {
  SIMULATED: "모의 실적",
  DEMO_SEED: "데모 데이터",
  VERIFIED: "실측(검증됨)",
  NOT_MEASURED: "미측정",
};

export const RISK_LABEL: Record<RiskLevel, string> = { LOW: "낮음", MEDIUM: "보통", HIGH: "높음" };

export const POLICY_STATUS_LABEL: Record<PolicyReviewStatus, string> = {
  NOT_REVIEWED: "검토 미완료",
  IN_PROGRESS: "검토 중",
  COMPLETED: "검토 완료",
};

export const COST_TYPE_LABEL: Record<CostType, string> = {
  AI_GENERATION: "AI 생성 비용",
  AD_SPEND: "광고비",
  OTHER: "기타",
};

export const INQUIRY_SOURCE_LABEL: Record<import("@prisma/client").InquirySource, string> = {
  KMONG: "크몽",
  PHONE: "전화",
  EMAIL: "이메일",
  WEBSITE: "홈페이지",
  KAKAO: "카카오톡",
  OTHER: "기타",
};

export const INQUIRY_STATUS_LABEL: Record<import("@prisma/client").InquiryStatus, string> = {
  NEW: "신규",
  QUOTED: "견적 발송",
  WON: "계약 전환",
  LOST: "미계약 종료",
};

export const TASK_STATUS_LABEL: Record<import("@prisma/client").TaskStatus, string> = {
  TODO: "대기",
  IN_PROGRESS: "진행 중",
  DONE: "완료",
  BLOCKED: "보류·문제",
};
