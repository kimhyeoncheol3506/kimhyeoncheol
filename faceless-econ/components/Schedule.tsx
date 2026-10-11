"use client";

import { useEffect, useMemo, useState } from "react";
import { PRIORITY_LABELS, TASKS } from "@/lib/planner/schedule";

const KEY = "faceless-econ:schedule:v1";

interface State {
  start: string; // YYYY-MM-DD
  done: Record<string, boolean>;
}

function todayStr() {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Seoul" }).format(new Date());
}

function addDays(d: string, n: number) {
  const t = new Date(`${d}T00:00:00+09:00`);
  t.setDate(t.getDate() + n);
  return new Intl.DateTimeFormat("ko-KR", { timeZone: "Asia/Seoul", month: "numeric", day: "numeric", weekday: "short" }).format(t);
}

export function Schedule() {
  const [st, setSt] = useState<State>({ start: todayStr(), done: {} });
  const [loaded, setLoaded] = useState(false);
  useEffect(() => {
    try {
      const raw = localStorage.getItem(KEY);
      if (raw) setSt(JSON.parse(raw));
    } catch {
      /* 저장소 사용 불가 시 기본값 */
    }
    setLoaded(true);
  }, []);
  useEffect(() => {
    if (!loaded) return;
    try {
      localStorage.setItem(KEY, JSON.stringify(st));
    } catch {
      /* 무시 */
    }
  }, [st, loaded]);

  const today = useMemo(() => {
    const diff = Math.floor((Date.parse(`${todayStr()}T00:00:00+09:00`) - Date.parse(`${st.start}T00:00:00+09:00`)) / 86_400_000);
    return diff + 1;
  }, [st.start]);

  const overdue = TASKS.filter((t) => !st.done[t.id] && t.dayEnd < today);
  const overdueHours = overdue.reduce((a, t) => a + t.hours, 0);
  const remainingMust = TASKS.filter((t) => !st.done[t.id] && t.priority === "must" && t.dayEnd <= 21).reduce((a, t) => a + t.hours, 0);
  const daysToPublish = Math.max(0, 22 - today);
  const dropCould = overdue.length > 0;
  const dropShould = overdueHours > 6 || (daysToPublish > 0 && remainingMust / daysToPublish > 3);
  const totalHours = TASKS.reduce((a, t) => a + t.hours, 0);
  const doneHours = TASKS.filter((t) => st.done[t.id]).reduce((a, t) => a + t.hours, 0);

  return (
    <div>
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <label>
          시작일{" "}
          <input type="date" value={st.start} onChange={(e) => setSt({ ...st, start: e.target.value })} className="rounded-md border border-neutral-300 px-2 py-1" />
        </label>
        <span>오늘은 <strong>{today}일차</strong> · 게시 목표 22일차 ({addDays(st.start, 21)})</span>
        <span className="text-neutral-500">진행률 {((doneHours / totalHours) * 100).toFixed(0)}% ({doneHours}/{totalHours}시간)</span>
      </div>

      {(dropCould || dropShould) && (
        <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
          <strong>지연 감지:</strong> 기한이 지난 작업 {overdue.length}개(약 {overdueHours}시간).{" "}
          {dropShould
            ? "게시일을 지키기 위해 '선택'과 '권장' 작업을 뒤로 미루고 '필수' 작업만 진행하세요. (모션 효과는 컷 전환으로, 지인 검수는 본인 재검수로 대체)"
            : "'선택' 작업(쇼츠 그래픽·쇼츠 게시)을 게시 이후로 미루세요."}
        </div>
      )}

      <div className="mt-3 overflow-x-auto">
        <table className="tbl">
          <thead>
            <tr>
              <th>완료</th>
              <th>일차</th>
              <th>단계</th>
              <th>작업</th>
              <th>완료 조건</th>
              <th className="num">예상 시간</th>
              <th>우선순위</th>
            </tr>
          </thead>
          <tbody>
            {TASKS.map((t) => {
              const late = !st.done[t.id] && t.dayEnd < today;
              const deferred = !st.done[t.id] && ((dropCould && t.priority === "could") || (dropShould && t.priority === "should"));
              return (
                <tr key={t.id} className={st.done[t.id] ? "opacity-50" : ""}>
                  <td>
                    <input type="checkbox" checked={!!st.done[t.id]} onChange={(e) => setSt({ ...st, done: { ...st.done, [t.id]: e.target.checked } })} />
                  </td>
                  <td className="whitespace-nowrap tabular-nums">
                    {t.dayStart === t.dayEnd ? `${t.dayStart}일` : `${t.dayStart}~${t.dayEnd}일`}
                    <div className="text-xs text-neutral-400">{addDays(st.start, t.dayStart - 1)}</div>
                  </td>
                  <td className="text-xs text-neutral-500">{t.phase}</td>
                  <td className="font-medium">
                    {t.title}
                    {late && <span className="ml-1 rounded bg-rose-50 px-1 text-xs text-rose-700">지연</span>}
                    {deferred && <span className="ml-1 rounded bg-neutral-100 px-1 text-xs text-neutral-600">미루기 권장</span>}
                  </td>
                  <td className="text-xs text-neutral-600">{t.done}</td>
                  <td className="num">{t.hours}시간</td>
                  <td>{PRIORITY_LABELS[t.priority]}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-xs text-neutral-500">진행 상태는 이 브라우저에만 저장됩니다.</p>
    </div>
  );
}
