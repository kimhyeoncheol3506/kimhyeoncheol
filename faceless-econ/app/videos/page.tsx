import Link from "next/link";
import { Card, PageTitle, ScoreBar, Thumb } from "@/components/ui";
import { getDataset } from "@/lib/dataset";
import { FORMAT_LABELS, compact } from "@/lib/format";
import { rankScores } from "@/lib/scoring/viral";

export const dynamic = "force-dynamic";

export default function VideosIndex() {
  const ds = getDataset();
  return (
    <>
      <PageTitle title="영상 정밀 분석" desc="상위 3개 채널별로 성과가 가장 높은 영상 3개를 우선 분석합니다. 영상이 3개 미만이면 있는 영상만 표시합니다." />
      <div className="space-y-6">
        {ds.pinnedTop3.map((cid) => {
          const ch = ds.channelMap.get(cid);
          if (!ch) return null;
          const ranked = rankScores(ds.scores.filter((s) => s.channelId === cid && s.format === "long"));
          const top = ranked.filter((s) => s.finalScore != null).slice(0, 3);
          const low = ranked.filter((s) => s.finalScore != null).slice(-1);
          return (
            <Card key={cid} title={ch.title} right={<Link href={`/channels/${cid}`} className="text-sm underline">전체 영상 목록</Link>}>
              {top.length === 0 ? (
                <p className="text-sm text-neutral-500">점수가 계산된 최근 롱폼 영상이 없습니다 (판정 보류).</p>
              ) : (
                <div className="grid gap-4 md:grid-cols-4">
                  {[...top, ...(ranked.length >= 6 ? low : [])].map((s, i) => {
                    const v = ds.videoMap.get(s.videoId)!;
                    const isLow = i >= top.length;
                    return (
                      <Link key={v.id} href={`/videos/${v.id}`} className={`rounded-lg border p-2 hover:border-neutral-400 ${isLow ? "border-dashed" : ""}`}>
                        <Thumb url={v.thumbnailUrl} alt={v.title} label={isLow ? "비교용 하위 영상" : `상위 ${i + 1}`} />
                        <div className="mt-2 text-xs text-neutral-500">{isLow ? "비교용: 성과 하위" : `성과 상위 ${i + 1}`} · {FORMAT_LABELS[v.format]} · {compact(v.viewCount)}회</div>
                        <div className="mt-1 line-clamp-2 text-sm font-medium">{v.title}</div>
                        <div className="mt-1"><ScoreBar value={s.finalScore} /></div>
                      </Link>
                    );
                  })}
                </div>
              )}
            </Card>
          );
        })}
      </div>
    </>
  );
}
