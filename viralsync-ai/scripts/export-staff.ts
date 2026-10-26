/**
 * AI 직원 명부(src/lib/company/staff.ts)로 Claude Code 회사 폴더의 직원 지시서를 만든다.
 *   npm run staff:export          → 광고홍보AI_회사/01_직원/*.md, .claude/agents/*.md 갱신
 *   npm run staff:export -- --check → 파일이 명부와 다르면 실패 (테스트·CI 용)
 */
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { staffFiles } from "../src/lib/company/staff-doc";

export const COMPANY_DIR = resolve(__dirname, "..", "광고홍보AI_회사");

export function staleFiles(root = COMPANY_DIR): string[] {
  const want = staffFiles();
  const stale = Object.entries(want).filter(([p, body]) => !existsSync(join(root, p)) || readFileSync(join(root, p), "utf8") !== body).map(([p]) => p);
  // 명부에서 빠진 직원의 옛 지시서
  for (const dir of ["01_직원", ".claude/agents", "05_매뉴얼"]) {
    const abs = join(root, dir);
    if (!existsSync(abs)) continue;
    for (const f of readdirSync(abs)) if (f.endsWith(".md") && !(`${dir}/${f}` in want)) stale.push(`${dir}/${f}`);
  }
  return stale;
}

function main() {
  const check = process.argv.includes("--check");
  const stale = staleFiles();
  if (check) {
    if (stale.length) {
      console.error(`직원 지시서가 명부와 다릅니다 → npm run staff:export\n${stale.join("\n")}`);
      process.exit(1);
    }
    console.log("직원 지시서가 명부와 일치합니다.");
    return;
  }
  const want = staffFiles();
  for (const p of stale) {
    const abs = join(COMPANY_DIR, p);
    if (p in want) {
      mkdirSync(dirname(abs), { recursive: true });
      writeFileSync(abs, want[p]);
    } else rmSync(abs);
  }
  console.log(stale.length ? `갱신 ${stale.length}개:\n${stale.join("\n")}` : "변경 없음");
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(__filename)) main();
