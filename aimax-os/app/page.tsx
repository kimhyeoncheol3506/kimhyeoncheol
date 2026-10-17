"use client";
import Link from "next/link";
import { useStore } from "@/lib/store";
import { PageHeader } from "@/components/PageHeader";
import { StatCard } from "@/components/StatCard";
import { Badge } from "@/components/Badge";
import { errorStatus, missionStatus, orderStatus, staffStatus } from "@/lib/labels";
import { won, wonShort } from "@/lib/format";
import type { StaffStatus } from "@/lib/types";

// 운영자 콘솔: 회사 전체 상황을 한 화면에서 봅니다.
export default function Dashboard() {
  const { data, resetAll } = useStore();
  const { staff, missions, errors, orders, buyers } = data;

  const activeMissions = missions.filter((m) => m.status !== "done");
  const reviewMissions = missions.filter((m) => m.status === "review");
  const openErrors = errors.filter((e) => e.status !== "resolved");
  const sales = orders.filter((o) => o.status !== "refunded").reduce((sum, o) => sum + o.amount, 0);
  const staffName = (id: string) => staff.find((s) => s.id === id)?.name ?? "-";
  const buyerName = (id: string) => buyers.find((b) => b.id === id)?.company ?? "-";

  const statusCount = (Object.keys(staffStatus) as StaffStatus[]).map((k) => ({
    key: k,
    count: staff.filter((s) => s.status === k).length,
  }));

  return (
    <>
      <PageHeader
        title="운영자 콘솔"
        desc="AI 직원, 미션, 오류, 주문 현황을 한눈에 봅니다."
        actions={
          <button
            className="btn"
            onClick={() => confirm("모든 데이터를 처음 예시 상태로 되돌릴까요?") && resetAll()}
          >
            ↺ 예시 데이터로 초기화
          </button>
        }
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="AI 직원" value={`${staff.length}명`} hint={`사용 가능 ${statusCount[0].count}명`} href="/staff" />
        <StatCard label="진행 중 미션" value={activeMissions.length} hint={`검수 대기 ${reviewMissions.length}건`} href="/missions" />
        <StatCard label="미처리 오류" value={openErrors.length} hint="오류 · 피드백 센터" href="/errors" alert={openErrors.length > 0} />
        <StatCard label="누적 매출 (환불 제외)" value={wonShort(sales)} hint={`주문 ${orders.length}건`} href="/orders" />
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <section className="card lg:col-span-1">
          <h2 className="font-semibold">직원 상태</h2>
          <ul className="mt-3 space-y-2">
            {statusCount.map(({ key, count }) => (
              <li key={key} className="flex items-center justify-between text-sm">
                <Badge label={staffStatus[key]} />
                <span className="font-semibold">{count}명</span>
              </li>
            ))}
          </ul>
          <div className="mt-4 flex flex-wrap gap-1.5">
            {staff.map((s) => (
              <Link
                key={s.id}
                href={`/staff/${s.id}`}
                title={`${s.name} · ${staffStatus[s.status].text}`}
                className="flex items-center gap-1 rounded-full bg-canvas px-2 py-1 text-xs hover:bg-brand-soft"
              >
                {s.avatar} {s.name}
              </Link>
            ))}
          </div>
        </section>

        <section className="card lg:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold">진행 중 미션</h2>
            <Link href="/missions" className="text-xs text-brand">
              전체 보기 →
            </Link>
          </div>
          <ul className="mt-3 divide-y divide-line">
            {activeMissions.slice(0, 5).map((m) => (
              <li key={m.id} className="flex items-center justify-between gap-3 py-2.5 text-sm">
                <div className="min-w-0">
                  <p className="truncate font-medium">{m.title}</p>
                  <p className="text-xs text-mute">
                    {staffName(m.staffId)} · 마감 {m.dueDate}
                  </p>
                </div>
                <Badge label={missionStatus[m.status]} />
              </li>
            ))}
            {activeMissions.length === 0 && <li className="py-6 text-center text-sm text-mute">진행 중인 미션이 없어요.</li>}
          </ul>
        </section>

        <section className="card lg:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold">최근 주문</h2>
            <Link href="/orders" className="text-xs text-brand">
              전체 보기 →
            </Link>
          </div>
          <ul className="mt-3 divide-y divide-line">
            {orders.slice(0, 5).map((o) => (
              <li key={o.id} className="flex items-center justify-between gap-3 py-2.5 text-sm">
                <div className="min-w-0">
                  <p className="truncate font-medium">{o.product}</p>
                  <p className="text-xs text-mute">
                    {buyerName(o.buyerId)} · {o.orderedAt.slice(0, 10)} · {o.channel === "cafe24" ? "카페24" : "직접"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold">{won(o.amount)}</span>
                  <Badge label={orderStatus[o.status]} />
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="card">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold">미처리 오류</h2>
            <Link href="/errors" className="text-xs text-brand">
              전체 보기 →
            </Link>
          </div>
          <ul className="mt-3 space-y-2">
            {openErrors.slice(0, 4).map((e) => (
              <li key={e.id} className="rounded-lg bg-canvas p-2.5 text-sm">
                <div className="flex items-center justify-between gap-2">
                  <p className="truncate font-medium">{e.title}</p>
                  <Badge label={errorStatus[e.status]} />
                </div>
                <p className="mt-0.5 text-xs text-mute">{e.createdAt}</p>
              </li>
            ))}
            {openErrors.length === 0 && <li className="py-6 text-center text-sm text-mute">🎉 처리할 오류가 없어요.</li>}
          </ul>
        </section>
      </div>
    </>
  );
}
