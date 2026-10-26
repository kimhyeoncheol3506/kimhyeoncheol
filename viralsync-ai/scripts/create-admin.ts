/* eslint-disable no-console */
/**
 * 실제 운영용 조직과 첫 관리자(캡틴) 계정을 만든다. 데모 데이터는 만들지 않는다.
 *   npm run admin:create
 * 대상 DB 는 DATABASE_URL (배포용 Neon 주소를 넣고 실행). 비밀번호는 화면에만 입력하고 어디에도 저장하지 않는다.
 */
import { createInterface } from "node:readline/promises";
import bcrypt from "bcryptjs";
import { PrismaClient } from "@prisma/client";
import { PACKAGES, PLATFORMS } from "../prisma/base-data";
import { DEFAULT_RULES } from "../src/lib/services/approvals";
import { DEFAULT_POSITIONING, DEFAULT_TARGET_INDUSTRY } from "../src/lib/business/playbook";

async function main() {
  const rl = createInterface({ input: process.stdin });
  const lines = rl[Symbol.asyncIterator]();
  const ask = async (q: string) => {
    process.stdout.write(q);
    const r = await lines.next();
    return r.done ? "" : String(r.value);
  };
  const host = (process.env.DATABASE_URL ?? "").replace(/\/\/[^@]*@/, "//***@").split("?")[0];
  console.log(`대상 DB: ${host || "(DATABASE_URL 없음)"}`);
  const orgName = (await ask("회사 이름: ")).trim();
  const name = (await ask("관리자 이름: ")).trim();
  const email = (await ask("관리자 이메일: ")).trim().toLowerCase();
  const password = await ask("비밀번호 (10자 이상): ");
  rl.close();
  if (!orgName || !name || !/^\S+@\S+\.\S+$/.test(email)) throw new Error("회사 이름·관리자 이름·이메일을 확인하세요.");
  if (password.length < 10) throw new Error("비밀번호는 10자 이상으로 정하세요.");

  const prisma = new PrismaClient();
  try {
    if (await prisma.user.findUnique({ where: { email } })) throw new Error("이미 있는 이메일입니다.");
    for (const p of PLATFORMS) await prisma.socialPlatform.upsert({ where: { key: p.key }, create: p, update: {} });
    const org = await prisma.organization.create({ data: { name: orgName, positioning: DEFAULT_POSITIONING, targetIndustry: DEFAULT_TARGET_INDUSTRY, businessStartDate: new Date() } });
    await prisma.user.create({ data: { organizationId: org.id, name, email, role: "ADMIN", passwordHash: await bcrypt.hash(password, 10) } });
    await prisma.approvalRule.createMany({ data: DEFAULT_RULES.map((r) => ({ ...r, organizationId: org.id, active: true })) });
    // 샘플 가격표 — ‘서비스 상품’ 화면에서 실제 가격으로 고치세요
    await prisma.servicePackage.createMany({ data: PACKAGES.map((p) => ({ ...p, organizationId: org.id })) });
    console.log(`완료: ‘${orgName}’ 조직과 관리자 ${email} 를 만들었습니다. 기본 결재 규칙 ${DEFAULT_RULES.length}개, 샘플 가격표 ${PACKAGES.length}개 포함.`);
  } finally {
    await prisma.$disconnect();
  }
}

main().catch((e) => {
  console.error(`실패: ${e instanceof Error ? e.message : e}`);
  process.exit(1);
});
