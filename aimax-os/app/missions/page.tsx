"use client";
import Link from "next/link";
import { useStore } from "@/lib/store";
import { PageHeader } from "@/components/PageHeader";
import { Badge } from "@/components/Badge";
import { MissionForm } from "@/components/MissionForm";
import { missionStatus, priority } from "@/lib/labels";
import type { MissionStatus } from "@/lib/types";

const COLUMNS: MissionStatus[] = ["todo", "doing", "review", "done"];

// 미션 보드: AI 직원별 미션을 부여하고 단계별로 옮깁니다.
export default function Missions() {
  const { data, update, remove } = useStore();
  const staff = (id: string) => data.staff.find((s) => s.id === id);

  return (
    <>
      <PageHeader title="미션 보드" desc="AI 직원에게 미션을 주고, 대기 → 진행 → 검수 → 완료로 관리합니다." />

      <section className="card mb-6">
        <h2 className="mb-3 font-semibold">새 미션 부여</h2>
        <MissionForm />
      </section>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {COLUMNS.map((col) => {
          const items = data.missions.filter((m) => m.status === col);
          return (
            <div key={col} className="rounded-card bg-white/60 p-3 ring-1 ring-line">
              <div className="mb-3 flex items-center justify-between px-1">
                <Badge label={missionStatus[col]} />
                <span className="text-xs text-mute">{items.length}건</span>
              </div>
              <div className="space-y-2">
                {items.map((m) => {
                  const s = staff(m.staffId);
                  return (
                    <div key={m.id} className="rounded-xl border border-line bg-white p-3 text-sm">
                      <div className="flex items-start justify-between gap-2">
                        <p className="font-medium">{m.title}</p>
                        <Badge label={priority[m.priority]} />
                      </div>
                      {m.detail && <p className="mt-1 text-xs text-sub">{m.detail}</p>}
                      <p className="mt-2 text-xs text-mute">
                        {s ? (
                          <Link href={`/staff/${s.id}`} className="hover:text-brand">
                            {s.avatar} {s.name}
                          </Link>
                        ) : (
                          "담당자 없음"
                        )}{" "}
                        · 마감 {m.dueDate}
                      </p>
                      {(m.status === "review" || m.feedback) && (
                        <textarea
                          className="input mt-2 min-h-[56px] text-xs"
                          placeholder="검수 의견을 남겨 주세요"
                          value={m.feedback}
                          onChange={(e) => update("missions", m.id, { feedback: e.target.value })}
                        />
                      )}
                      <div className="mt-2 flex items-center gap-1.5">
                        <select
                          className="input py-1 text-xs"
                          value={m.status}
                          onChange={(e) => update("missions", m.id, { status: e.target.value as MissionStatus })}
                        >
                          {COLUMNS.map((c) => (
                            <option key={c} value={c}>
                              {missionStatus[c].text}
                            </option>
                          ))}
                        </select>
                        <button
                          className="btn px-2 py-1 text-xs"
                          onClick={() => confirm(`'${m.title}' 미션을 삭제할까요?`) && remove("missions", m.id)}
                          aria-label="삭제"
                        >
                          🗑
                        </button>
                      </div>
                    </div>
                  );
                })}
                {items.length === 0 && <p className="py-6 text-center text-xs text-mute">비어 있음</p>}
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}
