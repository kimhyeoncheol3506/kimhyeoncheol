import { defineConfig } from "@playwright/test";

// E2E 는 별도 DB(viralsync_e2e)에 데모 데이터를 새로 만들고 별도 포트로 서버를 띄웁니다.
const PORT = Number(process.env.E2E_PORT ?? 3200);
export const E2E_DB = process.env.E2E_DATABASE_URL ?? "postgresql://postgres:postgres@localhost:5432/viralsync_e2e?schema=public";

export default defineConfig({
  testDir: "tests/e2e",
  timeout: 90_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  reporter: [["list"]],
  globalSetup: "./tests/e2e/global-setup.ts",
  use: {
    baseURL: `http://localhost:${PORT}`,
    launchOptions: { executablePath: process.env.PW_CHROMIUM_PATH || undefined },
    trace: "retain-on-failure",
    locale: "ko-KR",
  },
  webServer: {
    command: `npx next start -p ${PORT}`,
    port: PORT,
    reuseExistingServer: false,
    timeout: 120_000,
    env: { DATABASE_URL: E2E_DB, DEMO_MODE: "true", AI_PROVIDER: "demo", SESSION_SECRET: "e2e-secret-0123456789abcdef0123456789abcdef" },
  },
});
