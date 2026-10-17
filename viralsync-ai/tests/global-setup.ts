import { execSync } from "node:child_process";

/** 테스트 DB 스키마를 동기화 (비파괴적 db push). 테스트 데이터는 각 테스트가 고유 조직으로 생성합니다. */
export default function setup() {
  const url = process.env.TEST_DATABASE_URL ?? "postgresql://postgres:postgres@localhost:5432/viralsync_test?schema=public";
  if (process.env.SKIP_DB_SETUP === "true") return;
  try {
    execSync("npx prisma db push --skip-generate", { env: { ...process.env, DATABASE_URL: url }, stdio: "pipe" });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    console.warn(`[global-setup] 테스트 DB 준비 실패 — 통합 테스트가 실패할 수 있습니다.\n${msg.slice(0, 500)}`);
  }
}
