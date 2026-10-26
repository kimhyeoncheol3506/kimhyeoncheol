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
    await expect(page.getByText(/^(최종 )?승인했습니다/)).toBeVisible();
    const card2 = page.locator("article", { hasText: CAMPAIGN }).first();
    await card2.getByRole("button", { name: "반려" }).click();
    await expect(page.getByText("반려 또는 수정 요청 시 사유를 입력하세요.")).toBeVisible();
    await card2.getByPlaceholder(/결재 의견/).fill("E2E 반려 사유");
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
    for (const path of ["/dashboard", "/inquiries", "/inquiries/new", "/services", "/fulfillment", "/clients", "/campaigns", "/opportunities", "/content", "/approvals", "/approvals?tab=done", "/organization", "/settings/approval-rules", "/executions", "/platforms", "/reports", "/reports/monthly", "/policies", "/policies/new", "/settings/users", "/audit", "/search?q=커피", "/campaigns/new", "/clients/new"]) {
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

test.describe.serial("광고 문의 → 견적 → 계약 → 집행", () => {
  const NAME = `E2E 크몽고객 ${Date.now()}`;
  const BRAND = `E2E샤브${Date.now() % 100000}`;

  test("문의 붙여넣기 → 자동 분석 → 견적·답변 → 계약 전환 → 작업 완료", async ({ page }) => {
    await demoLogin(page, "manager@demo.viralsync.example");
    await page.goto("/inquiries");
    await expect(page.getByRole("heading", { name: "문의 접수함" })).toBeVisible();
    await page.getByRole("link", { name: "+ 문의 붙여넣기" }).click();
    await expect(page).toHaveURL(/\/inquiries\/new/);
    await page.waitForLoadState("networkidle");
    await page.getByRole("button", { name: "접수하고 자동 분석" }).click();
    await expect(page.getByText("고객 이름(닉네임)을 입력하세요.")).toBeVisible();
    await page.getByLabel("고객 이름·닉네임").fill(NAME);
    await page.getByLabel("문의 원문").fill(
      `안녕하세요.\n'${BRAND}' 브랜드의 광고대행에 대해 문의드리고 싶어 연락드렸습니다.\n▶홈페이지 : https://e2e-shabu.example\n▶인스타그램 : https://www.instagram.com/e2e_shabu\n\n비슷한 느낌의 음식점으로, 유사한 형태로 광고하고싶습니다.\n예산은 얼마정도로 잡아야 할지, 광고의 종류는 어떤 것들을 추천하는지 확인 부탁드립니다.`,
    );
    await page.getByRole("button", { name: "접수하고 자동 분석" }).click();
    await expect(page).toHaveURL(/\/inquiries\/c/);
    await page.waitForLoadState("networkidle");

    // 자동 분석 결과
    await expect(page.getByRole("heading", { name: `${NAME}님 문의` })).toBeVisible();
    await expect(page.getByText(BRAND, { exact: true })).toBeVisible();
    await expect(page.getByText(/음식점\s*\(분류/)).toBeVisible();
    await expect(page.getByText("종합대행 희망")).toBeVisible();
    await expect(page.getByText("고객에게 더 물어볼 것")).toBeVisible();

    // 견적안 변경 → 답변 자동 갱신
    const reply = page.getByLabel(/고객 답변 초안/);
    await expect(reply).toHaveValue(/표준형 \(추천\)/);
    await page.locator("label", { hasText: "집중형" }).click();
    await expect(reply).toHaveValue(/집중형 \(추천\)/);
    await expect(reply).toHaveValue(/크몽 안전결제/);
    await page.getByRole("button", { name: /견적·답변 저장/ }).click();
    // 집중형은 100만원 이상 → 관리자 결재 대기, 결재 전에는 계약 전환 불가
    await expect(page.getByText("견적이 결재 기준 이상이라 결재를 요청했습니다.", { exact: false })).toBeVisible();
    const inquiryUrl = page.url();
    await page.getByRole("button", { name: "계약 전환 (캠페인 생성)" }).click();
    await expect(page.getByText(/결재/).first()).toBeVisible();
    await logout(page);

    // 관리자 결재함에서 견적 승인
    await demoLogin(page, "admin@demo.viralsync.example");
    await page.goto("/approvals?tab=mine&gate=QUOTE");
    const quoteCard = page.locator("article", { hasText: NAME }).first();
    await expect(quoteCard.getByText("AI 1차 검토")).toBeVisible();
    await quoteCard.getByRole("button", { name: "승인" }).click();
    await expect(page.getByText("최종 승인했습니다.")).toBeVisible();
    await logout(page);

    // 계약 전환 (141만원 < 150만원 계약 결재 기준 → 즉시 전환)
    await demoLogin(page, "manager@demo.viralsync.example");
    await page.goto(inquiryUrl);
    await page.waitForLoadState("networkidle");
    await page.getByRole("button", { name: "계약 전환 (캠페인 생성)" }).click();
    await expect(page).toHaveURL(/\/campaigns\/c.*converted=1/);
    await expect(page.getByText("문의가 계약 전환되었습니다")).toBeVisible();
    await page.waitForLoadState("networkidle");
    await expect(page.getByText(/매체별 집행 작업 \(0\/\d+ 완료\)/)).toBeVisible();

    // 첫 작업 완료 처리 (결과물 없으면 거부)
    const firstTask = page.locator("li", { has: page.locator('select[name="status"]') }).first();
    await firstTask.locator('select[name="status"]').selectOption("DONE");
    await firstTask.getByRole("button", { name: "저장" }).click();
    await expect(page.getByText("완료 처리하려면 결과물 URL 또는 작업 내용을 기록하세요.")).toBeVisible();
    await firstTask.getByPlaceholder(/결과물 URL/).fill("https://blog-demo.example/post/1");
    await firstTask.getByRole("button", { name: "저장" }).click();
    await expect(page.getByText("작업 상태를 저장했습니다.")).toBeVisible();
    await expect(page.getByText(/매체별 집행 작업 \(1\/\d+ 완료\)/)).toBeVisible();

    // 문의함 상태
    await page.goto("/inquiries?status=WON");
    await expect(page.getByRole("link", { name: NAME })).toBeVisible();
    await page.goto("/fulfillment?status=DONE");
    await expect(page.getByText(BRAND).first()).toBeVisible();
  });

  test("읽기 전용 사용자는 문의함에 접근할 수 없음", async ({ page }) => {
    await demoLogin(page, "viewer@demo.viralsync.example");
    await expect(page.getByRole("link", { name: /문의 접수함/ })).toHaveCount(0);
    await page.goto("/inquiries");
    await expect(page.getByText("접근 권한 없음")).toBeVisible();
  });
});

test.describe.serial("스레드 바로 올리기", () => {
  // 실제 1x1 PNG
  const PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

  test("스크린샷 붙여넣기(Ctrl+V) → 미리보기 → 모의 게시 → 기록·이미지 확인", async ({ page }) => {
    await demoLogin(page, "manager@demo.viralsync.example");
    await page.getByRole("link", { name: /스레드 바로 올리기/ }).click();
    await expect(page.getByRole("heading", { name: "스레드 바로 올리기" })).toBeVisible();
    await page.waitForLoadState("networkidle");

    // 계정·공개 주소가 없으므로 실제 게시는 막혀 있어야 함
    await expect(page.getByText("모의 게시만 가능")).toBeVisible();
    await expect(page.getByText("Threads 계정이 연결되지 않았습니다.").first()).toBeVisible();

    // 클립보드 이미지 붙여넣기
    await page.evaluate((b64) => {
      const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
      const dt = new DataTransfer();
      dt.items.add(new File([bytes], "", { type: "image/png" }));
      window.dispatchEvent(new ClipboardEvent("paste", { clipboardData: dt, bubbles: true, cancelable: true }));
    }, PNG_B64);
    await expect(page.getByAltText("게시할 이미지 미리보기")).toBeVisible();
    await expect(page.getByRole("button", { name: /스레드에 바로 게시/ })).toBeDisabled();

    await page.getByLabel("문구 (선택)").fill(`E2E 스레드 테스트 ${Date.now()}`);
    await page.getByLabel(/광고·협찬/).check();
    await expect(page.getByText("실제 게시 문구 끝에")).toBeVisible();
    await page.getByRole("button", { name: "모의 게시 (테스트)" }).click();
    await expect(page.getByText("[모의] 게시 완료")).toBeVisible();
    await expect(page.getByAltText("게시할 이미지 미리보기")).toHaveCount(0); // 성공 후 초기화

    const card = page.locator("li", { hasText: "E2E 스레드 테스트" }).first();
    await expect(card.getByText("모의")).toBeVisible();
    await expect(card.getByText("#광고")).toBeVisible();
    const ok = await card.locator("img").evaluate((img: HTMLImageElement) => img.complete && img.naturalWidth > 0);
    expect(ok).toBe(true); // /media 공개 경로에서 실제로 이미지가 열림
  });

  test("파일 선택 업로드와 형식 오류 안내", async ({ page }) => {
    await demoLogin(page, "manager@demo.viralsync.example");
    await page.goto("/threads");
    await page.waitForLoadState("networkidle");
    await page.locator("#th-image").setInputFiles({ name: "a.gif", mimeType: "image/gif", buffer: Buffer.from("GIF89a") });
    await expect(page.getByText("JPG 또는 PNG 이미지만 올릴 수 있습니다.")).toBeVisible();
    await page.locator("#th-image").setInputFiles({ name: "shot.png", mimeType: "image/png", buffer: Buffer.from(PNG_B64, "base64") });
    await expect(page.getByAltText("게시할 이미지 미리보기")).toBeVisible();
    await page.getByRole("button", { name: "모의 게시 (테스트)" }).click();
    await expect(page.getByText("[모의] 게시 완료")).toBeVisible();
  });

  test("미로그인 사용자도 /media 이미지는 열 수 있지만(Threads 수집용) 잘못된 이름은 404", async ({ request }) => {
    // 클라이언트가 정규화하는 경로 탈출 시도: 파일 내용이 노출되면 안 됨
    expect(await (await request.get("/media/../../etc/passwd")).text()).not.toContain("root:");
    // 인코딩된 경로 탈출 시도는 /media 라우트의 파일명 검사에서 404
    const enc = await request.get("/media/..%2F..%2Fetc%2Fpasswd");
    expect(enc.status()).toBe(404);
    expect(await enc.text()).not.toContain("root:");
    expect((await request.get("/media/abc.png")).status()).toBe(404);
  });
});

test.describe.serial("AI 홍보 회사", () => {
  test("비서 5줄 보고 → 조직도·직원 지시서 → 캠페인에서 AI 팀에 맡기기 → 결재 요청서", async ({ page }) => {
    await demoLogin(page, "manager@demo.viralsync.example");
    await expect(page.getByText("한결 비서실장의 보고")).toBeVisible();
    await expect(page.getByLabel("비서 보고").getByText("한 일")).toBeVisible();

    await page.goto("/organization");
    await expect(page.getByRole("heading", { name: "AI 회사 조직도" })).toBeVisible();
    await expect(page.getByText("⛔ 금지선")).toBeVisible();
    await page.getByRole("link", { name: /컷 숏폼 PD/ }).click();
    await expect(page).toHaveURL(/\/organization\/staff\/shortform/);
    await expect(page.getByRole("heading", { name: /컷 — 숏폼 PD/ })).toBeVisible();
    await expect(page.getByText("광고홍보AI_회사/01_직원/04_숏폼PD_컷.md")).toBeVisible();

    await page.goto("/campaigns");
    await page.getByRole("link", { name: /하늘커피 브이로그 협업/ }).first().click();
    await page.waitForLoadState("networkidle");
    await expect(page.getByText("AI 팀 진행판")).toBeVisible();
    const form = page.getByRole("form", { name: "AI 팀에 맡기기" });
    for (const box of await form.getByRole("checkbox").all()) await box.uncheck();
    await form.getByRole("button", { name: "AI 팀에 맡기기" }).click();
    await expect(page.getByText("홍보할 매체를 하나 이상 고르세요.")).toBeVisible();
    await form.getByLabel(/틱톡/).check();
    await form.getByRole("button", { name: "AI 팀에 맡기기" }).click();
    await expect(page.getByText(/AI 팀이 작업했습니다: 틱톡 — 초안 2건, 결재 요청 2건/)).toBeVisible();
    await expect(page.getByRole("table", { name: "매체별 결과" }).getByText("틱톡")).toBeVisible();
    await logout(page);

    await demoLogin(page, "admin@demo.viralsync.example");
    await page.goto("/approvals?tab=pending&gate=CONTENT");
    const card = page.locator("article", { hasText: "숏폼 영상 대본" }).first();
    await expect(card.getByText("결재 요청서")).toBeVisible();
    await expect(card.getByText("되돌리는 법")).toBeVisible();
    await logout(page);
  });
});
