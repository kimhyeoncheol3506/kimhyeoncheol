"use client";
import { useState } from "react";
import { useStore } from "@/lib/store";
import { newId, nowStamp, today } from "@/lib/format";
import type { Priority } from "@/lib/types";

// AI 직원에게 미션을 주는 입력 폼. fixedStaffId를 주면 직원 선택 칸이 숨겨집니다.
export function MissionForm({ fixedStaffId }: { fixedStaffId?: string }) {
  const { data, add } = useStore();
  const [staffId, setStaffId] = useState(fixedStaffId ?? data.staff[0]?.id ?? "");
  const [title, setTitle] = useState("");
  const [detail, setDetail] = useState("");
  const [priority, setPriority] = useState<Priority>("normal");
  const [dueDate, setDueDate] = useState(today());

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    add("missions", {
      id: newId("m"),
      staffId: fixedStaffId ?? staffId,
      title: title.trim(),
      detail: detail.trim(),
      priority,
      status: "todo",
      dueDate,
      createdAt: nowStamp(),
      feedback: "",
    });
    setTitle("");
    setDetail("");
  };

  return (
    <form onSubmit={submit} className="grid gap-3 sm:grid-cols-6">
      {!fixedStaffId && (
        <div className="sm:col-span-2">
          <label className="label">담당 AI 직원</label>
          <select className="input" value={staffId} onChange={(e) => setStaffId(e.target.value)}>
            {data.staff.map((s) => (
              <option key={s.id} value={s.id}>
                {s.avatar} {s.name} · {s.role}
              </option>
            ))}
          </select>
        </div>
      )}
      <div className={fixedStaffId ? "sm:col-span-6" : "sm:col-span-4"}>
        <label className="label">미션 제목</label>
        <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="예: E식당 인스타 홍보 문구 5개" />
      </div>
      <div className="sm:col-span-6">
        <label className="label">상세 지시</label>
        <textarea className="input min-h-[72px]" value={detail} onChange={(e) => setDetail(e.target.value)} placeholder="분량, 톤, 참고 자료 등을 적어 주세요." />
      </div>
      <div className="sm:col-span-2">
        <label className="label">우선순위</label>
        <select className="input" value={priority} onChange={(e) => setPriority(e.target.value as Priority)}>
          <option value="low">낮음</option>
          <option value="normal">보통</option>
          <option value="high">긴급</option>
        </select>
      </div>
      <div className="sm:col-span-2">
        <label className="label">마감일</label>
        <input type="date" className="input" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
      </div>
      <div className="flex items-end sm:col-span-2">
        <button className="btn-primary w-full" disabled={!title.trim()}>
          ＋ 미션 부여
        </button>
      </div>
    </form>
  );
}
