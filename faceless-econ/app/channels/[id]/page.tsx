import Link from "next/link";
import { notFound } from "next/navigation";
import { Badge, Card, ClassBadge, PageTitle, ScoreBar, SourceBadge, Stat } from "@/components/ui";
import { VideoTable } from "@/components/VideoTable";
import { channelProfile } from "@/lib/analysis/patterns";
import { candidateById } from "@/lib/candidates";
import { getDataset } from "@/lib/dataset";
import { compact, num, pct } from "@/lib/format";
import { rankScores } from "@/lib/scoring/viral";
import { kst } from "@/lib/time";

export const dynamic = "force-dynamic";

export default function ChannelDetail({ params }: { params: { id: string } }) {
  const ds = getDataset();
  const id = decodeURIComponent(params.id);
  const cv = ds.channelViews.find((c) => c.channel.id === id);
  if (!cv) notFound();
  const ch = cv.channel;
  const cand = candidateById(id);
  const scores = ds.scores.filter((s) => s.channelId === id);
  const prof = channelProfile(id, ds.recent, ds.scoreMap, ds.settings.periodDays);
  const past = ds.pastHits.filter((v) => v.channelId === id).slice(0, 5);

  return (
    <>
      <PageTitle title={ch.title} desc={ch.description?.slice(0, 160) ?? undefined}>
        <div className="flex items-center gap-2">
          <SourceBadge source={ch.source} />
          {ch.url !== "#demo" && (
            <a href={ch.url} target="_blank" rel="noreferrer" className="rounded-lg border px-3 py-1.5 text-sm hover:bg-neutral-50">유튜브 채널 열기</a>
          )}
        </div>
      </PageTitle>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-6">
        <Stat label="구독자" value={ch.subscriberCount == null ? "비공개" : compact(ch.subscriberCount)} sub={ch.subscriberHidden ? "구독자 대비 지표 제외" : undefined} />
        <Stat label="누적 조회수" value={compact(ch.viewCount)} />
        <Stat label="공개 영상 수" value={num(ch.videoCount)} />
        <Stat label={`최근 ${ds.settings.periodDays}일 영상`} value={cv.recent.length} sub={`롱폼 ${prof.longCount} · 쇼츠 ${prof.shortsCount}`} />
        <Stat label="채널 바이럴(중앙값)" value={<ScoreBar value={cv.score.medianViral} />} sub={cv.score.holdReason ?? undefined} />
        <Stat label="수집 시각" value={<span className="text-sm">{kst(ch.collectedAt)}</span>} />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <Card title="페이스리스 판정">
          <ClassBadge cls={ch.faceless.cls} confidence={ch.faceless.confidence} />
          <div className="mt-2 text-sm">최근 영상 페이스리스(A/B/C) 비중: <strong>{pct(cv.facelessRatio, 0)}</strong></div>
          <div className="mt-1 text-sm">벤치마킹 대상: {cv.eligible ? <Badge tone="green">포함</Badge> : <Badge tone="red">제외</Badge>}</div>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-xs text-neutral-600">
            {ch.faceless.evidence.map((e, i) => <li key={i}>{e}</li>)}
          </ul>
          {cand && <p className="mt-2 text-xs text-neutral-500">선정 사유: {cand.decisionReason}</p>}
          <p className="mt-2 text-xs text-neutral-500">영상 화면을 직접 확인한 뒤 <Link href="/settings#faceless" className="underline">설정</Link>에서 확정할 수 있습니다.</p>
        </Card>
        <Card title="채널 프로필 (관측)">
          <ul className="space-y-1 text-sm">
            <li>주당 업로드(최근 기간): {prof.uploadsPerWeek.toFixed(1)}개</li>
            <li>롱폼 길이 중앙값: {prof.medianDurationMin?.toFixed(1) ?? "-"}분</li>
            <li>제목 길이 중앙값: {prof.medianTitleLen ?? "-"}자</li>
            <li>숫자 포함 제목: {pct(prof.numberTitleShare, 0)} · 질문형: {pct(prof.questionShare, 0)}</li>
            <li>자주 쓴 제목 키워드: {prof.topKeywords.join(", ") || "-"}</li>
          </ul>
        </Card>
        <Card title="성과 상위 3 vs 하위 3 (롱폼)">
          {prof.topVsBottom.length ? (
            <table className="tbl">
              <thead><tr><th>항목</th><th className="num">상위</th><th className="num">하위</th></tr></thead>
              <tbody>
                {prof.topVsBottom.map((r) => (
                  <tr key={r.metric}><td>{r.metric}</td><td className="num">{r.top}</td><td className="num">{r.bottom}</td></tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-sm text-neutral-500">점수가 계산된 롱폼이 6개 미만이라 비교하지 않습니다.</p>
          )}
          <p className="mt-2 text-xs text-neutral-500">차이는 상관관계이며 원인을 뜻하지 않습니다.</p>
        </Card>
      </div>

      <Card title={`최근 ${ds.settings.periodDays}일 영상 전체 목록 (${scores.length}개)`} className="mt-6">
        <VideoTable ds={ds} scores={rankScores(scores)} showChannel={false} />
      </Card>

      <Card title="과거 히트 영상 (참고용 — 순위 계산에서 제외)" className="mt-6">
        {past.length ? (
          <ul className="space-y-1 text-sm">
            {past.map((v) => (
              <li key={v.id}>
                <Link href={`/videos/${v.id}`} className="hover:underline">{v.title}</Link>{" "}
                <span className="text-neutral-500">· {compact(v.viewCount)}회 · {kst(v.publishedAt)}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-neutral-500">분석 기간 이전 영상이 수집되지 않았습니다.</p>
        )}
      </Card>
    </>
  );
}
