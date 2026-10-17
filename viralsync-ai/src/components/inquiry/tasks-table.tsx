import Link from "next/link";
import type { ServiceChannel, TaskStatus } from "@prisma/client";
import { CHANNEL_LABEL } from "@/lib/inquiry/planner";
import { dateOnly, won } from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import { TaskStatusBadge } from "@/components/ui/status";
import { TaskForm } from "@/components/forms/task-form";

export interface TaskRow {
  id: string;
  title: string;
  channel: ServiceChannel;
  status: TaskStatus;
  quantity: number;
  unitPrice: number;
  dueDate: Date | null;
  deliverableUrl: string | null;
  note: string;
  assigneeId: string | null;
  assignee: { name: string } | null;
  completedAt: Date | null;
  campaign?: { id: string; name: string; client: { name: string } };
}

export function TasksTable({ tasks, staff, canEdit, showCost }: { tasks: TaskRow[]; staff: { id: string; name: string }[]; canEdit: boolean; showCost: boolean }) {
  return (
    <ul className="divide-y divide-slate-100">
      {tasks.map((t) => {
        const overdue = t.status !== "DONE" && t.dueDate && t.dueDate < new Date();
        return (
          <li key={t.id} className="py-3">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="indigo">{CHANNEL_LABEL[t.channel]}</Badge>
              <span className="font-medium text-slate-800">{t.title}</span>
              <TaskStatusBadge status={t.status} />
              <span className={`text-xs ${overdue ? "font-semibold text-rose-600" : "text-slate-500"}`}>마감 {dateOnly(t.dueDate)}{overdue ? " (지남)" : ""}</span>
              {showCost && <span className="text-xs text-slate-400">{won(t.unitPrice * t.quantity)}</span>}
              {t.campaign && (
                <span className="text-xs text-slate-500">
                  · {t.campaign.client.name} / <Link className="link" href={`/campaigns/${t.campaign.id}`}>{t.campaign.name}</Link>
                </span>
              )}
            </div>
            {t.deliverableUrl && !canEdit && (
              <a href={t.deliverableUrl} target="_blank" rel="noreferrer noopener" className="link mt-1 block break-all text-xs">{t.deliverableUrl}</a>
            )}
            {canEdit ? (
              <div className="mt-2">
                <TaskForm task={t} staff={staff} />
              </div>
            ) : (
              t.note && <p className="mt-1 text-xs text-slate-600">{t.note}</p>
            )}
          </li>
        );
      })}
    </ul>
  );
}
