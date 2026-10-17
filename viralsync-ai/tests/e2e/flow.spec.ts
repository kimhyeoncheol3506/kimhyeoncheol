import { expect, test, type Page } from "@playwright/test";

async function demoLogin(page: Page, email: string) {
  await page.goto("/login");
  await page.locator(`form:has(input[value="${email}"]) button`).click();
  await expect(page).toHaveURL(/\/dashboard/);
}

async function logout(page: Page) {
  await page.getByRole("button", { name: "로그아웃" }).click();
  await expect(page).toHaveURL(/\/login/);
}

const stamp = Date.now();
const CLIENT = `E2E 테스트 고객 ${stamp}`;
const CAMPAIGN = `E2E 홈트 앱 캠페인 ${stamp}`;

test.describe.serial("핵심 사용자 흐름", () => {
  test("1. 미로그인 → 로그인 화면, 데모 로그인 → 대시보드", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/);
    await demoLogin(page, "manager@demo.viralsync.example");
    await expect(page.getByRole("heading", { name: "대시보드" })).toBeVisible();
    await expect(page.getByText("매체별 게시 횟수")).toBeVisible();
    await expect(page.getByText("게시 완료 건수")).toBeVisible();
  });

  test("2. 이메일/비밀번호 로그인 실패·성공", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("이메일").fill("admin@demo.viralsync.example");
    await page.getByLabel("비밀번호").fill("wrong");
    await page.getByRole("button", { name: "로그인", exact: true }).click();
    await expect(page.getByText("이메일 또는 비밀번호가 올바르지 않습니다.")).toBeVisible();
    await expect(page.getByLabel("이메일")).toHaveValue("admin@demo.viralsync.example");
    await page.getByLabel("비밀번호").fill("demo1234!");
    await page.getByRole("button", { name: "로그인", exact: true }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test("3. 고객 등록·수정, 캠페인 접수·분류, 후보 연결, 문구 생성·검토요청", async ({ page }) => {
    await demoLogin(page, "manager@demo.viralsync.example");

    // 고객 등록 (검증 오류 먼저)
    await page.goto("/clients/new");
    await page.getByRole("button", { name: "고객 등록" }).click();
    await expect(page.getByText("고객명을 입력하세요.")).toBeVisible();
    await page.getByLabel("고객명").fill(CLIENT);
    await page.getByLabel("고객사 담당자").fill("E2E 담당자");
    await page.getByLabel("홍보 대상 URL").fill("https://fit-e2e.example/app");
    await page.getByLabel("상품 또는 서비스 설명").fill("하루 15분 홈트 앱. 운동 기록과 맞춤 루틴을 제공합니다.");
    await page.getByLabel("핵심 타깃", { exact: true }).fill("운동을 시작하려는 30대 직장인");
    await page.getByLabel("필수 표현").fill("#E2E핏");
    await page.getByRole("button", { name: "고객 등록" }).click();
    await expect(page.getByText("고객이 등록되었습니다.")).toBeVisible();
    await page.waitForLoadState("networkidle"); // 클라이언트 이동 직후 하이드레이션 완료 대기

    // 수정
    await page.getByLabel("고객사 담당자").fill("E2E 담당자(수정)");
    await page.getByRole("button", { name: "변경사항 저장" }).click();
    await expect(page.getByText("고객 정보가 저장되었습니다.")).toBeVisible();

    // 광고 의뢰 접수
    await page.getByRole("link", { name: "+ 광고 의뢰 접수" }).click();
    await expect(page).toHaveURL(/\/campaigns\/new/);
    await page.waitForLoadState("networkidle");
    await page.getByLabel("의뢰 제목").fill(CAMPAIGN);
    await page.getByLabel("홍보 대상 URL").fill("http://localhost/x");
    await expect(page.getByText("내부망·로컬 주소는 등록할 수 없습니다.")).toBeVisible();
    await page.getByLabel("홍보 대상 URL").fill("https://fit-e2e.example/app");
    await expect(page.getByText(/URL 형식 확인됨/)).toBeVisible();
    await page.getByLabel("홍보 대상 유형").selectOption("APP");
    await page.getByLabel("주요 목표").selectOption("INSTALLS");
    await page.getByLabel("핵심 타깃").fill("30대 직장인");
    await page.getByLabel("주요 키워드").fill("홈트, 운동, 다이어트");
    await page.getByLabel("의뢰 상세 설명").fill("하루 15분 홈트 앱 설치를 유도하는 캠페인입니다. 운동 초보 직장인 대상.");
    await page.getByRole("button", { name: "의뢰 접수" }).click();
    await expect(page.getByText("희망 SNS 를 하나 이상 선택하세요.")).toBeVisible();
    // 검증 오류 후에도 입력값이 유지되어야 한다
    await expect(page.getByLabel("의뢰 제목")).toHaveValue(CAMPAIGN);
    await expect(page.getByLabel("주요 키워드")).toHaveValue("홈트, 운동, 다이어트");
    await page.getByLabel("Instagram").check();
    await page.getByLabel("TikTok").check();
    await page.getByRole("button", { name: "의뢰 접수" }).click();
    await expect(page.getByText("광고 의뢰가 저장되었습니다.")).toBeVisible();
    await page.waitForLoadState("networkidle");
    const campaignUrl = page.url();

    // AI 분석
    await page.getByRole("button", { name: "AI 분석 실행" }).click();
    await expect(page.getByText(/분석 완료: 건강·생활/)).toBeVisible();
    await expect(page.getByText("광고 정책 위험도")).toBeVisible();
    await expect(page.getByText("AI 분석 완료").first()).toBeVisible();

    // 홍보 기회 탐색 → 점수 확인 → 연결
    await page.goto("/opportunities");
    await page.getByLabel("평가 기준 캠페인").selectOption({ label: `${CLIENT} — ${CAMPAIGN}` });
    await page.getByLabel("검색", { exact: true }).fill("홈트");
    await page.getByRole("button", { name: "적용" }).click();
    await expect(page.getByText(/기준 점수를 실시간 계산했습니다/)).toBeVisible();
    await page.getByRole("button", { name: "캠페인에 연결" }).first().click();
    await expect(page.getByText(/연결 완료 · 관련성/)).toBeVisible();

    // 문구 생성
    await page.goto(`/content?campaignId=${campaignUrl.split("/campaigns/")[1].split("?")[0]}`);
    await expect(page.getByText("AI Provider: demo")).toBeVisible();
    await page.getByRole("button", { name: "문구 생성" }).click();
    await expect(page.getByText(/4건의 초안을 생성했습니다/)).toBeVisible();

    // 캠페인 상세에서 검토 요청
    await page.goto(campaignUrl);
    await page.getByRole("button", { name: /초안 4건 검토 요청/ }).click();
    await expect(page.getByText("4건을 검토 요청했습니다.")).toBeVisible();
    await logout(page);
  });

  test("4a. 배정 전 검토자는 새 고객 문구를 볼 수 없고, 관리자가 고객 접근 권한을 부여", async ({ page }) => {
    await demoLogin(page, "reviewer@demo.viralsync.example");
    await page.goto("/approvals");
    await expect(page.locator("article", { hasText: CAMPAIGN })).toHaveCount(0);
    await logout(page);

    await demoLogin(page, "admin@demo.viralsync.example");
    await page.goto("/settings/users");
    const row = page.locator("form", { hasText: "reviewer@demo.viralsync.example" });
    await row.getByLabel(CLIENT).check();
    await row.getByRole("button", { name: "저장" }).click();
    await expect(page.getByText("저장했습니다.")).toBeVisible();
    await logout(page);
  });

  test("4. 검토자 승인·반려", async ({ page }) => {
    await demoLogin(page, "reviewer@demo.viralsync.example");
    await page.goto("/approvals");
    const card = page.locator("article", { hasText: CAMPAIGN }).first();
    await expect(card).toBeVisible();
    await card.getByRole("button", { name: "승인" }).click();
    await expect(page.getByText("승인했습니다.")).toBeVisible();
    const card2 = page.locator("article", { hasText: CAMPAIGN }).first();
    await card2.getByRole("button", { name: "반려" }).click();
    await expect(page.getByText("반려 또는 수정 요청 시 사유를 입력하세요.")).toBeVisible();
    await card2.getByPlaceholder(/검토 의견/).fill("E2E 반려 사유");
    await card2.getByRole("button", { name: "반려" }).click();
    await expect(page.getByText("반려했습니다.")).toBeVisible();
    await logout(page);
  });

  test("5. 모의 실행 → 실적 기록 → 대시보드/CSV 반영", async ({ page, request }) => {
    await demoLogin(page, "manager@demo.viralsync.example");
    await page.goto("/reports?platform=INSTAGRAM");
    const before = Number((await page.locator("li", { hasText: "Instagram" }).first().locator("span.tabular-nums").innerText()).split("건")[0].replace(/,/g, ""));

    await page.goto("/executions");
    const block = page.locator("div.grid", { hasText: CAMPAIGN }).first();
    await expect(block.getByText("실행 전 미리보기")).toBeVisible();
    await block.getByLabel("플랫폼").selectOption("INSTAGRAM");
    await block.getByRole("button", { name: "실행 대기 등록" }).click();
    await expect(page.getByText(/실행 대기열에 등록했습니다/)).toBeVisible();

    await page.goto("/executions?status=QUEUED&platform=INSTAGRAM");
    const row = page.locator("tr", { hasText: CAMPAIGN }).first();
    await expect(row.getByText("실제 게시 불가: 공식 API 자격증명 미설정")).toBeVisible();
    await expect(row.getByRole("button", { name: "실제 게시" })).toHaveCount(0);
    await row.getByRole("button", { name: "모의 실행" }).click();
    await expect(page.getByText(/\[모의\] 실행 성공|실행 실패 \[/)).toBeVisible();
    // 재현된 일시 오류면 재시도
    for (let i = 0; i < 4; i++) {
      if (await page.getByText(/\[모의\] 실행 성공/).isVisible()) break;
      await page.goto("/executions?status=FAILED&platform=INSTAGRAM");
      const failed = page.locator("tr", { hasText: CAMPAIGN }).first();
      if (!(await failed.isVisible())) break;
      await failed.getByRole("button", { name: "모의 재시도" }).click();
      await expect(page.getByText(/\[모의\] 실행 성공|실행 실패 \[/)).toBeVisible();
    }
    await expect(page.getByText(/\[모의\] 실행 성공/)).toBeVisible();

    await page.goto("/reports?platform=INSTAGRAM");
    const after = Number((await page.locator("li", { hasText: "Instagram" }).first().locator("span.tabular-nums").innerText()).split("건")[0].replace(/,/g, ""));
    expect(after).toBe(before + 1);
    await expect(page.locator("tr", { hasText: CAMPAIGN }).first().getByText("모의 실적")).toBeVisible();

    const csv = await page.request.get("/api/export/publications");
    expect(csv.status()).toBe(200);
    expect(csv.headers()["content-type"]).toContain("text/csv");
    const text = await csv.text();
    expect(text).toContain(CAMPAIGN);
    expect(text).toContain("모의 실적");
    const csv2 = await page.request.get("/api/export/campaigns");
    expect(await csv2.text()).toContain(CAMPAIGN);
    // 비로그인 요청은 401
    expect((await request.get("/api/export/campaigns")).status()).toBe(401);
  });

  test("6. 권한 분리: 읽기 전용 사용자", async ({ page }) => {
    await demoLogin(page, "viewer@demo.viralsync.example");
    await expect(page.getByRole("link", { name: /직원·권한/ })).toHaveCount(0);
    await page.goto("/settings/users");
    await expect(page.getByText("접근 권한 없음")).toBeVisible();
    await page.goto("/clients");
    await expect(page.getByText(CLIENT)).toHaveCount(0); // 배정되지 않은 고객은 보이지 않음
    await expect(page.getByText("권한 없음").first()).toBeVisible(); // 예산 마스킹
    expect((await page.request.get("/api/export/publications")).status()).toBe(403);
    await page.goto("/dashboard");
    await expect(page.getByText("비용 데이터 열람 권한이 없습니다.")).toBeVisible();
  });

  test("7. 타 조직 데이터 격리", async ({ page }) => {
    await demoLogin(page, "admin@demo.viralsync.example");
    await page.goto("/search?q=보이면 안 됨");
    await expect(page.getByText("검색 결과가 없습니다")).toBeVisible();
    await logout(page);
    await demoLogin(page, "other-admin@demo.viralsync.example");
    await page.goto("/clients");
    await expect(page.getByText(CLIENT)).toHaveCount(0);
    await expect(page.getByText("[데모] 타사 전용 고객 — 보이면 안 됨")).toBeVisible();
  });

  test("8. 관리자 전체 화면 렌더링 확인", async ({ page }) => {
    await demoLogin(page, "admin@demo.viralsync.example");
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    for (const path of ["/dashboard", "/clients", "/campaigns", "/opportunities", "/content", "/approvals", "/executions", "/platforms", "/reports", "/reports/monthly", "/policies", "/policies/new", "/settings/users", "/audit", "/search?q=커피", "/campaigns/new", "/clients/new"]) {
      const res = await page.goto(path);
      expect(res?.status(), path).toBeLessThan(400);
      await expect(page.getByText("화면을 불러오지 못했습니다"), path).toHaveCount(0);
      await expect(page.locator("h1").first(), path).toBeVisible();
    }
    // 정책: 공식 문서 확인 없이 '검토 완료' 저장 불가
    await page.goto("/policies/new");
    await page.getByLabel("공식 정책 URL").fill("https://www.tiktok.com/community-guidelines");
    await page.getByLabel("검토 상태").selectOption("COMPLETED");
    await page.getByRole("button", { name: "정책 검토 등록" }).click();
    await expect(page.getByText(/마지막 검토일과 검토 결과/)).toBeVisible();
    // SNS 통합: 모든 플랫폼 데모 전용
    await page.goto("/platforms");
    await expect(page.getByText("1. 데모 전용").first()).toBeVisible();
    expect(errors).toEqual([]);
  });

  test("9. 모바일 화면 메뉴", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await demoLogin(page, "manager@demo.viralsync.example");
    await page.getByRole("button", { name: "메뉴 열기" }).click();
    await page.getByRole("dialog").getByRole("link", { name: /고객관리/ }).click();
    await expect(page).toHaveURL(/\/clients/);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    expect(overflow).toBe(false);
  });
});
