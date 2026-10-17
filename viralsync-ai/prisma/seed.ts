/* eslint-disable no-console */
/**
 * 데모 데이터 시드. 모든 데이터는 isDemo=true 이며 이름에 [데모] 표시가 붙습니다.
 * URL 은 예약 도메인(*.example)을 사용해 실제 계정·게시물로 오인되지 않도록 합니다.
 * 데모 데이터가 이미 있으면 아무 것도 하지 않습니다. 데모 데이터만 다시 만들기: npm run db:reset
 */
import bcrypt from "bcryptjs";
import { PrismaClient, type CampaignGoal, type ContentType, type PlatformKey, type Prisma, type TargetType } from "@prisma/client";
import { analyzeBrief, classify, scoreCandidate } from "../src/lib/analysis/engine";
import { DemoProvider } from "../src/lib/ai/demo-provider";
import { defaultDisclosure, inspectDraft } from "../src/lib/ai/guardrails";
import { getAdapter } from "../src/lib/adapters/platforms";
import { contentHash, finalText, simulatedMetrics } from "../src/lib/services/publications";
import { recomputeCampaignStatus } from "../src/lib/services/campaigns";
import { convertInquiry, createInquiry, saveQuote } from "../src/lib/services/inquiries";
import type { Ctx } from "../src/lib/auth/context";

const prisma = new PrismaClient();
const DAY = 86_400_000;
const now = Date.now();
const daysAgo = (n: number) => new Date(now - n * DAY);
const PASSWORD = "demo1234!";

const PLATFORMS: Prisma.SocialPlatformCreateInput[] = [
  { key: "INSTAGRAM", name: "Instagram", policyUrl: "https://help.instagram.com/477434105621119", maxTextLength: 2200, dailyLimit: 20, supportsComment: true },
  { key: "TIKTOK", name: "TikTok", policyUrl: "https://www.tiktok.com/community-guidelines", maxTextLength: 2200, dailyLimit: 10, supportsComment: false },
  { key: "X", name: "X", policyUrl: "https://help.x.com/en/rules-and-policies", maxTextLength: 280, dailyLimit: 30, supportsComment: true },
  { key: "FACEBOOK", name: "Facebook", policyUrl: "https://transparency.meta.com/policies/ad-standards/", maxTextLength: 5000, dailyLimit: 20, supportsComment: true },
  { key: "YOUTUBE", name: "YouTube", policyUrl: "https://support.google.com/youtube/answer/154235", maxTextLength: 5000, dailyLimit: 10, supportsComment: true },
  { key: "BLOG", name: "블로그", policyUrl: "https://www.ftc.go.kr", maxTextLength: 20000, dailyLimit: 10, supportsComment: false },
];

interface ClientSeed {
  name: string;
  contactName: string;
  promoUrl: string;
  budget: number;
  companyIntro: string;
  productDescription: string;
  coreTarget: string;
  bannedPhrases: string[];
  requiredPhrases: string[];
  toneOfVoice: string;
}

const CLIENTS: ClientSeed[] = [
  {
    name: "[데모] 하늘커피 로스터리",
    contactName: "김하늘(가상)",
    promoUrl: "https://haneul-coffee.example/subscribe",
    budget: 3_000_000,
    companyIntro: "스페셜티 원두를 매주 로스팅해 배송하는 소규모 로스터리입니다.",
    productDescription: "원두 정기구독 서비스. 매주 로스팅한 원두를 집으로 배송합니다. 커피 취향에 맞춰 원두를 고를 수 있습니다.",
    coreTarget: "홈카페를 즐기는 20~40대 직장인",
    bannedPhrases: ["최저가", "카페인 없음"],
    requiredPhrases: ["#하늘커피"],
    toneOfVoice: "따뜻하고 차분한 말투",
  },
  {
    name: "[데모] 코드런 아카데미",
    contactName: "박코드(가상)",
    promoUrl: "https://coderun-academy.example/bootcamp",
    budget: 8_000_000,
    companyIntro: "비전공자를 위한 온라인 코딩교육 부트캠프입니다.",
    productDescription: "12주 웹 개발 부트캠프. 현업 개발자 멘토링과 프로젝트 중심 강의를 제공합니다.",
    coreTarget: "개발자로 취업을 준비하는 비전공 20대 대학생과 직장인",
    bannedPhrases: ["취업 100% 보장", "무조건 합격"],
    requiredPhrases: [],
    toneOfVoice: "친근하지만 정확한 정보 위주",
  },
  {
    name: "[데모] 핏데일리 앱",
    contactName: "이핏(가상)",
    promoUrl: "https://fitdaily.example/app",
    budget: 5_000_000,
    companyIntro: "하루 15분 홈트 루틴을 추천하는 운동 앱입니다.",
    productDescription: "홈트 앱. 운동 기록과 맞춤 루틴을 제공하며 무료 체험 7일을 지원합니다.",
    coreTarget: "운동을 시작하려는 30대 직장인",
    bannedPhrases: ["살 빠짐 보장", "의학적 효과"],
    requiredPhrases: ["#핏데일리"],
    toneOfVoice: "활기차고 응원하는 말투",
  },
  {
    name: "[데모] 글로우랩 스킨케어",
    contactName: "최글로우(가상)",
    promoUrl: "https://glowlab.example/suncream",
    budget: 6_000_000,
    companyIntro: "민감 피부를 위한 저자극 스킨케어 브랜드입니다.",
    productDescription: "저자극 선크림. 백탁이 적고 가벼운 사용감의 데일리 선크림입니다.",
    coreTarget: "민감 피부 고민이 있는 20~30대 여성",
    bannedPhrases: ["피부과 추천 1위", "완치"],
    requiredPhrases: [],
    toneOfVoice: "깔끔하고 신뢰감 있는 말투",
  },
  {
    name: "[데모] 트립메이트",
    contactName: "정트립(가상)",
    promoUrl: "https://tripmate.example/download",
    budget: 4_000_000,
    companyIntro: "여행 일정을 자동으로 짜 주는 여행 플래너 앱입니다.",
    productDescription: "여행 플래너 앱. 국내여행·해외여행 일정과 맛집 동선을 한 번에 정리합니다.",
    coreTarget: "주말 국내여행을 자주 가는 20~30대",
    bannedPhrases: ["항공권 공짜"],
    requiredPhrases: ["#트립메이트"],
    toneOfVoice: "설레고 가벼운 말투",
  },
];

interface CampaignSeed {
  client: number;
  title: string;
  targetType: TargetType;
  goal: CampaignGoal;
  platforms: PlatformKey[];
  keywords: string[];
  banned: string[];
  description: string;
  coreTarget: string;
  stage: "DRAFT" | "ANALYZED" | "PENDING_REVIEW" | "APPROVED" | "READY_TO_RUN" | "COMPLETED" | "FAILED";
  owner: "admin" | "manager" | "manager2";
  budget: number;
  createdDaysAgo: number;
}

const CAMPAIGNS: CampaignSeed[] = [
  { client: 0, title: "가을 원두 정기구독 런칭", targetType: "PRODUCT", goal: "PURCHASES", platforms: ["INSTAGRAM", "BLOG", "YOUTUBE"], keywords: ["원두", "홈카페", "커피"], banned: ["최저가"], description: "가을 시즌 한정 블렌드 원두 정기구독을 알리는 캠페인입니다. 홈카페 이용자 대상 구매 전환이 목표입니다.", coreTarget: "홈카페 즐기는 직장인", stage: "COMPLETED", owner: "manager", budget: 1_500_000, createdDaysAgo: 40 },
  { client: 0, title: "하늘커피 브이로그 협업", targetType: "YOUTUBE", goal: "VIEWS", platforms: ["YOUTUBE", "INSTAGRAM"], keywords: ["커피", "브이로그", "카페"], banned: [], description: "카페 브이로그 크리에이터와 함께 로스팅 과정을 소개하는 유튜브 영상 조회 캠페인입니다.", coreTarget: "카페 브이로그 시청자", stage: "PENDING_REVIEW", owner: "manager", budget: 900_000, createdDaysAgo: 6 },
  { client: 1, title: "비전공자 코딩 부트캠프 모집", targetType: "BLOG", goal: "INQUIRIES", platforms: ["BLOG", "FACEBOOK", "X"], keywords: ["코딩교육", "부트캠프", "취업"], banned: ["무조건"], description: "12주 웹 개발 부트캠프 수강생 모집. 비전공자 대상 상담 문의 확보가 목표입니다.", coreTarget: "개발자 취업 준비 비전공 대학생", stage: "COMPLETED", owner: "admin", budget: 3_000_000, createdDaysAgo: 35 },
  { client: 1, title: "AI 개발 특강 쇼츠 홍보", targetType: "SHORTS", goal: "CLICKS", platforms: ["YOUTUBE", "TIKTOK", "X"], keywords: ["ai", "개발", "강의"], banned: [], description: "생성형 AI 개발 무료 특강을 쇼츠로 알리고 신청 페이지 클릭을 유도합니다.", coreTarget: "AI 개발에 관심 있는 대학생", stage: "FAILED", owner: "manager", budget: 1_200_000, createdDaysAgo: 20 },
  { client: 2, title: "핏데일리 앱 설치 캠페인", targetType: "APP", goal: "INSTALLS", platforms: ["INSTAGRAM", "TIKTOK", "YOUTUBE"], keywords: ["홈트", "운동", "다이어트"], banned: [], description: "하루 15분 홈트 앱 설치 캠페인. 무료 체험 7일 안내 중심으로 진행합니다.", coreTarget: "운동 시작하려는 30대 직장인", stage: "COMPLETED", owner: "manager", budget: 2_500_000, createdDaysAgo: 28 },
  { client: 2, title: "새해 운동 챌린지 릴스", targetType: "REELS", goal: "VIEWS", platforms: ["INSTAGRAM", "FACEBOOK"], keywords: ["운동", "챌린지", "필라테스"], banned: [], description: "새해 운동 챌린지를 릴스로 알리는 조회 캠페인입니다.", coreTarget: "운동 습관을 만들고 싶은 직장인", stage: "READY_TO_RUN", owner: "manager", budget: 1_000_000, createdDaysAgo: 8 },
  { client: 3, title: "민감피부 선크림 리뷰 협업", targetType: "PRODUCT", goal: "PURCHASES", platforms: ["INSTAGRAM", "BLOG", "YOUTUBE"], keywords: ["선크림", "스킨케어", "피부"], banned: ["1위"], description: "저자극 선크림 협찬 콘텐츠로 구매 전환을 목표로 합니다. 체험담은 크리에이터 본인 콘텐츠에서만 다룹니다.", coreTarget: "민감 피부 20대 여성", stage: "APPROVED", owner: "manager2", budget: 2_000_000, createdDaysAgo: 12 },
  { client: 3, title: "여름 자외선 차단 정보 캠페인", targetType: "BLOG", goal: "VISITS", platforms: ["BLOG", "INSTAGRAM"], keywords: ["선크림", "자외선", "보습"], banned: [], description: "여름철 자외선 차단 정보를 제공하고 브랜드 페이지 방문을 유도합니다.", coreTarget: "피부 관리에 관심 있는 여성", stage: "PENDING_REVIEW", owner: "manager2", budget: 800_000, createdDaysAgo: 4 },
  { client: 4, title: "주말 국내여행 플래너 앱", targetType: "APP", goal: "INSTALLS", platforms: ["INSTAGRAM", "TIKTOK", "X"], keywords: ["국내여행", "제주", "맛집"], banned: [], description: "주말 국내여행 일정 자동 생성 기능을 알리는 앱 설치 캠페인입니다.", coreTarget: "주말 여행 가는 20대", stage: "ANALYZED", owner: "manager2", budget: 1_800_000, createdDaysAgo: 3 },
  { client: 4, title: "해외여행 체크리스트 이벤트", targetType: "OTHER", goal: "CLICKS", platforms: ["FACEBOOK", "X"], keywords: [], banned: [], description: "", coreTarget: "", stage: "DRAFT", owner: "manager2", budget: 500_000, createdDaysAgo: 1 },
];

interface CandSeed {
  platform: PlatformKey;
  account: string;
  title: string;
  summary: string;
}

const CANDIDATES: CandSeed[] = [
  { platform: "INSTAGRAM", account: "@demo_homecafe_diary", title: "주말 홈카페 원두 추천 모음", summary: "핸드드립 홈카페 루틴과 원두 고르는 법을 소개하는 게시물" },
  { platform: "YOUTUBE", account: "데모 커피채널", title: "카페 사장님 로스팅 브이로그", summary: "작은 로스터리의 하루를 담은 카페 브이로그 영상" },
  { platform: "BLOG", account: "demo-coffee-note", title: "직장인 홈카페 입문 가이드", summary: "커피 도구와 원두 구독 서비스 비교 글" },
  { platform: "TIKTOK", account: "@demo_latteart", title: "15초 라떼아트 챌린지", summary: "홈카페 라떼아트 연습 쇼츠" },
  { platform: "BLOG", account: "demo-dev-career", title: "비전공자 개발자 취업 후기 정리", summary: "부트캠프 과정과 취업 준비 과정을 정리한 블로그 글" },
  { platform: "X", account: "@demo_dev_tips", title: "코딩 독학 vs 부트캠프 고민 스레드", summary: "개발 공부 방법에 대한 대학생들의 의견 스레드" },
  { platform: "YOUTUBE", account: "데모 AI 개발 강의", title: "생성형 AI로 챗봇 만들기", summary: "ai 챗봇 개발 입문 강의 영상" },
  { platform: "FACEBOOK", account: "데모 개발자 커뮤니티", title: "주니어 개발자 취업 정보 공유", summary: "개발 취업 공고와 코딩교육 정보를 공유하는 그룹 게시물" },
  { platform: "TIKTOK", account: "@demo_coding_shorts", title: "1분 코딩 꿀팁", summary: "개발 입문자를 위한 짧은 프로그래밍 팁" },
  { platform: "INSTAGRAM", account: "@demo_hometraining", title: "하루 15분 홈트 루틴", summary: "직장인을 위한 홈트 운동 루틴 릴스" },
  { platform: "YOUTUBE", account: "데모 필라테스", title: "초보자 필라테스 따라하기", summary: "운동을 처음 시작하는 직장인을 위한 필라테스 영상" },
  { platform: "TIKTOK", account: "@demo_fit_challenge", title: "30일 운동 챌린지 1일차", summary: "운동 챌린지와 다이어트 기록 쇼츠" },
  { platform: "FACEBOOK", account: "데모 러닝 클럽", title: "퇴근 후 러닝 모임 후기", summary: "직장인 러닝 모임 활동 소개" },
  { platform: "INSTAGRAM", account: "@demo_skin_daily", title: "민감 피부 선크림 고르는 법", summary: "민감 피부 스킨케어 루틴과 선크림 성분 정보" },
  { platform: "YOUTUBE", account: "데모 뷰티랩", title: "여름 자외선 차단 상식 5가지", summary: "선크림 바르는 법과 자외선 정보 영상" },
  { platform: "BLOG", account: "demo-beauty-note", title: "20대 데일리 스킨케어 정리", summary: "보습과 선크림 위주의 피부 관리 글" },
  { platform: "INSTAGRAM", account: "@demo_ootd_look", title: "가을 데일리 코디 룩북", summary: "패션 코디와 ootd 게시물" },
  { platform: "INSTAGRAM", account: "@demo_jeju_trip", title: "제주 2박 3일 맛집 동선", summary: "국내여행 제주 맛집과 카페 코스 정리" },
  { platform: "TIKTOK", account: "@demo_weekend_trip", title: "주말 강릉 당일치기", summary: "국내 여행 당일치기 코스 쇼츠" },
  { platform: "X", account: "@demo_travel_talk", title: "해외여행 준비물 체크리스트", summary: "해외여행 항공권 예약 팁과 준비물 스레드" },
  { platform: "BLOG", account: "demo-trip-planner", title: "부산 맛집 여행 일정표", summary: "부산 국내여행 맛집 일정 정리 글" },
  { platform: "X", account: "@demo_issue_now", title: "이번 주 정치 이슈 정리", summary: "선거와 정당 관련 정치 이슈 요약" },
  { platform: "FACEBOOK", account: "데모 재테크 모임", title: "주식 투자 수익률 인증", summary: "주식 투자 수익률과 코인 정보 게시물" },
  { platform: "YOUTUBE", account: "데모 게임채널", title: "신작 모바일 게임 사전예약 소식", summary: "모바일 게임 rpg 신작 소개" },
];

async function main() {
  if (process.env.SEED_RESET === "true") {
    // 데모 조직(isDemo=true)만 삭제합니다. 실제 조직 데이터는 건드리지 않습니다.
    const demoOrgs = await prisma.organization.findMany({ where: { isDemo: true }, select: { id: true } });
    const ids = demoOrgs.map((o) => o.id);
    await prisma.approval.deleteMany({ where: { content: { organizationId: { in: ids } } } });
    await prisma.organization.deleteMany({ where: { id: { in: ids } } });
    console.log(`기존 데모 조직 ${ids.length}개를 삭제했습니다.`);
  }
  const existing = await prisma.organization.count({ where: { isDemo: true } });
  if (existing > 0) {
    console.log("데모 데이터가 이미 있어 시드를 건너뜁니다. 데모 데이터를 다시 만들려면: npm run db:reset");
    return;
  }

  for (const p of PLATFORMS) await prisma.socialPlatform.upsert({ where: { key: p.key }, create: p, update: p });

  const org = await prisma.organization.create({ data: { name: "[데모] 바이럴싱크 에이전시", isDemo: true } });
  const other = await prisma.organization.create({ data: { name: "[데모] 타 대행사 (테넌트 격리 확인용)", isDemo: true } });
  const hash = await bcrypt.hash(PASSWORD, 10);

  const mkUser = (organizationId: string, email: string, name: string, role: Prisma.UserCreateInput["role"]) =>
    prisma.user.create({ data: { organizationId, email, name, role, passwordHash: hash, isDemo: true } });
  const admin = await mkUser(org.id, "admin@demo.viralsync.example", "[데모] 관리자 한지민", "ADMIN");
  const manager = await mkUser(org.id, "manager@demo.viralsync.example", "[데모] 매니저 오준호", "CAMPAIGN_MANAGER");
  const manager2 = await mkUser(org.id, "manager2@demo.viralsync.example", "[데모] 매니저 서유나", "CAMPAIGN_MANAGER");
  const writer = await mkUser(org.id, "writer@demo.viralsync.example", "[데모] 작성자 문태오", "CONTENT_WRITER");
  const reviewer = await mkUser(org.id, "reviewer@demo.viralsync.example", "[데모] 검토자 윤세라", "REVIEWER");
  const viewer = await mkUser(org.id, "viewer@demo.viralsync.example", "[데모] 열람자 강민", "VIEWER");
  const otherAdmin = await mkUser(other.id, "other-admin@demo.viralsync.example", "[데모] 타사 관리자", "ADMIN");
  const owners = { admin, manager, manager2 };

  const clients: Prisma.ClientGetPayload<{ include: { brandProfile: true } }>[] = [];
  for (const [i, c] of CLIENTS.entries()) {
    clients.push(
      await prisma.client.create({
        data: {
          organizationId: org.id,
          name: c.name,
          contactName: c.contactName,
          contactEmail: `client${i + 1}@demo.viralsync.example`,
          contactPhone: `010-0000-000${i + 1}`,
          promoUrl: c.promoUrl,
          budget: c.budget,
          contractStart: daysAgo(60 - i * 5),
          contractEnd: new Date(now + (120 + i * 30) * DAY),
          managerId: i < 3 ? manager.id : manager2.id,
          isDemo: true,
          brandProfile: {
            create: {
              companyIntro: c.companyIntro,
              productDescription: c.productDescription,
              coreTarget: c.coreTarget,
              bannedPhrases: c.bannedPhrases,
              requiredPhrases: c.requiredPhrases,
              toneOfVoice: c.toneOfVoice,
            },
          },
        },
        include: { brandProfile: true },
      }),
    );
  }
  // 고객 접근 권한: manager → 0,1,2 / manager2 → 3,4 / writer → 0~3 / reviewer → 전체 / viewer → 0
  const access: [string, number[]][] = [
    [manager.id, [0, 1, 2]],
    [manager2.id, [3, 4]],
    [writer.id, [0, 1, 2, 3]],
    [reviewer.id, [0, 1, 2, 3, 4]],
    [viewer.id, [0]],
  ];
  for (const [userId, idx] of access)
    await prisma.clientAccess.createMany({ data: idx.map((i) => ({ userId, clientId: clients[i].id })) });

  // 타 조직 데이터 (격리 확인용)
  const otherClient = await prisma.client.create({
    data: {
      organizationId: other.id,
      name: "[데모] 타사 전용 고객 — 보이면 안 됨",
      contactName: "타사 담당자(가상)",
      isDemo: true,
      brandProfile: { create: { productDescription: "타 조직 데이터", bannedPhrases: [], requiredPhrases: [] } },
    },
  });
  await prisma.campaign.create({
    data: {
      organizationId: other.id,
      clientId: otherClient.id,
      name: "[데모] 타사 캠페인 — 보이면 안 됨",
      ownerId: otherAdmin.id,
      isDemo: true,
      brief: { create: { title: "타사 캠페인", targetType: "OTHER", goal: "VIEWS", desiredPlatforms: ["X"], keywords: [], bannedKeywords: [] } },
    },
  });

  // 홍보 후보 게시물
  const cands = [];
  for (const [i, c] of CANDIDATES.entries()) {
    const n = String(i + 1).padStart(3, "0");
    cands.push(
      await prisma.contentCandidate.create({
        data: {
          organizationId: org.id,
          platform: c.platform,
          accountName: c.account,
          profileUrl: `https://sns-demo.example/${c.platform.toLowerCase()}/${encodeURIComponent(c.account.replace("@", ""))}`,
          postUrl: `https://sns-demo.example/${c.platform.toLowerCase()}/post/${n}`,
          title: `[데모] ${c.title}`,
          summary: c.summary,
          category: classify(`${c.title} ${c.summary}`).category,
          source: "DEMO",
          isDemo: true,
          lastCheckedAt: daysAgo(i % 9),
          createdAt: daysAgo(30 - i),
        },
      }),
    );
  }

  const provider = new DemoProvider();
  const TYPES: ContentType[][] = [
    ["COMMENT", "INFORMATIVE", "SNS_POST", "AD_DISCLOSURE"],
    ["YOUTUBE_META", "SHORT_HOOK", "QUESTION", "EMPATHY"],
    ["BLOG_COPY", "REPLY", "COMMENT", "SNS_POST"],
  ];

  for (const [ci, cs] of CAMPAIGNS.entries()) {
    const client = clients[cs.client];
    const bp = client.brandProfile!;
    const createdAt = daysAgo(cs.createdDaysAgo);
    const campaign = await prisma.campaign.create({
      data: {
        organizationId: org.id,
        clientId: client.id,
        name: cs.title,
        ownerId: owners[cs.owner].id,
        budget: cs.budget,
        startDate: createdAt,
        endDate: new Date(createdAt.getTime() + 30 * DAY),
        isDemo: true,
        createdAt,
        brief: {
          create: {
            title: cs.title,
            targetUrl: client.promoUrl,
            urlCheck: { valid: true, reason: "URL 형식만 확인했습니다. 외부 페이지 내용은 분석하지 않았습니다.", analyzed: false },
            targetType: cs.targetType,
            goal: cs.goal,
            coreTarget: cs.coreTarget,
            desiredPlatforms: cs.platforms,
            keywords: cs.keywords,
            bannedKeywords: cs.banned,
            description: cs.description,
          },
        },
      },
      include: { brief: true },
    });
    await prisma.auditLog.create({
      data: { organizationId: org.id, actorId: owners[cs.owner].id, action: "campaign.create", entityType: "Campaign", entityId: campaign.id, summary: `광고 의뢰 '${cs.title}' 접수`, createdAt },
    });
    if (cs.stage === "DRAFT") continue;

    const analysis = analyzeBrief(
      { title: cs.title, description: cs.description, keywords: cs.keywords, bannedKeywords: cs.banned, coreTarget: cs.coreTarget, targetType: cs.targetType, goal: cs.goal, desiredPlatforms: cs.platforms },
      bp,
    );
    await prisma.campaignBrief.update({
      where: { campaignId: campaign.id },
      data: { category: analysis.category, subcategory: analysis.subcategory, scores: analysis as unknown as Prisma.InputJsonValue, analyzedAt: new Date(createdAt.getTime() + 3600_000), analysisEngine: analysis.engine },
    });
    await prisma.campaign.update({ where: { id: campaign.id }, data: { status: "ANALYZED" } });

    // 관련 후보 상위 2개 연결
    const scored = cands
      .filter((c) => !c.campaignId)
      .map((c) => ({
        c,
        s: scoreCandidate(c, { keywords: cs.keywords, bannedKeywords: cs.banned, coreTarget: cs.coreTarget, desiredPlatforms: cs.platforms, category: analysis.category }, bp),
      }))
      .sort((a, b) => b.s.relevanceScore - a.s.relevanceScore)
      .slice(0, 2);
    const linked = [];
    for (const { c, s } of scored) {
      const u = await prisma.contentCandidate.update({
        where: { id: c.id },
        data: { campaignId: campaign.id, targetMatch: s.targetMatch, relevanceScore: s.relevanceScore, suitable: s.suitable, suitabilityNote: s.note, reviewStatus: s.suitable ? "SUITABLE" : "ON_HOLD", category: s.category },
      });
      c.campaignId = campaign.id;
      linked.push(u);
    }
    if (cs.stage === "ANALYZED") continue;

    // 문구 생성 (데모 Provider)
    const types = TYPES[ci % TYPES.length];
    const target = linked[0] ?? null;
    const gen = await provider.generate(
      {
        clientName: client.name,
        campaignName: cs.title,
        goal: cs.goal,
        targetType: cs.targetType,
        coreTarget: cs.coreTarget,
        keywords: cs.keywords,
        bannedKeywords: cs.banned,
        description: cs.description,
        targetUrl: client.promoUrl,
        brand: bp,
        candidate: target ? { platform: target.platform, accountName: target.accountName, title: target.title, summary: target.summary } : null,
        platform: target?.platform ?? cs.platforms[0],
      },
      types,
    );
    const genAt = new Date(createdAt.getTime() + 2 * 3600_000);
    const contents = [];
    for (const [di, d] of gen.drafts.entries()) {
      const pending = cs.stage === "PENDING_REVIEW";
      const status = pending ? "PENDING_REVIEW" : di === 3 ? (ci % 2 ? "REJECTED" : "CHANGES_REQUESTED") : "APPROVED";
      // 게시 대상 플랫폼: 연결 게시물 플랫폼이 희망 SNS 에 있으면 사용, 아니면 희망 SNS 를 순환
      const platform = target && cs.platforms.includes(target.platform) && di === 0 ? target.platform : cs.platforms[di % cs.platforms.length];
      const content = await prisma.generatedContent.create({
        data: {
          organizationId: org.id,
          campaignId: campaign.id,
          candidateId: di === 0 && target ? target.id : null,
          type: d.type,
          platform,
          body: d.body,
          disclosure: defaultDisclosure(client.name),
          warnings: inspectDraft(d.body, { bannedPhrases: [...bp.bannedPhrases, ...cs.banned], requiredPhrases: bp.requiredPhrases }),
          status,
          model: gen.model,
          provider: gen.provider,
          createdById: writer.id,
          isDemo: true,
          createdAt: genAt,
        },
      });
      if (status !== "PENDING_REVIEW") {
        await prisma.approval.create({
          data: {
            contentId: content.id,
            reviewerId: reviewer.id,
            decision: status,
            comment: status === "APPROVED" ? null : status === "REJECTED" ? "브랜드 문체와 맞지 않아 반려합니다." : "필수 해시태그를 추가해 주세요.",
            createdAt: new Date(genAt.getTime() + 5 * 3600_000),
          },
        });
      }
      if (di === 1 && !pending) {
        await prisma.contentRevision.create({
          data: { contentId: content.id, editorId: writer.id, before: `${d.body} (초기 버전)`, after: d.body, note: "어투 다듬기", createdAt: new Date(genAt.getTime() + 3600_000) },
        });
      }
      contents.push(content);
    }
    await prisma.costRecord.create({
      data: { organizationId: org.id, clientId: client.id, campaignId: campaign.id, type: "AI_GENERATION", amountKrw: 0, description: `${gen.model} 문구 ${gen.drafts.length}건 생성 (데모 Provider, 비용 없음)`, isDemo: true, incurredAt: genAt },
    });

    if (["COMPLETED", "FAILED", "READY_TO_RUN"].includes(cs.stage)) {
      const approved = contents.filter((c) => c.status === "APPROVED");
      for (const [pi, content] of approved.entries()) {
        const platform = content.platform!;
        const sp = PLATFORMS.find((p) => p.key === platform)!;
        const text = finalText(content.body, content.disclosure);
        const targetUrl = content.candidateId ? cands.find((c) => c.id === content.candidateId)?.postUrl ?? null : null;
        const execAt = new Date(genAt.getTime() + (1 + pi) * DAY);
        const h = contentHash(text, platform, targetUrl);
        if (cs.stage === "READY_TO_RUN" && pi === approved.length - 1) {
          await prisma.publication.create({
            data: { organizationId: org.id, campaignId: campaign.id, contentId: content.id, platform, targetUrl, contentHash: h, status: "QUEUED", isDemo: true, createdAt: execAt },
          });
          continue;
        }
        const sim = getAdapter(platform).simulate({ text, targetUrl, kind: targetUrl ? "COMMENT" : "POST", attempt: 0, maxTextLength: sp.maxTextLength });
        // FAILED 캠페인은 실패 사례를 보여 주기 위해 모두 실패 처리
        const ok = cs.stage === "FAILED" ? false : sim.ok || pi === 0;
        const pub = await prisma.publication.create({
          data: {
            organizationId: org.id,
            campaignId: campaign.id,
            contentId: content.id,
            platform,
            targetUrl,
            contentHash: ok ? h : `failed:${h}`,
            mode: "SIMULATED",
            status: ok ? "SUCCESS" : "FAILED",
            externalId: ok ? sim.externalId ?? `sim_seed_${pi}` : null,
            errorCode: ok ? null : sim.errorCode ?? "SIM_RATE_LIMITED",
            errorMessage: ok ? null : sim.errorMessage ?? "[모의] 플랫폼 호출 한도 초과 상황을 재현했습니다. 재시도할 수 있습니다.",
            retryCount: ok ? 0 : 1,
            executedById: owners[cs.owner].id,
            executedAt: execAt,
            isDemo: true,
            createdAt: execAt,
          },
        });
        if (ok) {
          // 성공 건마다 3일치 데모 실적 (DEMO_SEED — 실제 수집값 아님)
          for (let d = 0; d < 3; d++) {
            const m = simulatedMetrics(`${pub.id}|${d}`);
            await prisma.performanceMetric.create({
              data: { organizationId: org.id, campaignId: campaign.id, publicationId: pub.id, date: new Date(execAt.getTime() + d * DAY), clicks: m.clicks, visits: m.visits, conversions: m.conversions, source: "DEMO_SEED" },
            });
          }
        }
      }
      if (cs.stage !== "READY_TO_RUN") {
        await prisma.costRecord.create({
          data: { organizationId: org.id, clientId: client.id, campaignId: campaign.id, type: "AD_SPEND", amountKrw: Math.round(cs.budget * 0.6), description: "[데모] 크리에이터 협찬비 샘플", isDemo: true, incurredAt: new Date(genAt.getTime() + DAY) },
        });
      }
    }
    await prisma.$transaction((tx) => recomputeCampaignStatus(tx, campaign.id));
  }

  // 서비스 상품 카탈로그 (샘플 가격 — 서비스 상품 화면에서 수정)
  const PACKAGES: Omit<Prisma.ServicePackageCreateManyInput, "organizationId">[] = [
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
  ];
  await prisma.servicePackage.createMany({ data: PACKAGES.map((p) => ({ ...p, organizationId: org.id, isDemo: true })) });

  // 광고 문의 샘플 (실제 크몽 문의 유형을 본뜬 가상 문의)
  const managerCtx: Ctx = { userId: manager.id, organizationId: org.id, role: "CAMPAIGN_MANAGER", name: manager.name, clientIds: [clients[0].id, clients[1].id, clients[2].id] };
  const INQUIRIES = [
    {
      customerName: "[데모] 크몽고객A",
      text: "안녕하세요 ! 데모뷰티샵 입니다 혹시 https://demo-beauty.example 사이트도 블러그 가능할까요 ?\n네 키워드는 강남 피부관리, 강남 왁싱, 역삼 피부샵 입니다 <\n혹시 가능한지 여쭙고싶고 가격도 알고 싶습니다,",
      daysAgo: 1,
    },
    {
      customerName: "[데모] 크몽고객B",
      text: "안녕하세요.\n'[데모] 한우담 샤브' 브랜드의 광고대행에 대해 문의드리고 싶어 연락드렸습니다.\n▶홈페이지 : https://hanwoodam-demo.example\n▶인스타그램 : https://www.instagram.com/hanwoodam_demo\n\n○○샤브와 비슷한 느낌의 음식점으로,\n현재 ○○샤브가 하고 있는 광고와 유사한 형태로 광고하고싶습니다.\n\n예산은 얼마정도로 잡아야 할지, 광고의 종류는 어떤 것들을 추천하는지 확인 부탁드립니다.",
      daysAgo: 0,
    },
    {
      customerName: "[데모] 크몽고객C",
      text: "'[데모] 숲속베이커리' 카페입니다. 성수동 매장이고 인스타랑 플레이스 관리 맡기고 싶어요. 월 80만원 정도 생각중인데 가능할까요?",
      daysAgo: 6,
    },
  ];
  const created = [];
  for (const iq of INQUIRIES) {
    const q = await createInquiry(managerCtx, { source: "KMONG", customerName: iq.customerName, rawText: iq.text });
    await prisma.inquiry.update({ where: { id: q.id }, data: { isDemo: true, receivedAt: daysAgo(iq.daysAgo) } });
    created.push(q);
  }
  // 세 번째 문의는 견적 발송 후 계약 전환 → 집행 작업 일부 진행
  const third = await prisma.inquiry.findUniqueOrThrow({ where: { id: created[2].id } });
  await saveQuote(managerCtx, third.id, (third.selectedTier ?? "STANDARD") as "BASIC" | "STANDARD" | "PREMIUM", third.replyDraft ?? "");
  const conv = await convertInquiry(managerCtx, third.id);
  await prisma.campaign.update({ where: { id: conv.campaignId }, data: { isDemo: true } });
  await prisma.client.update({ where: { id: conv.clientId }, data: { isDemo: true } });
  await prisma.clientAccess.createMany({ data: [writer.id, reviewer.id].map((userId) => ({ userId, clientId: conv.clientId })), skipDuplicates: true });
  const tasks = await prisma.fulfillmentTask.findMany({ where: { campaignId: conv.campaignId }, orderBy: { createdAt: "asc" } });
  if (tasks[0])
    await prisma.fulfillmentTask.update({ where: { id: tasks[0].id }, data: { status: "DONE", completedAt: new Date(), note: "[데모] 기본 정보·메뉴 사진 정비 완료, 소식 1회 발행", deliverableUrl: "https://sns-demo.example/place/forest-bakery" } });
  if (tasks[1]) await prisma.fulfillmentTask.update({ where: { id: tasks[1].id }, data: { status: "IN_PROGRESS", note: "[데모] 이번 주 피드 3건 업로드 예정" } });

  // 연결 계정 (데모 전용)
  for (const p of PLATFORMS)
    await prisma.connectedAccount.create({
      data: { organizationId: org.id, platform: p.key as PlatformKey, accountName: `[데모] viralsync_${String(p.key).toLowerCase()}`, status: "DEMO_ONLY", isDemo: true },
    });

  // 정책 검토 샘플
  const policies: Omit<Prisma.PolicyReviewCreateManyInput, "organizationId">[] = [
    { platform: "INSTAGRAM", policyUrl: PLATFORMS[0].policyUrl, status: "COMPLETED", lastReviewedAt: daysAgo(12), nextReviewAt: new Date(now + 18 * DAY), changeSummary: "[데모] 브랜디드 콘텐츠 표시 도구 사용 권장 내용 확인", affectedFeatures: ["SNS 자체 게시물", "댓글 초안"], riskLevel: "MEDIUM", ownerId: reviewer.id, actionItems: "유료 파트너십 라벨 안내 문구 추가", result: "[데모] 샘플 검토 결과 — 실제 공식 문서 확인 기록 아님" },
    { platform: "YOUTUBE", policyUrl: PLATFORMS[4].policyUrl, status: "COMPLETED", lastReviewedAt: daysAgo(20), nextReviewAt: new Date(now + 10 * DAY), changeSummary: "[데모] 유료 PPL 포함 표시 의무 확인", affectedFeatures: ["유튜브 제목·설명"], riskLevel: "LOW", ownerId: reviewer.id, actionItems: "설명란 첫 줄에 유료 광고 고지", result: "[데모] 샘플 검토 결과 — 실제 공식 문서 확인 기록 아님" },
    { platform: "X", policyUrl: PLATFORMS[2].policyUrl, status: "COMPLETED", lastReviewedAt: daysAgo(40), nextReviewAt: daysAgo(10), changeSummary: "[데모] 자동화·중복 게시 규칙 확인", affectedFeatures: ["답글", "자동 실행"], riskLevel: "HIGH", ownerId: admin.id, actionItems: "중복 검사·일일 한도 적용", result: "[데모] 샘플 검토 결과 — 재검토 기한 경과" },
    { platform: "TIKTOK", policyUrl: PLATFORMS[1].policyUrl, status: "NOT_REVIEWED", nextReviewAt: new Date(now + 5 * DAY), changeSummary: "", affectedFeatures: ["쇼츠·릴스 후킹"], riskLevel: "MEDIUM", ownerId: reviewer.id, actionItems: "", result: "" },
    { platform: "FACEBOOK", policyUrl: PLATFORMS[3].policyUrl, status: "IN_PROGRESS", nextReviewAt: new Date(now + 3 * DAY), changeSummary: "[데모] 광고 표준 문서 검토 중", affectedFeatures: ["SNS 자체 게시물"], riskLevel: "LOW", ownerId: admin.id, actionItems: "", result: "" },
    { platform: "BLOG", policyUrl: PLATFORMS[5].policyUrl, status: "NOT_REVIEWED", nextReviewAt: new Date(now + 25 * DAY), changeSummary: "", affectedFeatures: ["블로그 홍보 문안"], riskLevel: "HIGH", ownerId: reviewer.id, actionItems: "추천·보증 심사지침 확인 필요", result: "" },
  ];
  await prisma.policyReview.createMany({ data: policies.map((p) => ({ ...p, organizationId: org.id, isDemo: true })) });

  const counts = {
    clients: await prisma.client.count({ where: { organizationId: org.id } }),
    campaigns: await prisma.campaign.count({ where: { organizationId: org.id } }),
    candidates: await prisma.contentCandidate.count({ where: { organizationId: org.id } }),
    contents: await prisma.generatedContent.count({ where: { organizationId: org.id } }),
    publications: await prisma.publication.count({ where: { organizationId: org.id } }),
    metrics: await prisma.performanceMetric.count({ where: { organizationId: org.id } }),
    packages: await prisma.servicePackage.count({ where: { organizationId: org.id } }),
    inquiries: await prisma.inquiry.count({ where: { organizationId: org.id } }),
    tasks: await prisma.fulfillmentTask.count({ where: { organizationId: org.id } }),
  };
  console.log("데모 데이터 생성 완료:", counts);
  console.log(`데모 계정 비밀번호: ${PASSWORD} (admin/manager/manager2/writer/reviewer/viewer @demo.viralsync.example)`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
