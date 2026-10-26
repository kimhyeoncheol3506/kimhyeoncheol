import type { Prisma, ProspectStage } from "@prisma/client";
import { prisma } from "@/lib/db";
import { assertCan, NotFoundError, type Ctx } from "@/lib/auth/context";
import { audit } from "./audit";

/** 영업 사냥 리스트 (PART 7). DM 은 사람이 자기 계정에서 직접 보내고, 여기에는 기록만 남긴다. */

export const STAGE_ORDER: ProspectStage[] = ["LISTED", "DM_SENT", "REPLIED", "MEETING", "TRIAL", "WON", "LOST", "WAITLIST"];
export const DAILY_DM_GOAL = 10;
export const LIST_GOAL = 100;

export interface ProspectInput {
  name: string;
  industry: string;
  region: string;
  instagram?: string | null;
  followers?: number | null;
  lastPostAt?: Date | null;
  postsPerMonth?: number | null;
  quality?: number | null;
  ownerName?: string | null;
  diagnosis?: string;
  notes?: string;
}

function clean(i: ProspectInput) {
  const name = i.name.trim();
  if (!name) throw new Error("가게 이름을 입력하세요.");
  if (i.quality != null && (i.quality < 1 || i.quality > 5)) throw new Error("품질은 1~5 로 입력하세요.");
  return { ...i, name, industry: i.industry.trim(), region: i.region.trim(), instagram: i.instagram?.trim() || null, ownerName: i.ownerName?.trim() || null };
}

export async function listProspects(ctx: Ctx, f: { stage?: ProspectStage; q?: string } = {}) {
  assertCan(ctx, "sales:manage");
  const where: Prisma.ProspectWhereInput = {
    organizationId: ctx.organizationId,
    ...(f.stage ? { stage: f.stage } : {}),
    ...(f.q ? { OR: [{ name: { contains: f.q, mode: "insensitive" } }, { region: { contains: f.q } }, { industry: { contains: f.q } }, { instagram: { contains: f.q, mode: "insensitive" } }] } : {}),
  };
  return prisma.prospect.findMany({ where, orderBy: [{ updatedAt: "desc" }], take: 300 });
}

export async function getProspect(ctx: Ctx, id: string) {
  assertCan(ctx, "sales:manage");
  const p = await prisma.prospect.findFirst({ where: { organizationId: ctx.organizationId, id } });
  if (!p) throw new NotFoundError();
  return p;
}

export async function createProspect(ctx: Ctx, input: ProspectInput) {
  assertCan(ctx, "sales:manage");
  const p = await prisma.prospect.create({ data: { ...clean(input), organizationId: ctx.organizationId, createdById: ctx.userId } });
  await audit(ctx, "sales.prospect", "Prospect", p.id, `사냥 리스트 추가: ${p.name}`);
  return p;
}

export async function updateProspect(ctx: Ctx, id: string, input: ProspectInput) {
  await getProspect(ctx, id);
  return prisma.prospect.update({ where: { id }, data: clean(input) });
}

/**
 * 붙여넣기 일괄 등록. 한 줄에 한 가게: 가게이름, 업종, 지역, 인스타, 팔로워, 마지막 게시일(YYYY-MM-DD), 월 게시 수
 * 쉼표 또는 탭으로 구분 (스프레드시트에서 복사해 붙여넣기 가능). 같은 이름+인스타는 건너뛴다.
 */
export function parseProspectLines(text: string): { rows: ProspectInput[]; errors: string[] } {
  const rows: ProspectInput[] = [];
  const errors: string[] = [];
  text
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean)
    .forEach((line, i) => {
      const c = line.split(/\t|,/).map((x) => x.trim());
      if (/^(가게|이름|상호)/.test(c[0]) && i === 0) return; // 머리글
      if (!c[0]) return void errors.push(`${i + 1}번째 줄: 가게 이름이 없습니다.`);
      const num = (v?: string) => (v && /^\d[\d,]*$/.test(v) ? Number(v.replace(/,/g, "")) : null);
      const date = c[5] && /^\d{4}-\d{1,2}-\d{1,2}$/.test(c[5]) ? new Date(`${c[5]}T00:00:00+09:00`) : null;
      if (c[5] && !date) errors.push(`${i + 1}번째 줄: 마지막 게시일 ‘${c[5]}’ 형식은 YYYY-MM-DD 로 (비워 둠).`);
      rows.push({ name: c[0], industry: c[1] ?? "", region: c[2] ?? "", instagram: c[3] || null, followers: num(c[4]), lastPostAt: date, postsPerMonth: num(c[6]) });
    });
  return { rows, errors };
}

export async function importProspects(ctx: Ctx, text: string) {
  assertCan(ctx, "sales:manage");
  const { rows, errors } = parseProspectLines(text);
  if (rows.length === 0) throw new Error(errors[0] ?? "등록할 줄이 없습니다.");
  const existing = await prisma.prospect.findMany({ where: { organizationId: ctx.organizationId }, select: { name: true, instagram: true } });
  const seen = new Set(existing.map((e) => `${e.name}|${e.instagram ?? ""}`));
  const fresh = rows.filter((r) => {
    const k = `${r.name}|${r.instagram ?? ""}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
  if (fresh.length) await prisma.prospect.createMany({ data: fresh.map((r) => ({ ...clean(r), organizationId: ctx.organizationId, createdById: ctx.userId })) });
  await audit(ctx, "sales.import", "Prospect", null, `사냥 리스트 ${fresh.length}곳 일괄 등록 (중복 ${rows.length - fresh.length})`);
  return { created: fresh.length, skipped: rows.length - fresh.length, errors };
}

/** 단계 변경 — DM 보냄·답장·만남 시각을 함께 기록 */
export async function setStage(ctx: Ctx, id: string, stage: ProspectStage) {
  const p = await getProspect(ctx, id);
  const now = new Date();
  const data: Prisma.ProspectUpdateInput = { stage };
  if (stage === "DM_SENT" && !p.dmSentAt) data.dmSentAt = now;
  if (stage === "REPLIED" && !p.repliedAt) data.repliedAt = now;
  if (stage === "MEETING" && !p.meetingAt) data.meetingAt = now;
  const u = await prisma.prospect.update({ where: { id }, data });
  await audit(ctx, stage === "DM_SENT" ? "sales.dm" : "sales.stage", "Prospect", id, `${p.name}: ${stage}`);
  return u;
}

function startOfDay(d = new Date()) {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  return x;
}

/** 퍼널·오늘 DM 수·이번 달 대기 고객 */
export async function salesStats(ctx: Ctx) {
  assertCan(ctx, "sales:manage");
  const [byStage, dmToday, dmTotal, monthStart] = await Promise.all([
    prisma.prospect.groupBy({ by: ["stage"], where: { organizationId: ctx.organizationId }, _count: { _all: true } }),
    prisma.prospect.count({ where: { organizationId: ctx.organizationId, dmSentAt: { gte: startOfDay() } } }),
    prisma.prospect.count({ where: { organizationId: ctx.organizationId, dmSentAt: { not: null } } }),
    Promise.resolve(new Date(new Date().getFullYear(), new Date().getMonth(), 1)),
  ]);
  const count = Object.fromEntries(STAGE_ORDER.map((s) => [s, byStage.find((b) => b.stage === s)?._count._all ?? 0])) as Record<ProspectStage, number>;
  const total = STAGE_ORDER.reduce((a, s) => a + count[s], 0);
  const replied = count.REPLIED + count.MEETING + count.TRIAL + count.WON;
  const waitlistThisMonth = await prisma.prospect.count({ where: { organizationId: ctx.organizationId, stage: "WAITLIST", updatedAt: { gte: monthStart } } });
  return { count, total, dmToday, dmTotal, replied, met: count.MEETING + count.TRIAL + count.WON, won: count.WON, waitlistThisMonth };
}

/** 고객 전환: 가게 → 고객(본인 계정 운영대행) 등록, 리스트는 TRIAL 로 */
export async function convertProspect(ctx: Ctx, id: string) {
  assertCan(ctx, "client:write");
  const p = await getProspect(ctx, id);
  if (p.clientId) return { clientId: p.clientId, created: false };
  const client = await prisma.$transaction(async (tx) => {
    const c = await tx.client.create({
      data: {
        organizationId: ctx.organizationId,
        name: p.name,
        contactName: p.ownerName ?? "사장님",
        industry: p.industry,
        promoUrl: p.instagram?.startsWith("http") ? p.instagram : p.instagram ? `https://www.instagram.com/${p.instagram.replace(/^@/, "")}` : null,
        ownAccount: true,
        managerId: ctx.userId,
      },
    });
    if (ctx.role !== "ADMIN") await tx.clientAccess.create({ data: { userId: ctx.userId, clientId: c.id } });
    await tx.prospect.update({ where: { id }, data: { clientId: c.id, stage: p.stage === "WON" ? "WON" : "TRIAL" } });
    return c;
  });
  await audit(ctx, "sales.convert", "Prospect", id, `${p.name} → 고객 등록 (본인 계정 운영대행)`);
  return { clientId: client.id, created: true };
}
