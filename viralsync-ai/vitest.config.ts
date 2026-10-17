import { defineConfig } from "vitest/config";
import tsconfigPaths from "vite-tsconfig-paths";

// 통합 테스트는 개발 DB 와 분리된 테스트 DB 를 사용합니다.
const TEST_DB = process.env.TEST_DATABASE_URL ?? "postgresql://postgres:postgres@localhost:5432/viralsync_test?schema=public";

export default defineConfig({
  plugins: [tsconfigPaths()],
  test: {
    environment: "node",
    include: ["tests/unit/**/*.test.ts", "tests/integration/**/*.test.ts"],
    setupFiles: ["tests/setup.ts"],
    globalSetup: ["tests/global-setup.ts"],
    env: { DATABASE_URL: TEST_DB, SESSION_SECRET: "test-secret-0123456789abcdef0123456789abcdef", AI_PROVIDER: "demo" },
    fileParallelism: false,
    testTimeout: 30000,
    hookTimeout: 60000,
  },
});
