import type { Prisma } from "@prisma/client";
import { MONTHLY_PLANS } from "../src/lib/business/playbook";

/** 모든 조직이 공유하는 기본 데이터 — 데모 시드와 실제 관리자 생성(scripts/create-admin.ts)에서 함께 쓴다 */
export const PLATFORMS: Prisma.SocialPlatformCreateInput[] = [
  { key: "THREADS", name: "Threads", policyUrl: "https://developers.facebook.com/docs/threads", maxTextLength: 500, dailyLimit: 250, supportsComment: true },
  { key: "INSTAGRAM", name: "Instagram", policyUrl: "https://help.instagram.com/477434105621119", maxTextLength: 2200, dailyLimit: 20, supportsComment: true },
  { key: "TIKTOK", name: "TikTok", policyUrl: "https://www.tiktok.com/community-guidelines", maxTextLength: 2200, dailyLimit: 10, supportsComment: false },
  { key: "X", name: "X", policyUrl: "https://help.x.com/en/rules-and-policies", maxTextLength: 280, dailyLimit: 30, supportsComment: true },
  { key: "FACEBOOK", name: "Facebook", policyUrl: "https://transparency.meta.com/policies/ad-standards/", maxTextLength: 5000, dailyLimit: 20, supportsComment: true },
  { key: "YOUTUBE", name: "YouTube", policyUrl: "https://support.google.com/youtube/answer/154235", maxTextLength: 5000, dailyLimit: 10, supportsComment: true },
  { key: "BLOG", name: "블로그", policyUrl: "https://www.ftc.go.kr", maxTextLength: 20000, dailyLimit: 10, supportsComment: false },
];

// 서비스 상품 카탈로그 (샘플 가격 — 서비스 상품 화면에서 수정)
export const PACKAGES: Omit<Prisma.ServicePackageCreateManyInput, "organizationId">[] = [
  { name: "블로그 포스팅 관리대행 (키워드 1개·월 4건)", channel: "BLOG", unitPrice: 220_000, unit: "월", description: "키워드 분석, 원고 작성, 이미지 편집, 광고 표시 포함 발행", deliverables: ["키워드 분석", "포스팅 4건", "월간 리포트"], leadTimeDays: 7 },
  { name: "블로그 체험단 모집·운영 (10명)", channel: "EXPERIENCE_GROUP", unitPrice: 330_000, unit: "회", description: "체험단 모집·일정 조율·가이드 전달 (후기 내용은 체험자 자율, 협찬 표시 필수)", deliverables: ["모집 공고", "체험자 10명", "게시물 링크 정리"], leadTimeDays: 14 },
  { name: "네이버 플레이스 관리", channel: "NAVER_PLACE", unitPrice: 150_000, unit: "월", description: "기본 정보·메뉴·사진 정비, 소식 발행, 리뷰 응대 가이드 (리뷰 조작 없음)", deliverables: ["정보 정비", "소식 4회", "리뷰 응대 가이드"], leadTimeDays: 5 },
  { name: "인스타그램 피드·릴스 운영 (월 8건)", channel: "INSTAGRAM", unitPrice: 300_000, unit: "월", description: "콘텐츠 기획·제작·업로드", deliverables: ["피드 6건", "릴스 2건"], leadTimeDays: 7 },
  { name: "인스타그램 인플루언서 협찬 (5명)", channel: "INSTAGRAM", unitPrice: 450_000, unit: "회", description: "인플루언서 섭외·유료 파트너십 표시 안내", deliverables: ["섭외 5명", "게시물 링크"], leadTimeDays: 14 },
  { name: "메타(인스타·페북) 광고 운영대행", channel: "META_AD", unitPrice: 200_000, unit: "월", description: "타깃 설정·소재 제작·최적화 (매체비 별도, 고객 계정 결제 권장)", deliverables: ["소재 3종", "주간 최적화", "월간 리포트"], leadTimeDays: 5, mediaSpendSeparate: true },
  { name: "네이버 검색광고 운영대행", channel: "SEARCH_AD", unitPrice: 200_000, unit: "월", description: "키워드·입찰·문안 관리 (매체비 별도)", deliverables: ["키워드 세팅", "입찰 관리", "월간 리포트"], leadTimeDays: 5, mediaSpendSeparate: true },
  { name: "유튜브 쇼츠 제작 (3편)", channel: "YOUTUBE", unitPrice: 300_000, unit: "회", description: "기획·촬영 가이드·편집", deliverables: ["쇼츠 3편"], leadTimeDays: 10 },
  { name: "틱톡 숏폼 제작 (3편)", channel: "TIKTOK", unitPrice: 270_000, unit: "회", description: "기획·편집·업로드", deliverables: ["숏폼 3편"], leadTimeDays: 10 },
  { name: "당근 비즈프로필·지역광고 세팅", channel: "KARROT", unitPrice: 100_000, unit: "회", description: "비즈프로필 정비, 지역광고 세팅 (광고비 별도)", deliverables: ["비즈프로필", "광고 세팅"], leadTimeDays: 3, mediaSpendSeparate: true },
  { name: "종합광고대행 패키지", channel: "PACKAGE", unitPrice: 380_000, unit: "월", description: "블로그·플레이스·SNS 기본 관리를 묶은 패키지 (견적 참고용)", deliverables: ["블로그 2건", "플레이스 관리", "인스타 4건"], leadTimeDays: 7 },
  // 월 정액 SNS·숏폼 운영대행 (책 PART 3-1)
  ...MONTHLY_PLANS.map((p) => ({ name: `월 정액 ${p.name}`, channel: "MONTHLY_SNS" as const, unitPrice: p.monthlyFee, unit: "월", description: p.note, deliverables: [...p.deliverables], leadTimeDays: 3 })),
];
