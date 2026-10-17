import type { ServiceChannel, TaskStatus } from "@prisma/client";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { listTasks, taskProgress } from "@/lib/services/tasks";
import { staffOptions } from "@/lib/services/reports";
import { CHANNEL_LABEL, SERVICE_CHANNELS } from "@/lib/inquiry/planner";
import { TASK_STATUS_LABEL } from "@/lib/labels";
import { str, type SP } from "@/lib/page";
import { Card, CardBody, PageHeader, StatCard } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/misc";
import { TasksTable } from "@/components/inquiry/tasks-table";

export const metadata = { title: "매체 집행 작업" };

export default async function FulfillmentPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  const sp = await searchParams;
  const sRaw = str(sp, "status");
  const status = sRaw && sRaw in TASK_STATUS_LABEL ? (sRaw as TaskStatus) : undefined;
  const cRaw = str(sp, "channel");
  const channel = cRaw && (SERVICE_CHANNELS as string[]).includes(cRaw) ? (cRaw as ServiceChannel) : undefined;
  const mine = str(sp, "mine") === "1";
  const [tasks, all, staff] = await Promise.all([listTasks(ctx, { status, channel, mine }), listTasks(ctx), staffOptions(ctx)]);
  const prog = taskProgress(all);
  const overdue = all.filter((t) => t.status !== "DONE" && t.dueDate && t.dueDate < new Date()).length;
  return (
    <>
      <PageHeader title="매체 집행 작업" description="계약된 캠페인의 매체별 실제 작업(포스팅·체험단·플레이스·광고 운영 등)을 담당자가 진행하고 결과물을 기록합니다." />
      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <StatCard label="전체 작업" value={prog.total} />
        <StatCard label="완료" value={`${prog.done} (${prog.pct}%)`} tone="good" />
        <StatCard label="진행 중" value={all.filter((t) => t.status === "IN_PROGRESS").length} />
        <StatCard label="마감 지남" value={overdue} tone={overdue ? "danger" : "default"} />
      </div>
      <form className="mb-4 flex flex-wrap gap-2">
        <select name="status" defaultValue={status ?? ""} className="input w-auto" aria-label="상태">
          <option value="">전체 상태</option>
          {Object.entries(TASK_STATUS_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <select name="channel" defaultValue={channel ?? ""} className="input w-auto" aria-label="매체">
          <option value="">전체 매체</option>
          {SERVICE_CHANNELS.map((c) => <option key={c} value={c}>{CHANNEL_LABEL[c]}</option>)}
        </select>
        <label className="flex items-center gap-1.5 text-sm"><input type="checkbox" name="mine" value="1" defaultChecked={mine} /> 내 작업만</label>
        <button className="rounded-lg border border-slate-300 bg-white px-3 text-sm">적용</button>
      </form>
      {tasks.length === 0 ? (
        <EmptyState title="집행 작업이 없습니다" description="문의를 계약 전환하면 매체별 작업이 자동으로 생성됩니다." />
      ) : (
        <Card>
          <CardBody>
            <TasksTable tasks={tasks} staff={staff} canEdit={can(ctx.role, "task:update")} showCost={can(ctx.role, "cost:read")} />
          </CardBody>
        </Card>
      )}
    </>
  );
}
