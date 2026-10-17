"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { updateTaskAction } from "@/app/actions/tasks";
import { TASK_STATUS_LABEL } from "@/lib/labels";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export function TaskForm({
  task,
  staff,
}: {
  task: { id: string; status: string; deliverableUrl: string | null; note: string; assigneeId: string | null };
  staff: { id: string; name: string }[];
}) {
  const { state, pending, onSubmit, formRef } = useActionForm(updateTaskAction);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="grid gap-2 sm:grid-cols-[8rem_9rem_1fr_1fr_auto]" noValidate>
      <input type="hidden" name="id" value={task.id} />
      <label className="sr-only" htmlFor={`ts-${task.id}`}>상태</label>
      <select id={`ts-${task.id}`} name="status" defaultValue={task.status} className="input py-1.5 text-sm">
        {Object.entries(TASK_STATUS_LABEL).map(([k, v]) => (
          <option key={k} value={k}>{v}</option>
        ))}
      </select>
      <label className="sr-only" htmlFor={`ta-${task.id}`}>담당자</label>
      <select id={`ta-${task.id}`} name="assigneeId" defaultValue={task.assigneeId ?? ""} className="input py-1.5 text-sm">
        <option value="">담당 미지정</option>
        {staff.map((s) => (
          <option key={s.id} value={s.id}>{s.name}</option>
        ))}
      </select>
      <label className="sr-only" htmlFor={`tu-${task.id}`}>결과물 URL</label>
      <input id={`tu-${task.id}`} name="deliverableUrl" type="url" defaultValue={task.deliverableUrl ?? ""} placeholder="결과물 URL (게시글·광고 보고서 등)" className="input py-1.5 text-sm" />
      <label className="sr-only" htmlFor={`tn-${task.id}`}>작업 메모</label>
      <input id={`tn-${task.id}`} name="note" defaultValue={task.note} placeholder="작업 메모" className="input py-1.5 text-sm" />
      <SubmitButton pending={pending} size="sm" pendingText="…">저장</SubmitButton>
      <div className="sm:col-span-5"><FormMessage state={state} /></div>
    </form>
  );
}
