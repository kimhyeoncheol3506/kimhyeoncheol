"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useStore } from "@/lib/store";
import { Badge } from "@/components/Badge";
import { MissionForm } from "@/components/MissionForm";
import { Toggle } from "@/components/Toggle";
import { allPermissions, missionStatus, permission, priority, staffStatus } from "@/lib/labels";
import type { StaffStatus } from "@/lib/types";

// 개별 이력서 및 상세 프로필
export default function StaffResume() {
  const { id } = useParams<{ id: string }>();
  const { data, update } = useStore();
  const s = data.staff.find((x) => x.id === id);

  if (!s) {
    return (
      <div className="card text-center">
        <p>직원을 찾을 수 없어요.</p>
        <Link href="/staff" className="btn mt-4">
          ← 직원 목록
        </Link>
      </div>
    );
  }

  const missions = data.missions.filter((m) => m.staffId === s.id);
  const togglePerm = (p: (typeof allPermissions)[number]) =>
    update("staff", s.id, {
      permissions: s.permissions.includes(p) ? s.permissions.filter((x) => x !== p) : [...s.permissions, p],
    });

  return (
    <>
      <Link href="/staff" className="text-sm text-sub hover:text-brand">
        ← 직원 목록
      </Link>

      {/* 프로필 머리 */}
      <div className="card mt-3 flex flex-wrap items-center gap-4">
        <span className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-soft text-4xl">{s.avatar}</span>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold">{s.name}</h1>
            <Badge label={staffStatus[s.status]} />
          </div>
          <p className="text-sm text-sub">
            {s.role} · {s.department} · 입사 {s.joinedAt}
          </p>
          <p className="mt-1 text-sm">{s.summary}</p>
        </div>
        <div>
          <label className="label">상태 변경</label>
          <select className="input" value={s.status} onChange={(e) => update("staff", s.id, { status: e.target.value as StaffStatus })}>
            {(Object.keys(staffStatus) as StaffStatus[]).map((k) => (
              <option key={k} value={k}>
                {staffStatus[k].text}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        {/* 이력서 */}
        <section className="card lg:col-span-2">
          <h2 className="font-semibold">📄 이력서</h2>
          <dl className="mt-3 space-y-4 text-sm">
            <div>
              <dt className="label">주요 경력</dt>
              <dd>
                <ul className="list-disc space-y-1 pl-5">
                  {s.resume.career.map((c) => (
                    <li key={c}>{c}</li>
                  ))}
                </ul>
              </dd>
            </div>
            <div>
              <dt className="label">보유 스킬</dt>
              <dd className="flex flex-wrap gap-1.5">
                {s.resume.skills.map((k) => (
                  <span key={k} className="rounded-md bg-canvas px-2 py-0.5 text-xs">
                    {k}
                  </span>
                ))}
              </dd>
            </div>
            <div>
              <dt className="label">강점</dt>
              <dd>{s.resume.strengths}</dd>
            </div>
            <div>
              <dt className="label">업무 성향</dt>
              <dd className="flex flex-wrap gap-1.5">
                {s.personality.map((p) => (
                  <span key={p} className="rounded-full bg-brand-soft px-2.5 py-0.5 text-xs text-brand">
                    {p}
                  </span>
                ))}
              </dd>
            </div>
          </dl>
        </section>

        {/* 실행 환경 + 권한 */}
        <section className="space-y-4">
          <div className="card">
            <h2 className="font-semibold">⚙️ 실행 환경</h2>
            <dl className="mt-3 space-y-2 text-sm">
              <Row k="AI 엔진" v={s.runtime.engine} />
              <Row k="사용 도구" v={s.runtime.tools.join(", ")} />
              <Row k="근무 일정" v={s.runtime.schedule} />
            </dl>
          </div>
          <div className="card">
            <h2 className="font-semibold">🔐 권한</h2>
            <p className="mt-1 text-xs text-mute">켜진 권한만 사용할 수 있어요.</p>
            <ul className="mt-3 space-y-2">
              {allPermissions.map((p) => (
                <li key={p} className="flex items-center justify-between text-sm">
                  <span>{permission[p]}</span>
                  <Toggle on={s.permissions.includes(p)} onClick={() => togglePerm(p)} />
                </li>
              ))}
            </ul>
          </div>
        </section>
      </div>

      {/* 미션 */}
      <section className="card mt-4">
        <h2 className="font-semibold">🎯 {s.name}에게 미션 주기</h2>
        <div className="mt-3">
          <MissionForm fixedStaffId={s.id} />
        </div>
        <ul className="mt-5 divide-y divide-line">
          {missions.map((m) => (
            <li key={m.id} className="flex items-center justify-between gap-3 py-2.5 text-sm">
              <div className="min-w-0">
                <p className="truncate font-medium">{m.title}</p>
                <p className="text-xs text-mute">마감 {m.dueDate}</p>
              </div>
              <div className="flex gap-1.5">
                <Badge label={priority[m.priority]} />
                <Badge label={missionStatus[m.status]} />
              </div>
            </li>
          ))}
          {missions.length === 0 && <li className="py-6 text-center text-sm text-mute">아직 받은 미션이 없어요.</li>}
        </ul>
      </section>
    </>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between gap-3">
      <dt className="text-sub">{k}</dt>
      <dd className="text-right font-medium">{v}</dd>
    </div>
  );
}
