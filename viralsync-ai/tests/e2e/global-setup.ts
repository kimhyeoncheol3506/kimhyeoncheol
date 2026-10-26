import { execSync } from "node:child_process";
import { E2E_DB } from "../../playwright.config";

export default function globalSetup() {
  const env = { ...process.env, DATABASE_URL: E2E_DB, SEED_RESET: "true" };
  execSync("npx prisma db push --skip-generate --accept-data-loss", { env, stdio: "inherit" }); // E2E 전용 DB
  execSync("npx tsx prisma/seed.ts", { env, stdio: "inherit" });
}
