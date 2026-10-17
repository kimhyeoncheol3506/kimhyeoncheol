"use client";
import { useState } from "react";
import { useStore } from "@/lib/store";
import { PageHeader } from "@/components/PageHeader";
import { Badge } from "@/components/Badge";
import { CopyForClaude } from "@/components/CopyForClaude";
import { errorStatus, severity } from "@/lib/labels";
import { newId, nowStamp } from "@/lib/format";
import type { ErrorStatus, Severity } from "@/lib/types";

// 오류 보고 및 피드백 센터
// - 화면 오류는 자동으로 들어옵니다 (components/ErrorCatcher.tsx)
// - 직접 발견한 문제나 개선 요청은 아래 폼으로 남깁니다
export default function ErrorCenter() {
  const { data, add, update, remove } = useStore();
  const [filter, setFilter] = useState<ErrorStatus | "all">("all");
  const [openId, setOpenId] = useState<string | null>(null);

  const list = data.errors.filter((e) => filter === "all" || e.status === filter);

  return (
    <>
      <PageHeader
        title="오류 · 피드백 센터"
        desc="문제가 생기면 여기 쌓입니다. '클로드 코드용 복사'를 눌러 클로드 코드에 붙여넣으면 수정을 요청할 수 있어요."
        actions={
          <button
            className="btn"
            onClick={() => {
              // 자동 감지가 잘 되는지 확인하는 테스트용 버튼
              setTimeout(() => {
                throw new Error("테스트 오류입니다 (오류 센터 동작 확인용)");
              }, 0);
            }}
          >
            🧪 테스트 오류 발생
          </button>
        }
      />

      <ReportForm
        staff={data.staff}
        onSubmit={(r) =>
          add("errors", {
            id: newId("e"),
            source: "manual",
            status: "open",
            createdAt: nowStamp(),
            feedback: "",
            ...r,
          })
        }
      />

      <div className="mb-3 mt-6 flex flex-wrap gap-1">
        {(["all", "open", "in_progress", "resolved"] as const).map((k) => (
          <button
            key={k}
            onClick={() => setFilter(k)}
            className={`rounded-full px-3 py-1 text-xs font-medium ${filter === k ? "bg-brand text-white" : "bg-white text-sub ring-1 ring-line"}`}
          >
            {k === "all" ? "전체" : errorStatus[k].text} {k === "all" ? data.errors.length : data.errors.filter((e) => e.status === k).length}
          </button>
        ))}
      </div>

      <ul className="space-y-2">
        {list.map((e) => {
          const open = openId === e.id;
          const who = data.staff.find((s) => s.id === e.staffId);
          return (
            <li key={e.id} className="card p-4">
              <button className="flex w-full flex-wrap items-center gap-2 text-left" onClick={() => setOpenId(open ? null : e.id)}>
                <Badge label={errorStatus[e.status]} />
                <Badge label={severity[e.severity]} />
                <span className="flex-1 font-medium">{e.title}</span>
                <span className="text-xs text-mute">
                  {e.source === "auto" ? "🤖 자동" : "✋ 직접"} · {e.createdAt}
                </span>
                <span className="text-mute">{open ? "▲" : "▼"}</span>
              </button>

              {open && (
                <div className="mt-4 space-y-3 border-t border-line pt-4 text-sm">
                  <p>
                    <span className="label inline">페이지</span> {e.page || "-"}
                    {who && (
                      <>
                        {" "}
                        · <span className="label inline">관련 직원</span> {who.avatar} {who.name}
                      </>
                    )}
                  </p>
                  <p className="whitespace-pre-wrap rounded-lg bg-canvas p-3">{e.message}</p>
                  {e.stack && <pre className="max-h-48 overflow-auto rounded-lg bg-gray-900 p-3 text-xs text-gray-100">{e.stack}</pre>}
                  <div>
                    <label className="label">CEO 메모 / 처리 내용</label>
                    <textarea
                      className="input min-h-[64px]"
                      value={e.feedback}
                      onChange={(ev) => update("errors", e.id, { feedback: ev.target.value })}
                      placeholder="어떻게 고쳐졌으면 좋겠는지, 처리 결과 등을 적어 두세요."
                    />
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <select
                      className="input w-auto"
                      value={e.status}
                      onChange={(ev) => update("errors", e.id, { status: ev.target.value as ErrorStatus })}
                    >
                      {(Object.keys(errorStatus) as ErrorStatus[]).map((k) => (
                        <option key={k} value={k}>
                          {errorStatus[k].text}
                        </option>
                      ))}
                    </select>
                    <CopyForClaude error={e} />
                    <button className="btn ml-auto" onClick={() => confirm("이 기록을 삭제할까요?") && remove("errors", e.id)}>
                      🗑 삭제
                    </button>
                  </div>
                </div>
              )}
            </li>
          );
        })}
        {list.length === 0 && <li className="card py-10 text-center text-sm text-mute">🎉 해당하는 기록이 없어요.</li>}
      </ul>
    </>
  );
}

function ReportForm({
  staff,
  onSubmit,
}: {
  staff: { id: string; name: string; avatar: string }[];
  onSubmit: (r: { title: string; message: string; severity: Severity; page: string; staffId?: string }) => void;
}) {
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [sev, setSev] = useState<Severity>("medium");
  const [page, setPage] = useState("");
  const [staffId, setStaffId] = useState("");

  return (
    <form
      className="card grid gap-3 sm:grid-cols-6"
      onSubmit={(e) => {
        e.preventDefault();
        if (!title.trim()) return;
        onSubmit({ title: title.trim(), message: message.trim(), severity: sev, page, staffId: staffId || undefined });
        setTitle("");
        setMessage("");
      }}
    >
      <h2 className="font-semibold sm:col-span-6">✋ 문제 · 개선 요청 직접 보고</h2>
      <div className="sm:col-span-4">
        <label className="label">무엇이 문제인가요?</label>
        <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="예: 주문 화면에서 금액이 0원으로 보여요" />
      </div>
      <div className="sm:col-span-2">
        <label className="label">심각도</label>
        <select className="input" value={sev} onChange={(e) => setSev(e.target.value as Severity)}>
          <option value="low">낮음 (불편함)</option>
          <option value="medium">보통 (일부 기능 안 됨)</option>
          <option value="high">심각 (업무 중단)</option>
        </select>
      </div>
      <div className="sm:col-span-6">
        <label className="label">자세히 (어떤 순서로 눌렀더니 어떻게 됐는지)</label>
        <textarea className="input min-h-[72px]" value={message} onChange={(e) => setMessage(e.target.value)} />
      </div>
      <div className="sm:col-span-2">
        <label className="label">어느 화면? (선택)</label>
        <input className="input" value={page} onChange={(e) => setPage(e.target.value)} placeholder="/orders" />
      </div>
      <div className="sm:col-span-2">
        <label className="label">관련 AI 직원 (선택)</label>
        <select className="input" value={staffId} onChange={(e) => setStaffId(e.target.value)}>
          <option value="">없음</option>
          {staff.map((s) => (
            <option key={s.id} value={s.id}>
              {s.avatar} {s.name}
            </option>
          ))}
        </select>
      </div>
      <div className="flex items-end sm:col-span-2">
        <button className="btn-primary w-full" disabled={!title.trim()}>
          보고하기
        </button>
      </div>
    </form>
  );
}
