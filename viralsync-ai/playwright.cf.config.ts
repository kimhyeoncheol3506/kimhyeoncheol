import { defineConfig } from "@playwright/test";
import base, { E2E_DB } from "./playwright.config";

// 같은 E2E 를 Cloudflare Workers 런타임(workerd, wrangler dev)에서 실행한다.
// 먼저 `npx opennextjs-cloudflare build` 로 .open-next 를 만들어 두어야 한다 (npm run test:e2e:cf 가 함께 실행).
const PORT = 3300;
const vars = {
  DATABASE_URL: E2E_DB,
  DEMO_MODE: "true",
  // Cloudflare 는 모든 요청에 cf-connecting-ip 를 붙여 ‘외부 접속’으로 판정되므로, 테스트에서만 데모 로그인 허용
  DEMO_ALLOW_REMOTE: "true",
  SESSION_SECRET: "e2e-secret-0123456789abcdef0123456789abcdef",
  TOKEN_ENCRYPTION_KEY: "e2e-token-key-0123456789abcdef0123456789",
};

export default defineConfig({
  ...base,
  use: { ...base.use, baseURL: `http://localhost:${PORT}` },
  webServer: {
    command: `npx wrangler dev --port ${PORT} --ip 127.0.0.1 ${Object.entries(vars).map(([k, v]) => `--var "${k}:${v}"`).join(" ")}`,
    port: PORT,
    reuseExistingServer: false,
    timeout: 180_000,
  },
});
