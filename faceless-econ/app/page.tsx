import Link from "next/link";
import { Badge, Card, ClassBadge, PageTitle, ScoreBar, Stat } from "@/components/ui";
import { HBar } from "@/components/charts";
import { getDataset, rankedRecent } from "@/lib/dataset";
import { compact, FORMAT_LABELS } from "@/lib/format";
import { fmtAge, kst } from "@/lib/time";

export const dynamic = "force-dynamic";

export default function SummaryPage() {
  const ds = getDataset();
  const longTop = rankedRecent(ds, "long").slice(0, 5);
  const shortsTop = rankedRecent(ds, "shorts").slice(0, 5);
  const m = ds.missing;
  const lastRun = ds.runs[0];

  return (
    <>
      <PageTitle title="요약 대시보드" desc="최근 게시 영상의 상대 성과와 페이스리스 제작 적합성을 따로 계산한 뒤, 마지막에만 결합해 벤치마킹 우선순위를 냅니다." />

      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        <Stat label="수집 채널 수" value={ds.channels.length} sub={`페이스리스 적합 ${ds.channelViews.filter((c) => c.eligible).length}개`} />
        <Stat label={`최근 ${ds.settings.periodDays}일 영상 수`} value={ds.recent.length} sub={`롱폼 ${ds.recent.filter((v) => v.format === "long").length} · 쇼츠 ${ds.recent.filter((v) => v.format === "shorts").length}`} />
        <Stat label="점수 계산 완료" value={ds.scores.length - m.viralHold} sub={`판정 보류 ${m.viralHold}개`} />
        <Stat label="스냅샷 수" value={compact(ds.snapshots.length)} sub="조회수 관측 기록" />
        <Stat label="데이터 수집 시각" value={<span className="text-base">{kst(ds.lastCollectedAt)}</span>} sub={ds.source === "demo" ? "데모 생성 시각" : lastRun ? `상태: ${lastRun.status}` : "수집 기록 없음"} />
        <Stat label="API 연결" value={<span className="text-base">{ds.apiKeyConfigured ? "키 설정됨" : "키 없음"}</span>} sub={<Link className="underline" href="/settings">설정으로 이동</Link>} />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <Card title="바이럴 상위 영상 — 롱폼" right={<Link href="/ranking?format=long" className="text-sm underline">전체 순위</Link>}>
          <TopList ds={ds} rows={longTop} />
        </Card>
        <Card title="바이럴 상위 영상 — 쇼츠" right={<Link href="/ranking?format=shorts" className="text-sm underline">전체 순위</Link>}>
          <TopList ds={ds} rows={shortsTop} />
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <Card title="상위 3개 채널" className="xl:col-span-2" right={<Link href="/compare" className="text-sm underline">비교 분석</Link>}>
          <div className="grid gap-3 md:grid-cols-3">
            {ds.pinnedTop3.map((id, i) => {
              const cv = ds.channelViews.find((c) => c.channel.id === id);
              if (!cv) return null;
              return (
                <Link key={id} href={`/channels/${id}`} className="rounded-lg border border-neutral-200 p-3 hover:border-neutral-400">
                  <div className="text-xs text-neutral-500">고정 분석 대상 {i + 1}</div>
                  <div className="mt-1 font-bold">{cv.channel.title}</div>
                  <div className="mt-2"><ClassBadge cls={cv.channel.faceless.cls} confidence={cv.channel.faceless.confidence} /></div>
                  <div className="mt-2 text-sm">최근 영상 {cv.recent.length}개</div>
                  <div className="mt-1 text-sm">채널 바이럴(중앙값) <ScoreBar value={cv.score.medianViral} /></div>
                </Link>
              );
            })}
            {ds.pinnedTop3.length < 3 && (
              <Link href="/settings#top3" className="flex items-center justify-center rounded-lg border border-dashed border-neutral-300 p-3 text-center text-sm text-neutral-500">
                3번째 채널(경제·기업사 애니메이션) 미확정
                <br />→ 설정에서 지정
              </Link>
            )}
          </div>
          <p className="mt-3 text-xs text-neutral-500">
            고정 대상은 사용자가 선정한 채널입니다. 데이터 기준 자동 상위 3개(페이스리스 적합 채널 중 최종 우선순위 중앙값):{" "}
            {ds.autoTop3.length ? ds.autoTop3.map((id) => ds.channelMap.get(id)?.title).join(", ") : "판정 보류 (데이터 부족)"}
          </p>
          {ds.channelViews.some((c) => c.score.medianViral != null) && (
            <div className="mt-4">
              <div className="mb-1 text-sm font-semibold">채널별 바이럴 점수 중앙값</div>
              <HBar
                data={ds.channelViews
                  .filter((c) => c.score.medianViral != null)
                  .sort((a, b) => b.score.medianViral! - a.score.medianViral!)
                  .map((c) => ({ name: c.channel.title, value: c.score.medianViral! }))}
              />
            </div>
          )}
        </Card>

        <Card title="수집 실패 및 결측 데이터 현황">
          <ul className="space-y-2 text-sm">
            <Row label="좋아요 비공개(최근 영상)" v={m.likesHidden} total={m.videosTotal} />
            <Row label="댓글 비활성(최근 영상)" v={m.commentsHidden} total={m.videosTotal} />
            <Row label="구독자 비공개 채널" v={m.subscribersHidden} total={ds.channels.length} />
            <Row label="게시 시각 확인 불가" v={m.publishedUnknown} />
            <Row label="삭제·비공개 전환 영상" v={m.unavailable} />
            <Row label="채널 내 상대 성과 미계산" v={m.relativeMissing} total={ds.scores.length} hint="같은 경과 시간 스냅샷 부족" />
            <Row label="바이럴 판정 보류" v={m.viralHold} total={ds.scores.length} />
            <Row label="페이스리스 미확정(추정·확인 필요)" v={m.facelessUnverified} total={m.videosTotal} />
            <Row label="실패한 수집 실행" v={m.failedRuns} />
          </ul>
          <p className="mt-3 text-xs text-neutral-500">결측 항목은 0점으로 처리하지 않고 해당 지표만 제외한 뒤 가중치를 재조정합니다.</p>
        </Card>
      </div>
    </>
  );
}

function Row({ label, v, total, hint }: { label: string; v: number; total?: number; hint?: string }) {
  return (
    <li className="flex items-center justify-between gap-2">
      <span>
        {label}
        {hint && <span className="ml-1 text-xs text-neutral-400">({hint})</span>}
      </span>
      <span className="tabular-nums font-semibold">
        {v}
        {total != null && <span className="font-normal text-neutral-400"> / {total}</span>}
      </span>
    </li>
  );
}

function TopList({ ds, rows }: { ds: ReturnType<typeof getDataset>; rows: ReturnType<typeof rankedRecent> }) {
  if (!rows.length) return <p className="text-sm text-neutral-500">해당 형식의 최근 영상이 없습니다.</p>;
  return (
    <table className="tbl">
      <thead>
        <tr>
          <th>#</th>
          <th>영상</th>
          <th className="num">경과</th>
          <th>최종 우선순위</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((s, i) => {
          const v = ds.videoMap.get(s.videoId)!;
          return (
            <tr key={s.videoId}>
              <td className="tabular-nums">{s.finalScore == null ? "-" : i + 1}</td>
              <td>
                <Link href={`/videos/${v.id}`} className="font-medium hover:underline">{v.title}</Link>
                <div className="mt-0.5 flex flex-wrap gap-1 text-xs text-neutral-500">
                  {ds.channelMap.get(v.channelId)?.title} · {FORMAT_LABELS[v.format]}
                  {s.warnings.some((w) => w.includes("변동성")) && <Badge tone="amber">변동성 주의</Badge>}
                </div>
              </td>
              <td className="num">{fmtAge(s.ageHours)}</td>
              <td><ScoreBar value={s.finalScore} /></td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
