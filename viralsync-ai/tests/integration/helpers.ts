import bcrypt from "bcryptjs";
import type { Role } from "@prisma/client";
import { prisma } from "@/lib/db";
import type { Ctx } from "@/lib/auth/context";
import { loadCtx } from "@/lib/auth/load-ctx";

const PLATFORMS = [
  { key: "THREADS", name: "Threads", policyUrl: "https://developers.facebook.com/docs/threads", maxTextLength: 500, dailyLimit: 250 },
  { key: "INSTAGRAM", name: "Instagram", policyUrl: "https://help.instagram.com", maxTextLength: 2200, dailyLimit: 20 },
  { key: "TIKTOK", name: "TikTok", policyUrl: "https://www.tiktok.com/community-guidelines", maxTextLength: 2200, dailyLimit: 10 },
  { key: "X", name: "X", policyUrl: "https://help.x.com", maxTextLength: 280, dailyLimit: 30 },
  { key: "FACEBOOK", name: "Facebook", policyUrl: "https://transparency.meta.com", maxTextLength: 5000, dailyLimit: 20 },
  { key: "YOUTUBE", name: "YouTube", policyUrl: "https://support.google.com/youtube", maxTextLength: 5000, dailyLimit: 10 },
  { key: "BLOG", name: "블로그", policyUrl: "https://www.ftc.go.kr", maxTextLength: 20000, dailyLimit: 10 },
] as const;

export async function ensurePlatforms() {
  for (const p of PLATFORMS) await prisma.socialPlatform.upsert({ where: { key: p.key }, create: p, update: {} });
}

let seq = 0;
export async function makeOrg(label: string) {
  await ensurePlatforms();
  const tag = `${label}-${Date.now()}-${seq++}`;
  const org = await prisma.organization.create({ data: { name: `test ${tag}` } });
  const hash = await bcrypt.hash("pw", 4);
  const mk = async (role: Role) => {
    const u = await prisma.user.create({ data: { organizationId: org.id, email: `${role.toLowerCase()}-${tag}@test.example`, name: `${role} ${tag}`, role, passwordHash: hash } });
    return u;
  };
  const users = {
    admin: await mk("ADMIN"),
    manager: await mk("CAMPAIGN_MANAGER"),
    writer: await mk("CONTENT_WRITER"),
    reviewer: await mk("REVIEWER"),
    viewer: await mk("VIEWER"),
  };
  await prisma.servicePackage.createMany({
    data: [
      { organizationId: org.id, name: "블로그", channel: "BLOG", unitPrice: 200000, unit: "월" },
      { organizationId: org.id, name: "플레이스", channel: "NAVER_PLACE", unitPrice: 150000, unit: "월" },
      { organizationId: org.id, name: "체험단", channel: "EXPERIENCE_GROUP", unitPrice: 300000, unit: "회", leadTimeDays: 14 },
      { organizationId: org.id, name: "인스타", channel: "INSTAGRAM", unitPrice: 300000, unit: "월" },
      { organizationId: org.id, name: "메타광고", channel: "META_AD", unitPrice: 200000, unit: "월", mediaSpendSeparate: true },
    ],
  });
  return { org, users };
}

export async function ctxOf(userId: string): Promise<Ctx> {
  const c = await loadCtx(userId);
  if (!c) throw new Error("user not found");
  return c;
}

export async function grant(userIds: string[], clientId: string) {
  await prisma.clientAccess.createMany({ data: userIds.map((userId) => ({ userId, clientId })), skipDuplicates: true });
}
