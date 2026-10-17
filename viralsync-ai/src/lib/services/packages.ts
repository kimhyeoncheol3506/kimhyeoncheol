import { prisma } from "@/lib/db";
import { assertCan, NotFoundError, type Ctx } from "@/lib/auth/context";
import type { CatalogItem } from "@/lib/inquiry/planner";
import type { PackageInput } from "@/lib/validation/schemas";
import { audit } from "./audit";

export async function listPackages(ctx: Ctx, includeInactive = true) {
  return prisma.servicePackage.findMany({
    where: { organizationId: ctx.organizationId, ...(includeInactive ? {} : { active: true }) },
    orderBy: [{ active: "desc" }, { channel: "asc" }, { unitPrice: "asc" }],
  });
}

export async function catalogOf(organizationId: string): Promise<CatalogItem[]> {
  return prisma.servicePackage.findMany({
    where: { organizationId, active: true },
    select: { id: true, name: true, channel: true, unitPrice: true, unit: true, mediaSpendSeparate: true, active: true },
  });
}

export async function createPackage(ctx: Ctx, input: PackageInput) {
  assertCan(ctx, "service:manage");
  const exists = await prisma.servicePackage.findFirst({ where: { organizationId: ctx.organizationId, name: input.name } });
  if (exists) throw new Error("같은 이름의 상품이 이미 있습니다.");
  const p = await prisma.servicePackage.create({ data: { ...input, organizationId: ctx.organizationId } });
  await audit(ctx, "package.create", "ServicePackage", p.id, `서비스 상품 '${p.name}' 등록 (${p.unitPrice.toLocaleString()}원/${p.unit})`);
  return p;
}

export async function updatePackage(ctx: Ctx, id: string, input: PackageInput & { active: boolean }) {
  assertCan(ctx, "service:manage");
  const before = await prisma.servicePackage.findFirst({ where: { id, organizationId: ctx.organizationId } });
  if (!before) throw new NotFoundError();
  const dup = await prisma.servicePackage.findFirst({ where: { organizationId: ctx.organizationId, name: input.name, NOT: { id } } });
  if (dup) throw new Error("같은 이름의 상품이 이미 있습니다.");
  const p = await prisma.servicePackage.update({ where: { id }, data: input });
  await audit(ctx, "package.update", "ServicePackage", id, `서비스 상품 '${p.name}' 수정 (${before.unitPrice.toLocaleString()}원 → ${p.unitPrice.toLocaleString()}원${p.active ? "" : ", 판매 중지"})`);
  return p;
}
