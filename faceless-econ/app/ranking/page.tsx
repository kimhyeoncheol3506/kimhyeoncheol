import Link from "next/link";
import { Card, PageTitle } from "@/components/ui";
import { VideoTable } from "@/components/VideoTable";
import { getDataset } from "@/lib/dataset";
import { FORMAT_LABELS } from "@/lib/format";
import { METRIC_LABELS, MILESTONES, VIRAL_METRICS, rankScores, type MilestoneKey } from "@/lib/scoring/viral";
import type { VideoFormat } from "@/lib/types";

export const dynamic = "force-dynamic";

type Basis = "current" | MilestoneKey;

export default function RankingPage({ searchParams }: { searchParams: { format?: string; basis?: string; sort?: string; channel?: string } }) {
  const ds = getDataset();
  const format = (["long", "shorts", "other"].includes(searchParams.format ?? "") ? searchParams.format : "long") as VideoFormat;
  const basis = (["current", ...MILESTONES.map((m) => m.key)].includes(searchParams.basis ?? "") ? searchParams.basis : "current") as Basis;
  const sort = searchParams.sort === "viral" ? "viralScore" : "finalScore";
  const channel = searchParams.channel ?? "";

  let rows = ds.scores.filter((s) => s.format === format && (!channel || s.channelId === channel));
  if (basis === "current") rows = rankScores(rows, sort);
  else
    rows = [...rows].sort((a, b) => {
      const av = a.milestones[basis];
      const bv = b.milestones[basis];
      if (av == null && bv == null) return 0;
      if (av == null) return 1;
      if (bv == null) return -1;
      return bv - av;
    });

  const q = (p: Record<string, string>) => {
    const s = new URLSearchParams({ format, basis, sort: sort === "viralScore" ? "viral" : "final", ...(channel ? { channel } : {}), ...p });
    return `/ranking?${s}`;
  };
  const counts = { long: 0, shorts: 0, other: 0 } as Record<VideoFormat, number>;
  for (const s of ds.scores) counts[s.format]++;
  const w = ds.settings.weights;
  const withMilestone = basis !== "current" ? rows.filter((r) => r.milestones[basis] != null).length : 0;

  return (
    <>
      <PageTitle title="바이럴 랭킹" desc={`최근 ${ds.settings.periodDays}일 게시 영상만 대상으로 합니다. 롱폼과 쇼츠는 따로 정규화·순위화합니다.`} />

      <div className="mb-4 flex flex-wrap items-center gap-2">
        {(["long", "shorts", "other"] as VideoFormat[]).map((f) => (
          <Link key={f} href={q({ format: f })} className={`rounded-lg px-3 py-1.5 text-sm font-medium ${f === format ? "bg-neutral-900 text-white" : "bg-white ring-1 ring-neutral-200"}`}>
            {FORMAT_LABELS[f]} ({counts[f]})
          </Link>
        ))}
        <span className="mx-2 h-5 w-px bg-neutral-300" />
        <Link href={q({ basis: "current" })} className={`rounded-lg px-3 py-1.5 text-sm ${basis === "current" ? "bg-neutral-900 text-white" : "bg-white ring-1 ring-neutral-200"}`}>현재 관측 점수</Link>
        {MILESTONES.map((m) => (
          <Link key={m.key} href={q({ basis: m.key })} className={`rounded-lg px-3 py-1.5 text-sm ${basis === m.key ? "bg-neutral-900 text-white" : "bg-white ring-1 ring-neutral-200"}`}>
            게시 후 {m.label}
          </Link>
        ))}
        {basis === "current" && (
          <>
            <span className="mx-2 h-5 w-px bg-neutral-300" />
            <Link href={q({ sort: "final" })} className={`rounded-lg px-3 py-1.5 text-sm ${sort === "finalScore" ? "bg-neutral-900 text-white" : "bg-white ring-1 ring-neutral-200"}`}>최종 우선순위순</Link>
            <Link href={q({ sort: "viral" })} className={`rounded-lg px-3 py-1.5 text-sm ${sort === "viralScore" ? "bg-neutral-900 text-white" : "bg-white ring-1 ring-neutral-200"}`}>바이럴 성과순</Link>
          </>
        )}
        <form action="/ranking" className="ml-auto flex items-center gap-2 text-sm">
          <input type="hidden" name="format" value={format} />
          <input type="hidden" name="basis" value={basis} />
          <select name="channel" defaultValue={channel} className="rounded-lg border border-neutral-300 bg-white px-2 py-1.5">
            <option value="">전체 채널</option>
            {ds.channels.map((c) => <option key={c.id} value={c.id}>{c.title}</option>)}
          </select>
          <button className="rounded-lg bg-white px-3 py-1.5 ring-1 ring-neutral-200">적용</button>
        </form>
      </div>

      {basis !== "current" && (
        <div className="mb-4 rounded-lg border border-sky-200 bg-sky-50 p-3 text-sm text-sky-900">
          게시 후 {MILESTONES.find((m) => m.key === basis)!.label} 시점(±20%)에 실제로 수집된 스냅샷이 있는 영상만 그 시점 조회수로 정렬합니다 ({withMilestone}/{rows.length}개).
          스냅샷이 없는 영상의 과거 조회수는 역산하지 않고 &lsquo;스냅샷 없음&rsquo;으로 표시합니다.
        </div>
      )}

      <Card>
        <VideoTable ds={ds} scores={rows} milestone={basis === "current" ? undefined : basis} />
      </Card>

      <Card title="점수 계산 방식" className="mt-6">
        <div className="grid gap-4 text-sm md:grid-cols-2">
          <div>
            <div className="font-semibold">바이럴 성과 점수 (0~100)</div>
            <ul className="mt-1 list-disc pl-5 text-neutral-700">
              {VIRAL_METRICS.map((m) => <li key={m}>{METRIC_LABELS[m]}: 가중치 {w[m]}</li>)}
            </ul>
            <p className="mt-2 text-neutral-600">각 지표를 같은 형식 그룹 안에서 백분위(0~100)로 정규화하고 가중 평균합니다. 결측 지표는 0점이 아니라 제외하며, 남은 지표의 가중치를 재조정합니다. 관측 가능한 가중치가 50% 미만이거나 그룹 영상이 3개 미만이면 판정 보류합니다.</p>
          </div>
          <div>
            <div className="font-semibold">페이스리스 제작 적합성 점수 / 최종 벤치마킹 우선순위</div>
            <p className="mt-1 text-neutral-700">적합성: A 100 · C 95 · B 85 · E 50 · D 0 · U 확인 불가(결측). 바이럴과는 별개의 개념입니다.</p>
            <p className="mt-1 text-neutral-700">최종 = (바이럴 가중치 합 {VIRAL_METRICS.reduce((a, m) => a + w[m], 0)} × 바이럴 + 페이스리스 가중치 {w.faceless} × 적합성) ÷ 전체 가중치. 적합성 확인 불가면 바이럴 점수만 사용합니다.</p>
            <p className="mt-1 text-neutral-600">각 영상의 실제 사용 가중치와 원본 값은 영상 정밀 분석 화면과 CSV 내보내기에서 확인할 수 있습니다.</p>
          </div>
        </div>
      </Card>
    </>
  );
}
