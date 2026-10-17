import type { AnalysisResult, ScoreKey } from "@/lib/analysis/engine";
import { SCORE_LABEL } from "@/lib/analysis/engine";
import { ScoreBar } from "@/components/ui/status";
import { Badge } from "@/components/ui/badge";

const ORDER: ScoreKey[] = ["topicFit", "targetFit", "brandFit", "contentRelevance", "trafficPotential", "policyRisk"];

export function AnalysisView({ result }: { result: AnalysisResult }) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2 text-sm">
        <span className="text-slate-500">분류</span>
        <span className="font-semibold text-slate-900">{result.category}</span>
        <span className="text-slate-400">›</span>
        <span className="font-semibold text-slate-900">{result.subcategory}</span>
        <Badge tone={result.dataSufficiency === "SUFFICIENT" ? "green" : result.dataSufficiency === "LIMITED" ? "amber" : "red"}>
          데이터 {result.dataSufficiency === "SUFFICIENT" ? "충분" : result.dataSufficiency === "LIMITED" ? "제한적" : "부족"}
        </Badge>
        <Badge tone="gray">엔진: {result.engine}</Badge>
      </div>
      {result.notes.length > 0 && (
        <ul className="space-y-1">
          {result.notes.map((n) => (
            <li key={n} className="rounded bg-sky-50 px-2 py-1 text-xs text-sky-800">ℹ {n}</li>
          ))}
        </ul>
      )}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[640px] text-sm">
          <thead>
            <tr className="border-b border-slate-200">
              <th className="th">지표</th>
              <th className="th">점수</th>
              <th className="th">구분</th>
              <th className="th">산출 기준 · 근거</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {ORDER.map((k) => {
              const s = result.scores[k];
              return (
                <tr key={k}>
                  <td className="td whitespace-nowrap font-medium">
                    {SCORE_LABEL[k]}
                    {k === "policyRisk" && <span className="block text-xs font-normal text-slate-400">높을수록 위험</span>}
                  </td>
                  <td className="td"><ScoreBar value={s.value} invert={k === "policyRisk"} /></td>
                  <td className="td">
                    <Badge tone={s.kind === "ESTIMATE" ? "amber" : "gray"}>{s.kind === "ESTIMATE" ? "추정치" : "분석 불가"}</Badge>
                  </td>
                  <td className="td text-xs">
                    <p className="text-slate-500">{s.criteria}</p>
                    <ul className="mt-1 list-inside list-disc text-slate-700">
                      {s.evidence.map((e) => (
                        <li key={e}>{e}</li>
                      ))}
                    </ul>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-slate-400">
        모든 점수는 입력된 의뢰 텍스트와 브랜드 프로필만으로 계산한 규칙 기반 추정치이며, 실제 성과 예측값이 아닙니다.
      </p>
    </div>
  );
}
