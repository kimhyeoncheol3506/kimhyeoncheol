"use client";
import Link from "next/link";
import { useState } from "react";
import { useStore } from "@/lib/store";
import { PageHeader } from "@/components/PageHeader";
import { Badge } from "@/components/Badge";
import { staffStatus } from "@/lib/labels";
import type { StaffStatus } from "@/lib/types";

// 직원 목록 및 상태 관리
export default function StaffDirectory() {
  const { data, update } = useStore();
  const [filter, setFilter] = useState<StaffStatus | "all">("all");
  const [q, setQ] = useState("");

  const list = data.staff.filter(
    (s) =>
      (filter === "all" || s.status === filter) &&
      (s.name + s.role + s.department).toLowerCase().includes(q.toLowerCase()),
  );
  const openMissions = (id: string) => data.missions.filter((m) => m.staffId === id && m.status !== "done").length;

  return (
    <>
      <PageHeader title="직원 목록 · 상태" desc="AI 직원의 현재 상태를 보고 바로 바꿀 수 있어요. 카드를 누르면 이력서가 열립니다." />

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <input className="input max-w-xs" placeholder="이름·역할 검색" value={q} onChange={(e) => setQ(e.target.value)} />
        <div className="flex flex-wrap gap-1">
          <FilterChip active={filter === "all"} onClick={() => setFilter("all")}>
            전체 {data.staff.length}
          </FilterChip>
          {(Object.keys(staffStatus) as StaffStatus[]).map((k) => (
            <FilterChip key={k} active={filter === k} onClick={() => setFilter(k)}>
              {staffStatus[k].text} {data.staff.filter((s) => s.status === k).length}
            </FilterChip>
          ))}
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {list.map((s) => (
          <div key={s.id} className="card flex flex-col">
            <Link href={`/staff/${s.id}`} className="flex items-start gap-3">
              <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-brand-soft text-2xl">{s.avatar}</span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-semibold">{s.name}</p>
                  <Badge label={staffStatus[s.status]} />
                </div>
                <p className="text-xs text-sub">
                  {s.role} · {s.department}
                </p>
                <p className="mt-2 line-clamp-2 text-sm text-sub">{s.summary}</p>
              </div>
            </Link>
            <div className="mt-4 flex items-center justify-between gap-2 border-t border-line pt-3">
              <span className="text-xs text-mute">진행 미션 {openMissions(s.id)}건</span>
              <select
                className="input w-auto py-1 text-xs"
                value={s.status}
                onChange={(e) => update("staff", s.id, { status: e.target.value as StaffStatus })}
              >
                {(Object.keys(staffStatus) as StaffStatus[]).map((k) => (
                  <option key={k} value={k}>
                    {staffStatus[k].text}
                  </option>
                ))}
              </select>
            </div>
          </div>
        ))}
        {list.length === 0 && <p className="col-span-full py-10 text-center text-sm text-mute">조건에 맞는 직원이 없어요.</p>}
      </div>
    </>
  );
}

function FilterChip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full px-3 py-1 text-xs font-medium ${active ? "bg-brand text-white" : "bg-white text-sub ring-1 ring-line hover:bg-canvas"}`}
    >
      {children}
    </button>
  );
}
