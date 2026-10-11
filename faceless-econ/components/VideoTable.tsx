import Link from "next/link";
import type { Dataset } from "@/lib/dataset";
import { compact, FORMAT_LABELS, pct } from "@/lib/format";
import type { MilestoneKey, VideoScore } from "@/lib/scoring/viral";
import { fmtAge, fmtDuration, kst } from "@/lib/time";
import { Badge, ClassBadge, NA, ScoreBar } from "./ui";

export function VideoTable({
  ds,
  scores,
  showChannel = true,
  milestone,
}: {
  ds: Dataset;
  scores: VideoScore[];
  showChannel?: boolean;
  milestone?: MilestoneKey;
}) {
  if (!scores.length) return <p className="text-sm text-neutral-500">표시할 영상이 없습니다.</p>;
  let rank = 0;
  return (
    <div className="overflow-x-auto">
      <table className="tbl">
        <thead>
          <tr>
            <th>#</th>
            <th>영상</th>
            <th className="num">게시(KST)</th>
            <th className="num">경과</th>
            <th className="num">길이</th>
            <th className="num">조회수</th>
            {milestone && <th className="num">기준 시점 조회수</th>}
            <th className="num" title="관측 조회수 ÷ 게시 후 경과 시간">시간당 조회수</th>
            <th className="num" title="조회수 ÷ 채널 구독자">구독자 대비</th>
            <th className="num" title="같은 채널·형식, 비슷한 경과 시간 영상의 시간당 조회수 중앙값 대비">채널 내 상대</th>
            <th className="num">좋아요율</th>
            <th className="num">댓글률</th>
            <th>페이스리스</th>
            <th>바이럴 성과</th>
            <th>최종 우선순위</th>
          </tr>
        </thead>
        <tbody>
          {scores.map((s) => {
            const v = ds.videoMap.get(s.videoId)!;
            const r = s.finalScore != null ? ++rank : null;
            const mv = milestone ? s.milestones[milestone] : null;
            return (
              <tr key={s.videoId}>
                <td className="tabular-nums">{r ?? "-"}</td>
                <td className="min-w-[260px]">
                  <Link href={`/videos/${v.id}`} className="font-medium hover:underline">{v.title}</Link>
                  <div className="mt-0.5 flex flex-wrap items-center gap-1 text-xs text-neutral-500">
                    {showChannel && <span>{ds.channelMap.get(v.channelId)?.title} ·</span>}
                    <span>{FORMAT_LABELS[v.format]}</span>
                    {v.url !== "#demo" && (
                      <a href={v.url} target="_blank" rel="noreferrer" className="underline">원본</a>
                    )}
                    {s.holdReason && <Badge tone="gray" title={s.holdReason}>보류: {s.holdReason}</Badge>}
                    {s.warnings.filter((w) => w.includes("변동성")).map((w) => <Badge key={w} tone="amber">{w}</Badge>)}
                  </div>
                </td>
                <td className="num text-xs">{kst(v.publishedAt).replace(" KST", "")}</td>
                <td className="num">{fmtAge(s.ageHours)}</td>
                <td className="num">{fmtDuration(v.durationSec)}</td>
                <td className="num">{compact(v.viewCount)}</td>
                {milestone && <td className="num">{mv == null ? <NA>스냅샷 없음</NA> : compact(mv)}</td>}
                <td className="num">{s.metrics.velocity.raw == null ? <NA /> : compact(s.metrics.velocity.raw)}</td>
                <td className="num">{s.metrics.subRatio.raw == null ? <NA>{s.metrics.subRatio.note ?? "-"}</NA> : `${s.metrics.subRatio.raw.toFixed(3)}배`}</td>
                <td className="num">{s.metrics.relative.raw == null ? <NA>관측 부족</NA> : `${s.metrics.relative.raw.toFixed(2)}배`}</td>
                <td className="num">{s.metrics.likeRate.raw == null ? <NA>비공개</NA> : pct(s.metrics.likeRate.raw)}</td>
                <td className="num">{s.metrics.commentRate.raw == null ? <NA>비활성</NA> : pct(s.metrics.commentRate.raw)}</td>
                <td><ClassBadge cls={v.faceless.cls} /></td>
                <td><ScoreBar value={s.viralScore} /></td>
                <td><ScoreBar value={s.finalScore} /></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
