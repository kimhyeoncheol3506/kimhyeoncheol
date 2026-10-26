import type { BoardStage, ChannelRow, StageState } from "@/lib/services/company";
import { CHANNEL_LABEL } from "@/lib/company/channels";
import { staffLabel } from "@/lib/company/staff";
import { num } from "@/lib/format";

const STATE: Record<StageState, [string, string]> = {
  done: ["완료", "border-emerald-200 bg-emerald-50 text-emerald-900"],
  active: ["진행 중", "border-sky-200 bg-sky-50 text-sky-900"],
  waiting: ["결재 대기", "border-amber-300 bg-amber-50 text-amber-900"],
  blocked: ["막힘", "border-rose-300 bg-rose-50 text-rose-900"],
  todo: ["대기", "border-slate-200 bg-white text-slate-500"],
};

export function TeamBoard({ stages, channels, simulatedOnly }: { stages: BoardStage[]; channels: ChannelRow[]; simulatedOnly: boolean }) {
  return (
    <div className="space-y-4">
      <ol className="grid gap-2 sm:grid-cols-2 lg:grid-cols-7" aria-label="AI 팀 진행 단계">
        {stages.map((s) => {
          const [label, cls] = STATE[s.state];
          return (
            <li key={s.label} className={`rounded-lg border p-2 text-xs ${cls}`}>
              <p className="font-semibold">{s.label} <span className="font-normal opacity-80">· {label}</span></p>
              <p className="mt-0.5 opacity-80">{staffLabel(s.staff).split(" ").slice(0, 2).join(" ")}</p>
              <p className="mt-1">{s.detail}</p>
            </li>
          );
        })}
      </ol>
      {channels.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm" aria-label="매체별 결과">
            <thead>
              <tr className="text-left text-xs text-slate-500">
                {["매체", "초안", "결재 대기", "승인", "게시", "실패", "클릭", "방문", "전환"].map((h) => <th key={h} className="px-2 py-1 font-medium">{h}</th>)}
              </tr>
            </thead>
            <tbody>
              {channels.map((c) => (
                <tr key={c.platform} className="border-t border-slate-100">
                  <td className="px-2 py-1.5 font-medium">{CHANNEL_LABEL[c.platform]}</td>
                  <td className="px-2 py-1.5 tabular-nums">{c.drafts}</td>
                  <td className="px-2 py-1.5 tabular-nums">{c.pending}</td>
                  <td className="px-2 py-1.5 tabular-nums">{c.approved}</td>
                  <td className="px-2 py-1.5 tabular-nums">{c.published}</td>
                  <td className="px-2 py-1.5 tabular-nums">{c.failed}</td>
                  <td className="px-2 py-1.5 tabular-nums">{num(c.clicks)}</td>
                  <td className="px-2 py-1.5 tabular-nums">{num(c.visits)}</td>
                  <td className="px-2 py-1.5 tabular-nums">{num(c.conversions)}{c.measured && <span className="ml-1 text-[10px] text-emerald-700">실측</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {simulatedOnly && <p className="mt-1 text-[11px] text-slate-400">클릭·방문·전환은 모의 실행·데모 수치입니다 (실측 연결 전).</p>}
        </div>
      )}
    </div>
  );
}
