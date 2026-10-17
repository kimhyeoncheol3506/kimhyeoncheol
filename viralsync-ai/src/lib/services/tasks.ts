import type { Prisma, ServiceChannel, TaskStatus } from "@prisma/client";
import { prisma } from "@/lib/db";
import { assertCan, NotFoundError, type Ctx } from "@/lib/auth/context";
import { seesAllClients } from "@/lib/auth/permissions";
import type { TaskUpdateInput } from "@/lib/validation/schemas";
import { audit } from "./audit";

function taskWhere(ctx: Ctx): Prisma.FulfillmentTaskWhereInput {
  return {
    organizationId: ctx.organizationId,
    campaign: { deletedAt: null, ...(seesAllClients(ctx.role) ? {} : { clientId: { in: ctx.clientIds } }) },
  };
}

export async function listTasks(ctx: Ctx, f: { status?: TaskStatus; channel?: ServiceChannel; campaignId?: string; mine?: boolean } = {}) {
  assertCan(ctx, "campaign:read");
  return prisma.fulfillmentTask.findMany({
    where: {
      ...taskWhere(ctx),
      ...(f.status ? { status: f.status } : {}),
      ...(f.channel ? { channel: f.channel } : {}),
      ...(f.campaignId ? { campaignId: f.campaignId } : {}),
      ...(f.mine ? { assigneeId: ctx.userId } : {}),
    },
    orderBy: [{ status: "asc" }, { dueDate: { sort: "asc", nulls: "last" } }],
    include: {
      campaign: { select: { id: true, name: true, client: { select: { name: true } } } },
      assignee: { select: { id: true, name: true } },
    },
    take: 300,
  });
}

export async function updateTask(ctx: Ctx, id: string, input: TaskUpdateInput) {
  assertCan(ctx, "task:update");
  const t = await prisma.fulfillmentTask.findFirst({ where: { ...taskWhere(ctx), id } });
  if (!t) throw new NotFoundError();
  if (input.status === "DONE" && !input.deliverableUrl && !input.note.trim())
    throw new Error("완료 처리하려면 결과물 URL 또는 작업 내용을 기록하세요.");
  if (input.assigneeId) {
    const u = await prisma.user.findFirst({ where: { id: input.assigneeId, organizationId: ctx.organizationId } });
    if (!u) throw new NotFoundError("담당자를 찾을 수 없습니다.");
  }
  const updated = await prisma.fulfillmentTask.update({
    where: { id },
    data: {
      status: input.status,
      deliverableUrl: input.deliverableUrl ?? null,
      note: input.note,
      assigneeId: input.assigneeId,
      completedAt: input.status === "DONE" ? (t.completedAt ?? new Date()) : null,
    },
  });
  await audit(ctx, "task.update", "FulfillmentTask", id, `집행 작업 '${t.title}' ${t.status} → ${input.status}`);
  return updated;
}

export function taskProgress(tasks: { status: TaskStatus }[]) {
  const done = tasks.filter((t) => t.status === "DONE").length;
  return { done, total: tasks.length, pct: tasks.length ? Math.round((done / tasks.length) * 100) : 0 };
}
